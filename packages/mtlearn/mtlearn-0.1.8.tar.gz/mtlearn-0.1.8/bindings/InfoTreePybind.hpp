#pragma once


#include <mmcfilters/attributes/AttributeComputedIncrementally.hpp>
#include <mmcfilters/trees/NodeMT.hpp>
#include <mmcfilters/trees/MorphologicalTree.hpp>
#include <mmcfilters/utils/Common.hpp>

#include "MorphologicalTreePybind.hpp"
#include "PybindTorchUtils.hpp"

#include <memory>
#include <vector>
#include <tuple>

#include <pybind11/pybind11.h>
#include <torch/extension.h>
#include <ATen/ops/_sparse_mm.h>



namespace mtlearn {

namespace py = pybind11;

using mmcfilters::AttributeComputedIncrementally;
using mmcfilters::InvalidNode;
using mmcfilters::MorphologicalTreePybindPtr;
using mmcfilters::NodeId;

class InfoTreePybind {
public:

    
    static torch::Tensor getResidues(MorphologicalTreePybindPtr tree) {
        if (!tree) {
            throw py::value_error("MorphologicalTreePybindPtr inválido");
        }

        int numNodes = tree->getNumNodes();
        float* residues = new float[numNodes];

        for (NodeId nodeId : tree->getNodeIds()) {
            residues[nodeId] = static_cast<float>(tree->getResidueById(nodeId));
        }

        return PybindTorchUtils::toTensor(residues, numNodes);
    }


    

    static torch::Tensor getJacobianDense(MorphologicalTreePybindPtr tree) {
        if (!tree) {
            throw py::value_error("MorphologicalTreePybindPtr inválido");
        }

        int numNodes = tree->getNumNodes();
        int imageSize = tree->getNumRowsOfImage() * tree->getNumColsOfImage();

        auto options = torch::TensorOptions().dtype(torch::kFloat32);
        torch::Tensor denseTensor = torch::zeros({numNodes, imageSize}, options);
        float* data = denseTensor.data_ptr<float>();

        for (auto nodeId : tree->getNodeIds()) {
            mmcfilters::NodeMT node = tree->proxy(nodeId);
            auto pixelsOfCC = node.getPixelsOfCC();

            for (auto pixel : pixelsOfCC) {
                data[nodeId * imageSize + pixel] = 1.0f;
            }
        }

        return denseTensor;
    }



    static torch::Tensor getJacobian(MorphologicalTreePybindPtr tree){
        if (!tree) {
            throw py::value_error("MorphologicalTreePybindPtr inválido");
        }

        std::vector<int64_t> rowIndices;
        std::vector<int64_t> colIndices;
        auto imageSize = tree->getNumRowsOfImage() * tree->getNumColsOfImage();

        for(auto nodeId : tree->getNodeIds()){
            mmcfilters::NodeMT node = tree->proxy(nodeId);
            auto pixelsOfCC = node.getPixelsOfCC();

            for(auto pixel : pixelsOfCC){
                rowIndices.push_back(nodeId);
                colIndices.push_back(pixel);
            }
        }

        return PybindTorchUtils::toSparseCooTensor(
            rowIndices,
            colIndices,
            tree->getNumNodes(),
            imageSize
        );
    }


    static std::list<torch::Tensor> getInfoForJacobian(MorphologicalTreePybindPtr tree) {
        if (!tree) {
            throw py::value_error("MorphologicalTreePybindPtr inválido");
        }
        if (tree->getNumNodes() == 0) {
            throw std::runtime_error("MorphologicalTreePybind está vazio.");
        }

        int numNodes = tree->getNumNodes();
        int numPixels = tree->getNumRowsOfImage() * tree->getNumColsOfImage();

        // --- Tensores ---
        auto opts_i64 = torch::TensorOptions().dtype(torch::kInt64).requires_grad(false);
        auto opts_f32 = torch::TensorOptions().dtype(torch::kFloat32).requires_grad(false);

        torch::Tensor tResiduos = torch::zeros({numNodes}, opts_f32);
        torch::Tensor tPreOrder  = torch::zeros({numNodes}, opts_i64);
        torch::Tensor tPostOrder = torch::zeros({numNodes}, opts_i64);
        torch::Tensor tParent    = torch::zeros({numNodes}, opts_i64);
        torch::Tensor tNodeOfPixel = torch::zeros({numPixels}, opts_i64);
        
        float* residues_ptr = tResiduos.data_ptr<float>();
        int64_t* preOrder_ptr = tPreOrder.data_ptr<int64_t>();
        int64_t* postOrder_ptr = tPostOrder.data_ptr<int64_t>();
        int64_t* parent_ptr = tParent.data_ptr<int64_t>();
        int64_t* nodeOfPixel_ptr = tNodeOfPixel.data_ptr<int64_t>();
        
        #pragma omp parallel for
        for (NodeId nodeId : tree->getNodeIds()) {
            residues_ptr[nodeId]   = static_cast<float>(tree->getResidueById(nodeId));
            preOrder_ptr[nodeId]   = static_cast<int64_t>(tree->getTimePreOrderById(nodeId));
            postOrder_ptr[nodeId]  = static_cast<int64_t>(tree->getTimePostOrderById(nodeId));
            parent_ptr[nodeId]     = static_cast<int64_t>(tree->getParentById(nodeId));
        }

        for (int p = 0; p < numPixels; ++p){
            nodeOfPixel_ptr[p] = static_cast<int64_t>(tree->getSCById(p));
        }

        // Ordem dos tensores no retorno:
        // [residues, preOrder, postOrder, parent, nodeOfPixel]
        std::list<torch::Tensor> result;
        result.push_back(tResiduos);
        result.push_back(tPreOrder);
        result.push_back(tPostOrder);
        result.push_back(tParent);
        result.push_back(tNodeOfPixel);
        
        return result;
    }


    //Somente para teste
    static torch::Tensor getAcumulatedGradient(MorphologicalTreePybindPtr treePtr, torch::Tensor gradientOfLoss) {
        MorphologicalTreePybind* tree = treePtr.get();
        const int64_t numNodes = tree->getNumNodes();
        float* gradLoss = gradientOfLoss.data_ptr<float>();
        auto opts_f32 = torch::TensorOptions().dtype(torch::kFloat32).requires_grad(false);
        torch::Tensor summationGrad = torch::zeros({numNodes}, opts_f32);
        AttributeComputedIncrementally::computerAttribute(
            tree,
            tree->getRootById(),
            [&](NodeId nodeId) -> void { // pre-processing
                summationGrad[nodeId] = 0;
                for (int p : tree->getCNPsById(nodeId)) {
                    summationGrad[nodeId] += gradLoss[p];
                }
            },
            [&](NodeId parent, NodeId child) -> void { // merge-processing
                summationGrad[parent] += summationGrad[child];
            },
            [&](NodeId nodeId) -> void { } // post-processing
        );
        return summationGrad;
    }
    

};

} // namespace mtlearn
