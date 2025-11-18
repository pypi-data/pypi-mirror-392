# Versão estável: utiliza Jacobiana implícita (não materializada) para o backward dos filtros conectados,
# sem materializar matriz Jacobiana, com cache de ordem e máscara para propagação eficiente.

import math
import torch
import numpy as np
import mmcfilters
import mtlearn
from ._helpers import (
    group_name,
    to_numpy_u8,
    build_tree,
    update_ds_stats,
    normalize_with_ds_stats,
    maybe_refresh_norm_for_key,
    IndexedDatasetWrapper
)




class ConnectedFilterImplicitFunction(torch.autograd.Function):
    """
    Forward implícito otimizado (sem materializar a Jacobiana).
    Realiza a acumulação ao longo da hierarquia na ordem de pós-ordem (tpost crescente).
    Equivale a y = J.T @ residues, mas com custo O(N + P).
    A propagação é feita dos filhos para os pais na ordem de pós-ordem crescente.
    Nenhuma máscara é necessária porque parent[root] = root garante que não há acúmulo redundante.
    
    enter_n = tpre.view(-1, 1)
    exit_n  = tpost.view(-1, 1)
    enter_p = tpre[node_of_pixel].view(1, -1)
    J = (enter_n <= enter_p) & (enter_p < exit_n)
    return J.float().T @ filtered_res
    """
    @staticmethod
    def forward_from_info(filtered_res, tpre, tpost, node_of_pixel, parent, order_forward=None):
        """
        Forward implícito totalmente vetorizado usando prefix-scan em tpre/tpost.
        Equivalente a y = J.T @ filtered_res, mas sem materializar J.
            #Forma materalizada (ineficiente):
            enter_n = tpre.view(-1, 1)
            exit_n  = tpost.view(-1, 1)
            enter_p = tpre[node_of_pixel].view(1, -1)
            J = (enter_n <= enter_p) & (enter_p < exit_n)
            return J.float().T @ filtered_res
        """
        
        max_t = int(tpost.max().item()) + 1
        delta = torch.zeros(max_t, device=filtered_res.device, dtype=filtered_res.dtype)
        delta.index_add_(0, tpre, filtered_res)
        delta.index_add_(0, tpost, -filtered_res)
        y_cumsum = torch.cumsum(delta, dim=0)
        y = y_cumsum[tpre[node_of_pixel]]
        return y

    def backward_from_info(grad_output, tpre, tpost, parent, node_of_pixel, order_pre=None):
        g_pix = grad_output.reshape(-1)
        N = tpre.numel()
        base = torch.zeros(N, dtype=g_pix.dtype, device=g_pix.device)
        base.index_add_(0, node_of_pixel.reshape(-1), g_pix)

        # pré-ordem (perm e rank)
        if( order_pre is None):
            order_pre = torch.argsort(tpre)                  
        pre_rank = torch.empty_like(order_pre)
        pre_rank[order_pre] = torch.arange(N, device=order_pre.device)

        base_sorted = base[order_pre]
        pref = torch.cumsum(base_sorted, dim=0)
        pref0 = torch.cat([pref.new_zeros(1), pref], dim=0)

        # time->rank: R[t] = # de nós com tpre < t
        T = int(torch.max(tpost).item()) + 1
        counts = torch.bincount(tpre, minlength=T)           # quantos nós têm cada tpre
        cum = torch.cumsum(counts, dim=0)                    # inclusivo
        R = torch.cat([cum.new_zeros(1), cum[:-1]], dim=0)   # exclusivo

        l = pre_rank
        r = R[tpost]                                         # fim exclusivo
        grad_nodes = pref0[r] - pref0[l]
        return grad_nodes   
                 
    @staticmethod
    def backward_from_info_OLD(grad_output, tpre, tpost, parent, node_of_pixel, order_pre=None):
        """
        Versão 100% vetorizada de J @ grad_output:
        1) condensa grad_output dos pixels no nó-CNP (base)
        2) soma por subárvore via prefix-sum em pré-ordem usando (tpre, tpost) e searchsorted
        Requer: tpre/tpost de uma DFS real (timer++ em entrada/saída, como no C++).
        """
        # 1) pixels -> nó CNP
        g_pix = grad_output.view(-1)
        N = tpre.numel()
        base = torch.zeros(N, device=g_pix.device)
        base.index_add_(0, node_of_pixel.view(-1), g_pix)

        # 2) ordenar nós por pré-ordem e prefix-sum
        if( order_pre is None):
            order_pre = torch.argsort(tpre)                  # (N,)
        pre_rank  = torch.empty_like(order_pre)
        pre_rank[order_pre] = torch.arange(N, device=order_pre.device)
        base_sorted = base[order_pre]                    # (N,)
        pref = torch.cumsum(base_sorted, dim=0)          # (N,)
        pref0 = torch.cat([pref.new_zeros(1), pref])     # (N+1,)

        # 3) converter tpost -> índice de fim do bloco da subárvore via lower_bound
        sorted_tpre = tpre[order_pre]                    # (N,)
        # out_idx[n] = #{nodes m | tpre[m] < tpost[n]} na ordem de pré-ordem
        out_idx = torch.searchsorted(sorted_tpre, tpost, right=False)  # (N,)

        l = pre_rank                                     # início
        r = out_idx                                      # fim exclusivo
        grad_nodes = pref0[r] - pref0[l]                 # soma em [l, r)

        return grad_nodes 
            
            
    
    @staticmethod
    def forward(ctx, weight, bias, residues, tpre, tpost, parent, node_of_pixel, attrs2d, numRows: int, numCols: int, beta_f: float = 1.0, clamp_logits: bool = False, order_forward=None, order_backward=None):
        """
        Forward do filtro conectado com Jacobiana implícita.
        Args:
            weight, bias: parâmetros da camada
            residues: resíduos da árvore
            tpre: ordem de entrada (pré-ordem) dos nós
            tpost: ordem de saída (pós-ordem) dos nós
            parent: vetor de pais dos nós
            node_of_pixel: mapeamento de pixel para nó
            attrs2d: atributos normalizados (numNodes, K)
            numRows, numCols: dimensões da imagem
            beta_f: ganho da sigmoide
            clamp_logits: aplica clamp em beta_f·logits
            order_forward: cache para forward (pós-ordem crescente)
            order_backward: cache para backward (pós-ordem decrescente)
        Returns:
            y_2d: saída filtrada (numRows, numCols)
        """
        # --- Critério sigmoid ---
        logits = attrs2d @ weight.view(-1) + bias
        s = beta_f * logits
        if clamp_logits:
            s = torch.clamp(s, -12.0, 12.0)
        sigmoid = torch.sigmoid(s)

        # --- Aplicação implícita da reconstrução ---
        filtered_res = residues * sigmoid
        y = ConnectedFilterImplicitFunction.forward_from_info(filtered_res, tpre, tpost, node_of_pixel, parent, order_forward)
        y_2d = y.reshape(numRows, numCols)

        # --- Contexto para backward ---
        ctx.save_for_backward(attrs2d, residues, sigmoid, tpre, tpost, parent, node_of_pixel)
        ctx.beta_f = beta_f
        ctx.order_backward = order_backward
        return y_2d

    @staticmethod
    def backward(ctx, grad_output):
        """
        Backward do filtro conectado com Jacobiana implícita.
        Recebe grad_output (gradiente da saída).
        Retorna gradientes para cada argumento do forward.
        A propagação do gradiente é feita na ordem reversa da forward: pós-ordem decrescente (pais para filhos),
        utilizando order_backward.
        """
        # Recupera apenas os tensores utilizados na Jacobiana implícita
        attrs2d, residues, sigmoid, tpre, tpost, parent, node_of_pixel = ctx.saved_tensors
        #beta_f = ctx.beta_f
        order_backward = ctx.order_backward
        grad_output_flat = grad_output.flatten()

        # --- backward implícito pela árvore (J @ grad_output) ---
        grad_nodes = ConnectedFilterImplicitFunction.backward_from_info(
            grad_output_flat, tpre, tpost, parent, node_of_pixel, order_backward
        )

        # --- derivada da sigmoide ---
        d_sigmoid = sigmoid * (1 - sigmoid)
        grad_s = grad_nodes * residues * d_sigmoid

        # --- gradientes finais ---
        dW = attrs2d.T @ grad_s
        dB = grad_s.sum().view(1)

        # Retornar exatamente 13 elementos (incluindo novos argumentos)
        return (
            dW,          # weight
            dB,          # bias
            None,        # residues
            None,        # tpre
            None,        # tpost
            None,        # parent
            None,        # node_of_pixel
            None,        # attrs2d
            None,        # numRows
            None,        # numCols
            None,        # beta_f
            None,        # clamp_logits
            None,        # order_forward
            None         # order_backward
        )




