"""
PyTorch Adapter
Captures neural signals from PyTorch models
"""

import torch
import torch.nn as nn
import numpy as np
import time
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class PyTorchAdapter:
    """
    PyTorch-specific signal capture adapter
    Automatically hooks into BERT and other transformer models
    """
    
    def __init__(self, exporter, config: Dict[str, Any]):
        self.exporter = exporter
        self.config = config
        self.hooks = []
        
    def attach_monitoring(self, model):
        """Attach monitoring hooks to PyTorch model"""
        
        # Detect model type
        model_type = self._detect_model_type(model)
        logger.info(f"Detected model type: {model_type}")
        
        # Attach appropriate hooks based on model type
        if 'bert' in model_type.lower():
            self._attach_bert_hooks(model)
        elif 'gpt' in model_type.lower():
            self._attach_gpt_hooks(model)
        else:
            self._attach_generic_hooks(model)
        
        logger.info(f"Attached {len(self.hooks)} monitoring hooks")
        
        return model
    
    def _detect_model_type(self, model) -> str:
        """Detect specific model architecture"""
        model_name = model.__class__.__name__.lower()
        
        if hasattr(model, 'config'):
            model_type = getattr(model.config, 'model_type', model_name)
            return model_type
        
        return model_name
    
    def _attach_bert_hooks(self, model):
        """Attach BERT-specific monitoring hooks"""
        logger.info("Attaching BERT-specific hooks")
        
        # Hook 1: Capture hidden states from each encoder layer
        if hasattr(model, 'bert') and hasattr(model.bert, 'encoder'):
            for layer_idx, layer in enumerate(model.bert.encoder.layer):
                hook = layer.register_forward_hook(
                    self._create_layer_hook(layer_idx, 'bert_encoder')
                )
                self.hooks.append(hook)
        
        # Hook 2: Capture attention patterns
        if hasattr(model, 'bert') and hasattr(model.bert, 'encoder'):
            for layer_idx, layer in enumerate(model.bert.encoder.layer):
                attention = layer.attention.self
                hook = attention.register_forward_hook(
                    self._create_attention_hook(layer_idx)
                )
                self.hooks.append(hook)
        
        # Hook 3: Capture pre-classification embeddings (KEY SIGNAL!)
        for name, module in model.named_modules():
            if 'classifier' in name.lower() or 'head' in name.lower():
                hook = module.register_forward_hook(
                    self._create_classification_hook(name)
                )
                self.hooks.append(hook)
                logger.info(f"Hooked classification layer: {name}")
    
    def _attach_gpt_hooks(self, model):
        """Attach GPT-specific monitoring hooks"""
        logger.info("Attaching GPT-specific hooks")
        
        # Hook transformer blocks
        if hasattr(model, 'transformer') and hasattr(model.transformer, 'h'):
            for layer_idx, layer in enumerate(model.transformer.h):
                hook = layer.register_forward_hook(
                    self._create_layer_hook(layer_idx, 'gpt_block')
                )
                self.hooks.append(hook)
    
    def _attach_generic_hooks(self, model):
        """Attach generic hooks for unknown models"""
        logger.info("Attaching generic hooks")
        
        # Hook all Linear and LayerNorm layers
        for name, module in model.named_modules():
            if isinstance(module, (nn.Linear, nn.LayerNorm)):
                hook = module.register_forward_hook(
                    self._create_generic_hook(name)
                )
                self.hooks.append(hook)
    
    def _create_layer_hook(self, layer_idx: int, layer_type: str):
        """Create hook for capturing layer outputs"""
        def hook(module, input, output):
            try:
                # Extract hidden states
                if isinstance(output, tuple):
                    hidden_state = output[0]
                else:
                    hidden_state = output
                
                # Signal #1 & #2: Token states and CLS embedding
                signals = {
                    'framework': 'pytorch',
                    'signal_type': 'hidden_states',
                    'layer_type': layer_type,
                    'layer_index': layer_idx,
                    'timestamp': time.time(),
                    
                    # CLS token embedding (for BERT)
                    'cls_embedding': self._extract_cls_embedding(hidden_state),
                    
                    # Layer statistics
                    'statistics': self._compute_tensor_statistics(hidden_state),
                    
                    # Neural health metrics
                    'neural_health': self._compute_neural_health(hidden_state)
                }
                
                # Export asynchronously
                self.exporter.export(signals)
                
            except Exception as e:
                logger.error(f"Error in layer hook: {e}")
        
        return hook
    
    def _create_attention_hook(self, layer_idx: int):
        """Create hook for capturing attention patterns"""
        def hook(module, input, output):
            try:
                # Extract attention weights
                if isinstance(output, tuple) and len(output) > 1:
                    attention_weights = output[1]
                    
                    if attention_weights is not None:
                        # Signal #3: Attention patterns
                        signals = {
                            'framework': 'pytorch',
                            'signal_type': 'attention',
                            'layer_index': layer_idx,
                            'timestamp': time.time(),
                            
                            # Attention metrics
                            'attention_metrics': {
                                'entropy_per_head': self._compute_attention_entropy(attention_weights),
                                'max_attention': float(attention_weights.max()),
                                'mean_attention': float(attention_weights.mean()),
                                'head_agreement': float(attention_weights.std(dim=1).mean())
                            },
                            
                            # Shape information
                            'shape': list(attention_weights.shape),
                            'num_heads': attention_weights.shape[1]
                        }
                        
                        self.exporter.export(signals)
            
            except Exception as e:
                logger.error(f"Error in attention hook: {e}")
        
        return hook
    
    def _create_classification_hook(self, layer_name: str):
        """Create hook for pre-classification embeddings (PRIMARY SIGNAL)"""
        def hook(module, input, output):
            try:
                # This is the KEY signal for domain detection!
                cls_embedding = input[0].detach().cpu()
                
                signals = {
                    'framework': 'pytorch',
                    'signal_type': 'pre_classification',
                    'layer_name': layer_name,
                    'timestamp': time.time(),
                    
                    # Raw embedding vector (768-dim for BERT-base)
                    'embedding': cls_embedding.numpy().tolist(),
                    
                    # Comprehensive statistics
                    'statistics': {
                        'mean': float(cls_embedding.mean()),
                        'std': float(cls_embedding.std()),
                        'norm': float(torch.norm(cls_embedding)),
                        'max': float(cls_embedding.max()),
                        'min': float(cls_embedding.min())
                    },
                    
                    # Neural health indicators
                    'neural_health': {
                        'sparsity': float((cls_embedding == 0).float().mean()),
                        'saturation': float((torch.abs(cls_embedding) > 0.95).float().mean()),
                        'stability': self._compute_stability(cls_embedding)
                    },
                    
                    # Domain detection indicators
                    'domain_indicators': {
                        'magnitude': float(torch.norm(cls_embedding)),
                        'information_density': float((cls_embedding != 0).float().mean()),
                        'preliminary_ood_score': self._quick_ood_estimate(cls_embedding)
                    }
                }
                
                self.exporter.export(signals)
            
            except Exception as e:
                logger.error(f"Error in classification hook: {e}")
        
        return hook
    
    def _create_generic_hook(self, layer_name: str):
        """Create generic hook for unknown layers"""
        def hook(module, input, output):
            try:
                if isinstance(output, torch.Tensor):
                    signals = {
                        'framework': 'pytorch',
                        'signal_type': 'generic_activation',
                        'layer_name': layer_name,
                        'timestamp': time.time(),
                        'statistics': self._compute_tensor_statistics(output)
                    }
                    self.exporter.export(signals)
            except Exception as e:
                logger.error(f"Error in generic hook: {e}")
        
        return hook
    
    # Helper methods
    
    def _extract_cls_embedding(self, hidden_state: torch.Tensor) -> List[float]:
        """Extract CLS token embedding"""
        try:
            if hidden_state.dim() >= 3:
                # [batch, seq_len, hidden_size] -> take first token
                cls_token = hidden_state[0, 0, :].detach().cpu()
                return cls_token.numpy().tolist()
        except:
            pass
        return []
    
    def _compute_tensor_statistics(self, tensor: torch.Tensor) -> Dict[str, float]:
        """Compute comprehensive tensor statistics"""
        tensor_cpu = tensor.detach().cpu()
        return {
            'mean': float(tensor_cpu.mean()),
            'std': float(tensor_cpu.std()),
            'max': float(tensor_cpu.max()),
            'min': float(tensor_cpu.min()),
            'shape': list(tensor.shape)
        }
    
    def _compute_neural_health(self, tensor: torch.Tensor) -> Dict[str, float]:
        """Compute neural health metrics"""
        tensor_cpu = tensor.detach().cpu()
        return {
            'sparsity': float((tensor_cpu == 0).float().mean()),
            'saturation': float((torch.abs(tensor_cpu) > 0.95).float().mean()),
            'dead_neurons': float((tensor_cpu.abs().mean(dim=[0, 1]) < 1e-6).float().mean()) if tensor_cpu.dim() >= 3 else 0.0
        }
    
    def _compute_attention_entropy(self, attention: torch.Tensor) -> List[float]:
        """Compute entropy per attention head"""
        entropies = []
        try:
            for head in range(attention.shape[1]):
                head_attn = attention[0, head, :, :]
                entropy = -(head_attn * torch.log(head_attn + 1e-9)).sum(dim=-1).mean()
                entropies.append(float(entropy))
        except:
            pass
        return entropies
    
    def _compute_stability(self, tensor: torch.Tensor) -> float:
        """Compute neural stability score"""
        variance = float(tensor.var())
        return 1.0 / (1.0 + variance)
    
    def _quick_ood_estimate(self, embedding: torch.Tensor) -> float:
        """Quick out-of-domain estimation"""
        sparsity = float((embedding == 0).float().mean())
        norm = float(torch.norm(embedding))
        
        # Simple heuristic: high sparsity + low norm suggests OOD
        if sparsity > 0.3 and norm < 15.0:
            return -1.0  # Likely out-of-domain
        else:
            return 1.0   # Likely in-domain
    
    def cleanup(self):
        """Remove all hooks"""
        for hook in self.hooks:
            hook.remove()
        self.hooks.clear()
        logger.info("Cleaned up all PyTorch hooks")
