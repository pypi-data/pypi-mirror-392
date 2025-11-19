"""
PyTorch Adapter
Captures neural signals from PyTorch models
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

import numpy as np  # type: ignore[import-not-found]

try:  # pragma: no cover - optional dependency
    import torch  # type: ignore[import-not-found]
    import torch.nn as nn  # type: ignore[import-not-found]
except Exception as exc:  # pragma: no cover - optional dependency
    torch = None  # type: ignore[assignment]
    nn = None  # type: ignore[assignment]
    _TORCH_IMPORT_ERROR: Optional[Exception] = exc
else:
    _TORCH_IMPORT_ERROR = None

logger = logging.getLogger(__name__)


class PyTorchAdapter:
    """
    PyTorch-specific signal capture adapter
    Automatically hooks into BERT and other transformer models
    """
    
    def __init__(self, exporter, config: Dict[str, Any]):
        if torch is None:
            raise RuntimeError(
                "PyTorch is not installed. Install the 'pytorch' extra to enable "
                "PyTorch monitoring, e.g. pip install onex-sdk[pytorch]"
            ) from _TORCH_IMPORT_ERROR

        self.exporter = exporter
        self.config = config or {}
        self.hooks = []

        # Sampling configuration for exported signals
        batch_value = self.config.get("hidden_state_sample_batch", 1)
        tokens_value = self.config.get("hidden_state_sample_tokens", 4)
        features_value = self.config.get("hidden_state_sample_features", 32)
        precision_value = self.config.get("hidden_state_precision", 6)

        self.sample_batch_size = max(1, int(batch_value or 1))
        self.sample_tokens = max(1, int(tokens_value or 4))
        self.sample_features = max(1, int(features_value or 32))
        self.embedding_precision = int(precision_value) if precision_value is not None else -1
        self.capture_full_hidden_state = bool(self.config.get("capture_full_hidden_state", False))
        
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
                logger.info(f"Hooked encoder layer: {layer}")
                logger.info(f"Hooked encoder layer: {hook}")
        
        # Hook 2: Capture attention patterns
        if hasattr(model, 'bert') and hasattr(model.bert, 'encoder'):
            for layer_idx, layer in enumerate(model.bert.encoder.layer):
                attention = layer.attention.self
                hook = attention.register_forward_hook(
                    self._create_attention_hook(layer_idx)
                )
                logger.info(f"Hooked attention layer: {attention}")
                logger.info(f"Hooked attention layer: {hook}")
                self.hooks.append(hook)
        
        # Hook 2b: Capture embedding outputs
        if hasattr(model, 'bert') and hasattr(model.bert, 'embeddings'):
            hook = model.bert.embeddings.register_forward_hook(
                self._create_embedding_hook('bert_embeddings')
            )
            logger.info(f"Hooked embedding layer: {model.bert.embeddings}")
            logger.info(f"Hooked embedding layer: {hook}")
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
            elif isinstance(module, nn.Embedding):
                hook = module.register_forward_hook(
                    self._create_embedding_hook(name)
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

                hidden_tensor = self._prepare_tensor(hidden_state)
                if hidden_tensor is None:
                    return

                cls_info = self._collect_cls_embeddings(hidden_tensor)

                # Signal #1 & #2: Token states and CLS embedding
                signals = {
                    'framework': 'pytorch',
                    'signal_type': 'hidden_states',
                    'layer_type': layer_type,
                    'layer_index': layer_idx,
                    'timestamp': time.time(),
                    'statistics': self._compute_tensor_statistics(hidden_tensor),
                    'neural_health': self._compute_neural_health(hidden_tensor),
                    'hidden_state_sample': self._sample_hidden_state(hidden_tensor),
                    'token_statistics': self._compute_token_statistics(hidden_tensor),
                    'feature_statistics': self._compute_feature_statistics(hidden_tensor),
                    'token_norms': self._compute_token_norms(hidden_tensor),
                    'pooled_embedding': self._compute_pooled_embeddings(hidden_tensor),
                    'hidden_state_energy': self._compute_hidden_state_energy(hidden_tensor),
                    'cls_embedding': cls_info.get('primary', []),
                    'cls_embedding_batch': cls_info.get('batch', []),
                    'cls_embedding_norms': cls_info.get('norms', []),
                    'cls_embedding_stats': cls_info.get('statistics', {}),
                }

                if self.capture_full_hidden_state:
                    signals['hidden_state_full'] = hidden_tensor.tolist()

                logger.info(
                    "Hidden layer %s (%s) statistics: %s",
                    layer_idx,
                    layer_type,
                    signals["statistics"],
                )
                logger.info(
                    "Hidden layer %s (%s) neural health: %s",
                    layer_idx,
                    layer_type,
                    signals["neural_health"],
                )

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
                        
                        logger.info(
                            "Attention layer %s metrics: %s",
                            layer_idx,
                            signals["attention_metrics"],
                        )
                        logger.info(
                            "Attention layer %s shape: %s",
                            layer_idx,
                            signals["shape"],
                        )

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
                
                logger.info(
                    "Pre-classification layer %s statistics: %s",
                    layer_name,
                    signals["statistics"],
                )
                logger.info(
                    "Pre-classification layer %s neural health: %s",
                    layer_name,
                    signals["neural_health"],
                )
                logger.info(
                    "Pre-classification layer %s domain indicators: %s",
                    layer_name,
                    signals["domain_indicators"],
                )

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
                    logger.info(
                        "Generic activation layer %s statistics: %s",
                        layer_name,
                        signals["statistics"],
                    )
                    self.exporter.export(signals)
            except Exception as e:
                logger.error(f"Error in generic hook: {e}")
        
        return hook

    def _create_embedding_hook(self, embedding_name: str):
        """Capture embedding layer outputs and derived signals."""
        def hook(module, input, output):
            try:
                if isinstance(output, tuple):
                    embedding_output = output[0]
                else:
                    embedding_output = output

                embedding_tensor = self._prepare_tensor(embedding_output)
                if embedding_tensor is None:
                    return

                signals = {
                    'framework': 'pytorch',
                    'signal_type': 'embeddings',
                    'embedding_name': embedding_name,
                    'timestamp': time.time(),
                    'statistics': self._compute_tensor_statistics(embedding_tensor),
                    'neural_health': self._compute_neural_health(embedding_tensor),
                    'embedding_sample': self._sample_hidden_state(embedding_tensor),
                    'token_statistics': self._compute_token_statistics(embedding_tensor),
                    'feature_statistics': self._compute_feature_statistics(embedding_tensor),
                    'token_norms': self._compute_token_norms(embedding_tensor),
                    'pooled_embedding': self._compute_pooled_embeddings(embedding_tensor),
                    'hidden_state_energy': self._compute_hidden_state_energy(embedding_tensor),
                }

                if self.capture_full_hidden_state:
                    signals['embedding_full'] = embedding_tensor.tolist()

                logger.info(
                    "Embedding layer %s statistics: %s",
                    embedding_name,
                    signals["statistics"],
                )
                logger.info(
                    "Embedding layer %s neural health: %s",
                    embedding_name,
                    signals["neural_health"],
                )
                logger.info(
                    "Embedding layer %s sampled tensor: %s",
                    embedding_name,
                    signals["embedding_sample"],
                )

                self.exporter.export(signals)
            except Exception as e:
                logger.error(f"Error in embedding hook: {e}")

        return hook
    
    # Helper methods
    
    def _prepare_tensor(self, tensor: Any) -> Optional[torch.Tensor]:
        """Detach tensor and move to CPU for analysis."""
        if not isinstance(tensor, torch.Tensor):
            return None
        return tensor.detach().to(dtype=torch.float32).cpu()

    def _round_array(self, array: np.ndarray) -> np.ndarray:
        """Round numpy array using configured precision."""
        if self.embedding_precision >= 0:
            return np.round(array, self.embedding_precision)
        return array

    def _sample_hidden_state(self, tensor: torch.Tensor) -> List[Any]:
        """Return a compact numeric snapshot of the hidden state."""
        try:
            if tensor.dim() == 0:
                return []

            if tensor.dim() == 1:
                sample = tensor[:min(self.sample_features, tensor.shape[0])]
            elif tensor.dim() == 2:
                batch_limit = min(self.sample_batch_size, tensor.shape[0])
                feature_limit = min(self.sample_features, tensor.shape[1])
                sample = tensor[:batch_limit, :feature_limit]
            else:
                batch_limit = min(self.sample_batch_size, tensor.shape[0])
                token_limit = min(self.sample_tokens, tensor.shape[1])
                feature_limit = min(self.sample_features, tensor.shape[2])
                sample = tensor[:batch_limit, :token_limit, :feature_limit]

            array = sample.numpy()
            array = self._round_array(array)
            return array.tolist()
        except Exception:
            return []

    def _collect_cls_embeddings(self, hidden_state: torch.Tensor) -> Dict[str, Any]:
        """Collect CLS embeddings and derived metrics."""
        info: Dict[str, Any] = {
            'primary': [],
            'batch': [],
            'norms': [],
            'statistics': {}
        }
        try:
            if hidden_state.dim() < 3 or hidden_state.shape[1] == 0:
                return info

            cls_tokens = hidden_state[:, 0, :]
            if cls_tokens.numel() == 0:
                return info

            primary = cls_tokens[0].numpy()
            info['primary'] = self._round_array(primary).tolist()

            batch_limit = min(self.sample_batch_size, cls_tokens.shape[0])
            batch_sample = cls_tokens[:batch_limit].numpy()
            info['batch'] = self._round_array(batch_sample).tolist()

            norms = cls_tokens.norm(dim=1)
            info['norms'] = norms[:batch_limit].tolist()

            info['statistics'] = {
                'mean': float(cls_tokens.mean().item()),
                'std': float(cls_tokens.std(unbiased=False).item()),
                'norm_mean': float(norms.mean().item()),
                'max': float(cls_tokens.max().item()),
                'min': float(cls_tokens.min().item()),
            }
        except Exception:
            pass
        return info

    def _extract_cls_embedding(self, hidden_state: torch.Tensor) -> List[float]:
        """Maintain backwards compatibility with legacy CLS extraction."""
        cls_info = self._collect_cls_embeddings(hidden_state)
        return cls_info.get('primary', [])

    def _compute_pooled_embeddings(self, hidden_state: torch.Tensor) -> List[Any]:
        """Compute mean pooled embeddings for sampled batch items."""
        try:
            if hidden_state.dim() < 3:
                return []
            pooled = hidden_state.mean(dim=1)
            batch_limit = min(self.sample_batch_size, pooled.shape[0])
            array = pooled[:batch_limit].numpy()
            array = self._round_array(array)
            return array.tolist()
        except Exception:
            return []

    def _compute_tensor_statistics(self, tensor: torch.Tensor) -> Dict[str, float]:
        """Compute comprehensive tensor statistics."""
        tensor_cpu = tensor.detach().cpu().float()
        if tensor_cpu.numel() == 0:
            return {
                'mean': 0.0,
                'std': 0.0,
                'max': 0.0,
                'min': 0.0,
                'shape': list(tensor_cpu.shape)
            }
        return {
            'mean': float(tensor_cpu.mean().item()),
            'std': float(tensor_cpu.std(unbiased=False).item()),
            'max': float(tensor_cpu.max().item()),
            'min': float(tensor_cpu.min().item()),
            'shape': list(tensor_cpu.shape)
        }
    
    def _compute_neural_health(self, tensor: torch.Tensor) -> Dict[str, float]:
        """Compute neural health metrics."""
        tensor_cpu = tensor.detach().cpu().float()
        sparsity = float((tensor_cpu == 0).float().mean().item())
        saturation = float((torch.abs(tensor_cpu) > 0.95).float().mean().item())

        dead_neurons = 0.0
        if tensor_cpu.dim() >= 3:
            dead_neurons = float((tensor_cpu.abs().mean(dim=[0, 1]) < 1e-6).float().mean().item())

        return {
            'sparsity': sparsity,
            'saturation': saturation,
            'dead_neurons': dead_neurons
        }

    def _compute_token_statistics(self, tensor: torch.Tensor) -> List[Dict[str, Any]]:
        """Compute statistics for individual tokens."""
        stats: List[Dict[str, Any]] = []
        try:
            if tensor.dim() < 3:
                return stats

            batch_limit = min(self.sample_batch_size, tensor.shape[0])
            token_limit = min(self.sample_tokens, tensor.shape[1])

            for batch_idx in range(batch_limit):
                for token_idx in range(token_limit):
                    token_vec = tensor[batch_idx, token_idx]
                    stats.append({
                        'batch': batch_idx,
                        'token': token_idx,
                        'mean': float(token_vec.mean().item()),
                        'std': float(token_vec.std(unbiased=False).item()),
                        'norm': float(token_vec.norm().item()),
                        'max': float(token_vec.max().item()),
                        'min': float(token_vec.min().item())
                    })
        except Exception:
            pass
        return stats

    def _compute_feature_statistics(self, tensor: torch.Tensor) -> List[Dict[str, Any]]:
        """Compute statistics across embedding dimensions."""
        stats: List[Dict[str, Any]] = []
        try:
            if tensor.dim() < 3:
                return stats

            batch_limit = min(self.sample_batch_size, tensor.shape[0])
            feature_limit = min(self.sample_features, tensor.shape[2])
            subset = tensor[:batch_limit, :, :feature_limit]

            for feature_idx in range(feature_limit):
                feature_values = subset[:, :, feature_idx]
                stats.append({
                    'feature': feature_idx,
                    'mean': float(feature_values.mean().item()),
                    'std': float(feature_values.std(unbiased=False).item()),
                    'norm': float(feature_values.norm().item()),
                    'max': float(feature_values.max().item()),
                    'min': float(feature_values.min().item())
                })
        except Exception:
            pass
        return stats

    def _compute_token_norms(self, tensor: torch.Tensor) -> List[List[float]]:
        """Return per-token L2 norms for sampled batch items."""
        try:
            if tensor.dim() < 3:
                return []
            norms = tensor.norm(dim=-1)
            batch_limit = min(self.sample_batch_size, norms.shape[0])
            token_limit = min(self.sample_tokens, norms.shape[1])
            subset = norms[:batch_limit, :token_limit]
            return subset.tolist()
        except Exception:
            return []

    def _compute_hidden_state_energy(self, tensor: torch.Tensor) -> float:
        """Compute mean squared activation energy."""
        try:
            return float(tensor.pow(2).mean().item())
        except Exception:
            return 0.0
    
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