class ConnectedFilterLayerWithImplicitJacobian(torch.nn.Module):
    """
    Camada geral por grupo: σ( A_norm @ w + b ) com filtering conectado e Jacobiana implícita.

    • Para cada grupo g com K atributos normalizados A_g ∈ R^{numNodes×K},
      aplica-se logits = A_g @ w_g + b_g e s = σ(β_f · logits).
    • O filtering conectado é aplicado sobre s.
    • O backward de (w_g, b_g) é realizado via Jacobiana implícita, sem materialização da matriz Jacobiana.

    Args:
        in_channels (int): canais de entrada
        attributes_spec (Iterable[Iterable[Type]]): lista de grupos (K≥1 atributos)
        tree_type (str): "max-tree" | "min-tree" | outro (ToS)
        device (str): dispositivo para tensores de saída e parâmetros
        scale_mode (str): "minmax01" | "zscore_tree" | "hybrid" | "none"
        eps (float): proteção numérica
        initial_weight (float): valor inicial para pesos (default 0.0)
        initial_bias (float): valor inicial para bias (default 0.0)
        beta_f (float): ganho da sigmoide no FORWARD (default 1000.0)
        top_hat (bool): aplica top-hat ao final (como nas outras camadas)
        clamp_logits (bool): se True, clamp de β_f·logits em ±12 antes da sigmoide
        hybrid_k (float): clipping em ±kσ para o modo híbrido
        hybrid_floor_a (float): remapeamento para [a,1] no modo híbrido
    """
    def __init__(self,
                 in_channels,
                 attributes_spec,
                 tree_type="max-tree",
                 device="cpu",
                 scale_mode: str = "hybrid",
                 eps: float = 1e-6,
                 beta_f: float = 1.0,
                 top_hat: bool = False,
                 clamp_logits: bool = False,
                 hybrid_k: float = 3.0,
                 hybrid_floor_a: float = 0.05,
                 ):
        super().__init__()
    
        # --- parâmetros do modo híbrido ---
        self.hybrid_k = float(hybrid_k)
        self.hybrid_floor_a = float(hybrid_floor_a)

        self.in_channels = int(in_channels)
        self.tree_type   = str(tree_type)
        self.device      = torch.device(device)
        self.scale_mode  = str(scale_mode)
        self.eps         = float(eps)
        self.beta_f      = float(beta_f)
        self.top_hat     = bool(top_hat)
        self.clamp_logits = bool(clamp_logits)


        # Definição de grupos (K≥1) e conjunto de atributos usados
        self.group_defs = []
        all_attr_types_set = set()
        for item in attributes_spec:
            group = tuple(item) if isinstance(item, (list, tuple)) else (item,)
            if len(group) < 1:
                raise ValueError("Cada grupo deve conter pelo menos 1 atributo.")
            self.group_defs.append(group)
            for at in group:
                all_attr_types_set.add(at)
        self._all_attr_types = list(all_attr_types_set)

        self.num_groups   = len(self.group_defs)
        self.out_channels = self.in_channels * self.num_groups

        # Caches/normalização
        self._trees      = {}
        self._base_attrs = {}
        self._norm_attrs = {}
        self._stats_epoch = 0
        self._norm_epoch_by_key = {}
        self._ds_stats = {}
        self._stats_frozen = False
        self._info_jacobian = {}

        # Parâmetros: para cada grupo g, (w_g, b_g)
        self._weights = torch.nn.ParameterDict()
        self._biases  = torch.nn.ParameterDict()
        for g, group in enumerate(self.group_defs):
            k = len(group)
            gname = "+".join([t.name for t in group])
            w = torch.empty(k, dtype=torch.float32, device=self.device)
            b = torch.empty(1, dtype=torch.float32, device=self.device)
            # Xavier-like init para vetor 1D
            fan_in, fan_out = k, 1
            gain = 1.0
            std = gain * math.sqrt(2.0 / float(fan_in + fan_out))
            a = math.sqrt(3.0) * std
            torch.nn.init.uniform_(w, -a, a)
            torch.nn.init.constant_(b, 0.0)
            self._weights[gname] = torch.nn.Parameter(w, requires_grad=True)
            self._biases[gname]  = torch.nn.Parameter(b, requires_grad=True)

    # ---------- helpers ----------
    def _group_name(self, group):
        return group_name(group)

    def _to_numpy_u8(self, img2d_t: torch.Tensor) -> np.ndarray:
        return to_numpy_u8(img2d_t)

    def _compute_tree_info_for_jacobian(self, img_np: np.ndarray):
        """
        Constrói a árvore e retorna um dicionário com informações necessárias para Jacobiana implícita:
            - residues: resíduos da árvore
            - tpre: ordem de entrada (pré-ordem) dos nós
            - tpost: ordem de saída (pós-ordem) dos nós
            - parent: vetor de pais dos nós
            - node_of_pixel: mapeamento de pixel para nó
            - numRows: número de linhas da imagem
            - numCols: número de colunas da imagem
            - tree_type: tipo da árvore
            - order_forward: ordem cacheada para propagação ascendente (pós-ordem crescente)
            - order_backward: ordem cacheada para propagação descendente (pós-ordem decrescente)
        Nenhuma máscara é necessária pois parent[root] = root.
        """
        tree = build_tree(img_np, self.tree_type)
        residues, tpre, tpost, parent, node_of_pixel = mtlearn.InfoTree.get_info_for_jacobian(tree)
        info = {
            "residues": residues.to(self.device),
            "tpre": tpre.to(self.device),
            "tpost": tpost.to(self.device),
            "parent": parent.to(self.device),
            "node_of_pixel": node_of_pixel.to(self.device),
            "numRows": tree.numRows,
            "numCols": tree.numCols,
            "tree_type": self.tree_type,
        }
        # Ordem forward: pós-ordem crescente
        info["order_forward"] = torch.argsort(tpre, descending=False).to(self.device)
        # Ordem backward: pós-ordem decrescente
        info["order_backward"] = torch.argsort(tpre).to(self.device)
        return tree, info

    # ---------- normalização com suporte a 'hybrid' ----------
    def _update_ds_stats(self, attr_type, a_raw_1d: torch.Tensor):
        """
        Coleta estatísticas do dataset. Para o modo 'hybrid', usamos as mesmas
        estatísticas do 'zscore_tree' (count, sum, sumsq).
        """
        if getattr(self, "_stats_frozen", False):
            return
        smode = self.scale_mode
        if smode == "hybrid":
            smode = "zscore_tree"
        changed = update_ds_stats(self._ds_stats, smode, attr_type, a_raw_1d)
        if changed:
            self._stats_epoch += 1

    def _normalize_with_ds_stats(self, attr_type, a_raw_1d: torch.Tensor) -> torch.Tensor:
        """
        Normaliza conforme self.scale_mode. No caso 'hybrid', aplica:
          1) z-score com mean/std do dataset
          2) clipping em [-k, +k]
          3) remapeamento para [a, 1]:  a + (1-a) * ( (x+k)/(2k) )
        """
        if self.scale_mode != "hybrid":
            return normalize_with_ds_stats(self._ds_stats, self.scale_mode, self.eps, attr_type, a_raw_1d)

        # --- modo híbrido ---
        st = self._ds_stats.get(attr_type, None)
        if st is None:
            # fallback: retorna o tensor original (evita crash em primeiros passos)
            return a_raw_1d

        # estatísticas em estilo z-score
        count = st["count"].to(torch.float32)
        mean  = (st["sum"] / torch.clamp(count, min=1.0)) if count.item() > 0 else torch.tensor(0.0, device=a_raw_1d.device)
        var   = (st["sumsq"] / torch.clamp(count, min=1.0) - mean * mean) if count.item() > 0 else torch.tensor(0.0, device=a_raw_1d.device)
        std   = torch.sqrt(torch.clamp(var, min=self.eps))

        # 1) z-score
        x = (a_raw_1d - mean) / std
        # 2) clip em [-k, +k]
        k = torch.tensor(self.hybrid_k, dtype=x.dtype, device=x.device)
        x = torch.clamp(x, -k, k)
        # 3) reescala para [a, 1]
        a = torch.tensor(self.hybrid_floor_a, dtype=x.dtype, device=x.device)
        x01 = a + (1.0 - a) * ((x + k) / (2.0 * k))
        return x01

    def _maybe_refresh_norm_for_key(self, key: str):
        """
        Atualiza as normalizações em cache para a imagem/árvore identificada por `key`
        caso _stats_epoch tenha mudado. Para o modo 'hybrid', aplicamos a nossa
        própria rotina (_normalize_with_ds_stats). Para os demais modos, delegamos
        ao helper externo.
        """
        # Se não há atributos brutos cacheados, nada a fazer
        if key not in self._base_attrs:
            return

        # Já está atualizado para este epoch?
        if self._norm_epoch_by_key.get(key, -1) == self._stats_epoch:
            return

        if self.scale_mode == "hybrid":
            # Reaplica normalização híbrida atributo a atributo
            per_attr_raw = self._base_attrs[key]           # dict[attr_type] -> (numNodes,1)
            per_attr_norm = {}
            for attr_type, a_raw_2d in per_attr_raw.items():
                a_raw_1d = a_raw_2d.view(-1)              # (numNodes,)
                a_norm   = self._normalize_with_ds_stats(attr_type, a_raw_1d)
                per_attr_norm[attr_type] = a_norm
            self._norm_attrs[key] = per_attr_norm
            self._norm_epoch_by_key[key] = self._stats_epoch
        else:
            # Modos já suportados pelo helper (_helpers.normalize_with_ds_stats)
            maybe_refresh_norm_for_key(
                key,
                self._base_attrs,
                self._norm_attrs,
                self._all_attr_types,
                self._ds_stats,
                self.scale_mode,
                self.eps,
                self._norm_epoch_by_key,
                self._stats_epoch
            )
            
    def freeze_ds_stats(self):
        """Congela a atualização de `_ds_stats` (não coleta mais nem avança `_stats_epoch`)."""
        self._stats_frozen = True

    def unfreeze_ds_stats(self):
        """Descongela a atualização de `_ds_stats` e permite voltar a coletar stats."""
        self._stats_frozen = False

    def save_stats(self, path: str):
        """Salva `_ds_stats` e `scale_mode` para reprodutibilidade."""
        payload = {"ds_stats": self._ds_stats, "scale_mode": self.scale_mode}
        torch.save(payload, path)
        print(f"[ConnectedLinearUnit] stats salvas em {path}")

    def load_stats(self, path: str, refresh_cache: bool = True):
        """Carrega `_ds_stats` e, opcionalmente, re-normaliza o cache existente."""
        payload = torch.load(path, map_location=self.device)
        self._ds_stats = payload.get("ds_stats", {})
        # invalida normalizações antigas
        self._stats_epoch += 1
        if refresh_cache:
            self.refresh_cached_normalization()

    # ---------- construção de árvore e atributos ----------
    def _ensure_tree_info_and_attributes_cached(self, key: str, img_t: torch.Tensor):
        """
        Garante que a árvore e as informações necessárias para Jacobiana implícita estejam em cache para a chave fornecida.
        Constrói e armazena um dicionário com campos:
            - residues, tpre, tpost, parent, node_of_pixel, numRows, numCols, tree_type
        Também armazena atributos normalizados e brutos.
        """
        if key in self._info_jacobian:
            return

        img_np = self._to_numpy_u8(img_t.detach())
        tree, info = self._compute_tree_info_for_jacobian(img_np)
        # self._trees[key] = tree  # removido, árvore não é mais armazenada no cache
        self._info_jacobian[key] = info  # dict com campos estruturados

        per_attr_raw, per_attr_norm = {}, {}
        for attr_type in self._all_attr_types:
            attr_np  = mmcfilters.Attribute.computeAttributes(tree, [attr_type])[1]
            a_raw_1d = torch.as_tensor(attr_np, device=self.device).squeeze(1)
            self._update_ds_stats(attr_type, a_raw_1d)
            a_norm = self._normalize_with_ds_stats(attr_type, a_raw_1d)
            per_attr_raw[attr_type]  = a_raw_1d.unsqueeze(1)
            per_attr_norm[attr_type] = a_norm

        self._base_attrs[key] = per_attr_raw
        self._norm_attrs[key] = per_attr_norm
        self._norm_epoch_by_key[key] = self._stats_epoch

    # ---------- inspeção ----------
    def inspect_training_sample(self, img: torch.Tensor, channel: int = 0, idx: int | None = None, build_if_missing: bool = True):
        """
        Retorna árvore, atributos, pesos e bias de uma amostra específica.

        Se 'idx' for fornecido, usa o cache (key = f"{idx}_{c}").
        Caso contrário, computa árvore e atributos on-the-fly, sem cache.
        """
        # Normaliza formato da imagem
        if img.dim() == 2:
            imgCHW = img.unsqueeze(0)
        elif img.dim() == 3:
            imgCHW = img
        else:
            raise ValueError(f"img deve ser (H,W) ou (C,H,W); veio {tuple(img.shape)}")

        C, H, W = imgCHW.shape
        if C != self.in_channels:
            if C != 1:
                raise AssertionError(f"in_channels={self.in_channels}, input C={C}")

        c = channel if C > 1 else 0

        if idx is not None:
            key = f"{idx}_{c}"
            use_cache = True
        else:
            use_cache = False

        if use_cache:
            if (key not in self._info_jacobian) and build_if_missing:
                self._ensure_tree_info_and_attributes_cached(key, imgCHW[c])
            elif key not in self._info_jacobian:
                raise KeyError("Árvore/atributos não encontrados no cache. Use build_if_missing=True.")
            self._maybe_refresh_norm_for_key(key)
            # Como a árvore não é mais armazenada em self._trees, retornamos None.
            tree = None  # A árvore não está mais disponível no cache; utilize inspect sem cache se necessário.
            base_attrs_by_group = {}
            norm_attrs_by_group = {}
            weights_by_group    = {}
            bias_by_group       = {}
            for group in self.group_defs:
                gname = self._group_name(group)
                cols_raw  = [self._base_attrs[key][attr_type].view(-1, 1) for attr_type in group]
                cols_norm = [self._norm_attrs[key][attr_type].view(-1, 1) for attr_type in group]
                A_raw  = torch.cat(cols_raw,  dim=1)
                A_norm = torch.cat(cols_norm, dim=1)
                base_attrs_by_group[gname] = A_raw
                norm_attrs_by_group[gname] = A_norm
                weights_by_group[gname]    = self._weights[gname]
                bias_by_group[gname]       = self._biases[gname]
        else:
            print("[inspect_training_sample] Executando sem cache — computando árvore e atributos diretamente.")
            img_np = self._to_numpy_u8(imgCHW[c].detach())
            tree, info = self._compute_tree_info_for_jacobian(img_np)
            residues = info["residues"]
            base_attrs_by_group = {}
            norm_attrs_by_group = {}
            weights_by_group    = {}
            bias_by_group       = {}
            for group in self.group_defs:
                gname = self._group_name(group)
                cols_raw, cols_norm = [], []
                for attr_type in group:
                    attr_np = mmcfilters.Attribute.computeAttributes(tree, [attr_type])[1]
                    a_raw_1d = torch.as_tensor(attr_np, device=self.device).squeeze(1)
                    a_norm = self._normalize_with_ds_stats(attr_type, a_raw_1d)
                    cols_raw.append(a_raw_1d.unsqueeze(1))
                    cols_norm.append(a_norm.view(-1, 1))
                A_raw = torch.cat(cols_raw, dim=1)
                A_norm = torch.cat(cols_norm, dim=1)
                base_attrs_by_group[gname] = A_raw
                norm_attrs_by_group[gname] = A_norm
                weights_by_group[gname]    = self._weights[gname]
                bias_by_group[gname]       = self._biases[gname]

        return {
            "tree": tree,
            "base_attrs_by_group": base_attrs_by_group,
            "norm_attrs_by_group": norm_attrs_by_group,
            "weights_by_group": weights_by_group,
            "bias_by_group": bias_by_group,
        }

    # ---------- forward ----------
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Aplica σ( A_norm @ w + b ) por grupo, seguido do filtering conectado usando Jacobiana implícita.
        Utiliza caches distintos de ordem/máscara para forward (ascendente) e backward (descendente).
        """
        # Lógica de entrada igual ao ConnectedFilterLayer
        if isinstance(x, tuple) and len(x) == 2:
            x, idx = x
            use_cache = True
        elif isinstance(x, list) and len(x) == 2 and isinstance(x[1], torch.Tensor) and x[1].dim() == 1:
            x, idx = x[0], x[1]
            use_cache = True
        else:
            if isinstance(x, list):
                x = torch.stack(x, dim=0)
            idx = torch.arange(x.size(0), device=x.device)
            use_cache = False

        assert x.dim() == 4, f"Esperado (B,C,H,W), veio {tuple(x.shape)}"
        B, C, H, W = x.shape
        assert C == self.in_channels, f"in_channels={self.in_channels}, input C={C}"

        out = torch.empty((B, self.out_channels, H, W), dtype=torch.float32, device=self.device)

        for b in range(B):
            for c in range(C):
                if use_cache:
                    # Use idx como parte da chave para persistência de cache
                    key = f"{int(idx[b])}_{c}"
                    self._ensure_tree_info_and_attributes_cached(key, x[b, c])
                    self._maybe_refresh_norm_for_key(key)
                    info = self._info_jacobian[key]
                    for g, group in enumerate(self.group_defs):
                        gname = self._group_name(group)
                        # Monta A_norm (numNodes, K) empilhando colunas dos atributos do grupo
                        cols = [self._norm_attrs[key][attr_type].view(-1, 1) for attr_type in group]
                        A_norm = torch.cat(cols, dim=1)  # (numNodes, K)
                        y_ch = ConnectedFilterImplicitFunction.apply(
                            self._weights[gname],
                            self._biases[gname],
                            info["residues"],
                            info["tpre"],
                            info["tpost"],
                            info["parent"],
                            info["node_of_pixel"],
                            A_norm,
                            info["numRows"],
                            info["numCols"],
                            self.beta_f,
                            self.clamp_logits,
                            info["order_forward"],
                            info["order_backward"]
                        )
                        if self.top_hat:
                            x_bc = x[b, c].to(dtype=torch.float32, device=self.device)
                            tt = self.tree_type
                            if tt == "max-tree":
                                y_out = x_bc - y_ch
                            elif tt == "min-tree":
                                y_out = y_ch - x_bc
                            else:
                                y_out = torch.abs(y_ch - x_bc)
                        else:
                            y_out = y_ch
                        out[b, c * self.num_groups + g].copy_(y_out, non_blocking=True)
                else:
                    # Não usar cache, construir árvore e atributos diretamente
                    img_np = self._to_numpy_u8(x[b, c].detach())
                    tree, info = self._compute_tree_info_for_jacobian(img_np)
                    residues = info["residues"]
                    per_attr_norm = {}
                    for attr_type in self._all_attr_types:
                        attr_np = mmcfilters.Attribute.computeAttributes(tree, [attr_type])[1]
                        a_raw_1d = torch.as_tensor(attr_np, device=self.device).squeeze(1)
                        a_norm = self._normalize_with_ds_stats(attr_type, a_raw_1d)
                        per_attr_norm[attr_type] = a_norm
                    for g, group in enumerate(self.group_defs):
                        gname = self._group_name(group)
                        cols = [per_attr_norm[attr_type].view(-1, 1) for attr_type in group]
                        A_norm = torch.cat(cols, dim=1)  # (numNodes, K)
                        y_ch = ConnectedFilterImplicitFunction.apply(
                            self._weights[gname],
                            self._biases[gname],
                            info["residues"],
                            info["tpre"],
                            info["tpost"],
                            info["parent"],
                            info["node_of_pixel"],
                            A_norm,
                            info["numRows"],
                            info["numCols"],
                            self.beta_f,
                            self.clamp_logits,
                            info["order_forward"],
                            info["order_backward"]
                        )
                        if self.top_hat:
                            x_bc = x[b, c].to(dtype=torch.float32, device=self.device)
                            tt = self.tree_type
                            if tt == "max-tree":
                                y_out = x_bc - y_ch
                            elif tt == "min-tree":
                                y_out = y_ch - x_bc
                            else:
                                y_out = torch.abs(y_ch - x_bc)
                        else:
                            y_out = y_ch
                        out[b, c * self.num_groups + g].copy_(y_out, non_blocking=True)

        return out

    # ---------- predição / inferência ----------
    def predict(self, x: torch.Tensor, beta_f: float = 1000.0) -> torch.Tensor:
        """Predição com β_f fixo (forward ~hard); restaura modo train/eval ao final.
        Utiliza caches distintos de ordem/máscara para forward (ascendente) e backward (descendente).
        """
        was_training = self.training
        self.eval()
        with torch.no_grad():
            # Lógica de entrada igual ao forward
            if isinstance(x, tuple) and len(x) == 2:
                x, idx = x
                use_cache = True
            elif isinstance(x, list) and len(x) == 2 and isinstance(x[1], torch.Tensor) and x[1].dim() == 1:
                x, idx = x[0], x[1]
                use_cache = True
            else:
                if isinstance(x, list):
                    x = torch.stack(x, dim=0)
                idx = torch.arange(x.size(0), device=x.device)
                use_cache = False
            B, C, H, W = x.shape
            out = torch.empty((B, self.out_channels, H, W), dtype=torch.float32, device=self.device)
            for b in range(B):
                for c in range(C):
                    if use_cache:
                        key = f"{int(idx[b])}_{c}"
                        self._ensure_tree_info_and_attributes_cached(key, x[b, c])
                        self._maybe_refresh_norm_for_key(key)
                        info = self._info_jacobian[key]
                        for g, group in enumerate(self.group_defs):
                            gname = self._group_name(group)
                            cols = [self._norm_attrs[key][attr_type].view(-1, 1) for attr_type in group]
                            A_norm = torch.cat(cols, dim=1)  # (numNodes, K)
                        y_ch = ConnectedFilterImplicitFunction.apply(
                            self._weights[gname],
                            self._biases[gname],
                            info["residues"],
                            info["tpre"],
                            info["tpost"],
                            info["parent"],
                            info["node_of_pixel"],
                            A_norm,
                            info["numRows"],
                            info["numCols"],
                            beta_f,  # usa β_f passado
                            self.clamp_logits,
                            info["order_forward"],
                            info["order_backward"]
                        )
                        if self.top_hat:
                            x_bc = x[b, c].to(dtype=torch.float32, device=self.device)
                            tt = self.tree_type
                            if tt == "max-tree":
                                y_out = x_bc - y_ch
                            elif tt == "min-tree":
                                y_out = y_ch - x_bc
                            else:
                                y_out = torch.abs(y_ch - x_bc)
                        else:
                            y_out = y_ch
                        out[b, c * self.num_groups + g].copy_(y_out, non_blocking=True)
                    else:
                        img_np = self._to_numpy_u8(x[b, c].detach())
                        tree, info = self._compute_tree_info_for_jacobian(img_np)
                        per_attr_norm = {}
                        for attr_type in self._all_attr_types:
                            attr_np = mmcfilters.Attribute.computeAttributes(tree, [attr_type])[1]
                            a_raw_1d = torch.as_tensor(attr_np, device=self.device).squeeze(1)
                            a_norm = self._normalize_with_ds_stats(attr_type, a_raw_1d)
                            per_attr_norm[attr_type] = a_norm
                        for g, group in enumerate(self.group_defs):
                            gname = self._group_name(group)
                            cols = [per_attr_norm[attr_type].view(-1, 1) for attr_type in group]
                            A_norm = torch.cat(cols, dim=1)  # (numNodes, K)
                        y_ch = ConnectedFilterImplicitFunction.apply(
                            self._weights[gname],
                            self._biases[gname],
                            info["residues"],
                            info["tpre"],
                            info["tpost"],
                            info["parent"],
                            info["node_of_pixel"],
                            A_norm,
                            info["numRows"],
                            info["numCols"],
                            beta_f,  # usa β_f passado
                            self.clamp_logits,
                            info["order_forward"],
                            info["order_backward"]
                        )
                        if self.top_hat:
                            x_bc = x[b, c].to(dtype=torch.float32, device=self.device)
                            tt = self.tree_type
                            if tt == "max-tree":
                                y_out = x_bc - y_ch
                            elif tt == "min-tree":
                                y_out = y_ch - x_bc
                            else:
                                y_out = torch.abs(y_ch - x_bc)
                        else:
                            y_out = y_ch
                        out[b, c * self.num_groups + g].copy_(y_out, non_blocking=True)
        if was_training:
            self.train()
        else:
            self.eval()
        return out

    # ---------- salvar / carregar ----------
    def save_params(self, path: str):
        """Salva pesos e bias de todos os grupos."""
        payload = {
            "weights": { name: p.detach().cpu() for name, p in self._weights.items() },
            "biases":  { name: p.detach().cpu() for name, p in self._biases.items()  },
            "scale_mode": self.scale_mode,
        }
        torch.save(payload, path)
        print(f"[ConnectedLinearUnit] pesos e bias salvos em {path}")

    def get_params(self):
        """Retorna dicionários {weights}, {biases} (tensores clonados em CPU)."""
        return (
            { name: p.detach().cpu().clone() for name, p in self._weights.items() },
            { name: p.detach().cpu().clone() for name, p in self._biases.items()  },
        )


    # ---------- utilidades: normalização em cache ----------
    def refresh_cached_normalization(self):
        """Reaplica normalização aos atributos no cache conforme _ds_stats atual."""
        for key, per_attr_raw in self._base_attrs.items():
            per_attr_norm = {}
            for attr_type, a_raw_2d in per_attr_raw.items():
                a_raw_1d = a_raw_2d.view(-1)
                a_norm = self._normalize_with_ds_stats(attr_type, a_raw_1d)
                per_attr_norm[attr_type] = a_norm
            self._norm_attrs[key] = per_attr_norm
            self._norm_epoch_by_key[key] = self._stats_epoch

    # ---------- inicializadores (Opção A e C) ----------
    @staticmethod
    def _logit(p: float) -> float:
        p = max(min(float(p), 1.0 - 1e-6), 1e-6)
        return math.log(p / (1.0 - p))

    @torch.no_grad()
    def init_identity_with_bias(self, p0: float = 0.995):
        """
        (Opção C) Inicializa para 'identidade' com viés:
          - w_g <- 0
          - b_g <- logit(p0)/beta_f
        Mantém a imagem (p≈p0) e permite treinar saindo dessa condição.
        """
        L = self._logit(p0) / float(self.beta_f)
        for group in self.group_defs:
            gname = self._group_name(group)
            self._weights[gname].zero_()
            self._biases[gname].fill_(L)

    @torch.no_grad()
    def init_identity_bias_zero(self, p0: float = 0.99):
        """
        (Opção A) Inicializa para 'identidade' com bias=0, assumindo 'scale_mode=="hybrid"':
          - atributos normalizados ∈ [a, 1], com 'a=self.hybrid_floor_a'
          - define w_g = c * 1, com c = logit(p0)/(beta_f * K * a)
          - define b_g = 0
        Garante p>=p0 para todos os nós (limiar inferior pela soma mínima K*a*c).
        """
        if self.scale_mode != "hybrid":
            print("[init_identity_bias_zero] Aviso: esta inicialização supõe 'scale_mode==\"hybrid\"'.")
        a = max(min(self.hybrid_floor_a, 1.0), 1e-6)
        L = self._logit(p0) / float(self.beta_f)
        for group in self.group_defs:
            gname = self._group_name(group)
            K = len(group)
            c = L / (K * a)
            self._weights[gname].fill_(c)
            self._biases[gname].zero_()

    def build_dataloader_cached(self, dataloader):
        """
        Pré-processa e cacheia árvores/atributos para um DataLoader, usando o cache persistente por idx+c.
        O DataLoader retornado produz batches ((x, idx), y), onde idx é o índice do dataset original.
        """
        from torch.utils.data import DataLoader

        dataset_wrapped = IndexedDatasetWrapper(dataloader.dataset)
        new_loader = DataLoader(
            dataset_wrapped,
            batch_size=dataloader.batch_size,
            shuffle=False,
            num_workers=dataloader.num_workers,
            pin_memory=dataloader.pin_memory,
            drop_last=False,
            collate_fn=dataloader.collate_fn,
            persistent_workers=getattr(dataloader, "persistent_workers", False),
        )

        print(f"[ConnectedFilterLayerWithImplicitJacobian] Preprocessing dataset using mode '{self.scale_mode}'...")
        self._stats_frozen = False
        total_batches = len(new_loader)

        with torch.no_grad():
            for batch_i, ((x, idx), y) in enumerate(new_loader):
                B, C, H, W = x.shape
                for b in range(B):
                    for c in range(C):
                        key = f"{int(idx[b])}_{c}"
                        self._ensure_tree_info_and_attributes_cached(key, x[b, c])
                if (batch_i + 1) % 10 == 0 or batch_i == total_batches - 1:
                    print(f"  [{batch_i+1}/{total_batches}] batches processed.")

        self.freeze_ds_stats()
        self.refresh_cached_normalization()
        print(f"[ConnectedFilterLayerWithImplicitJacobian] Full and normalized cache with '{self.scale_mode}'.")
        return new_loader
    

# Exporta símbolos públicos do módulo:
__all__ = [
    'ConnectedFilterImplicitFunction',
    'ConnectedFilterLayerWithImplicitJacobian'
]


