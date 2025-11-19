"""Semantic Binary (Sb) template tables and helpers.

This module provides a minimal, in-process template table for the Sb
codec. It allows semantic_compress/semantic_decompress to treat Sb
payloads as header-only when a (domain_id, template_id) entry exists,
while falling back to the legacy core compressor when no entry is
available or when values conflict.

The initial implementation stores full-byte templates only; templated
slots can be layered on top later without changing the basic lookup
API.
"""

from __future__ import annotations

from typing import Dict, Mapping


# Sb template tables keyed by domain_id -> {template_id: bytes}
_SB_TEMPLATES: Dict[int, Dict[int, bytes]] = {
    0: {
        # Domain 0: Common JSON response templates
        # These are repeated structures in LLM API responses

        # Single-field openers
        0: b'{"id":',
        1: b',"type":',
        2: b',"model":',
        3: b',"status":',
        4: b',"content":',
        5: b',"role":',
        6: b',"object":',
        7: b',"created":',
        8: b',"index":',
        9: b',"finish_reason":',

        # Multi-field openers
        10: b'{"id":"',
        11: b'","model":"',
        12: b'","object":"',
        13: b'","created":',
        14: b',"choices":[',
        15: b'{"index":0,',
        16: b',"message":{',
        17: b'"role":"',
        18: b'","content":"',
        19: b'"},"finish_reason":"',

        # Usage block
        20: b',"usage":{',
        21: b'"prompt_tokens":',
        22: b',"completion_tokens":',
        23: b',"total_tokens":',
        24: b'}}',
        25: b'},"usage":{',

        # Complete responses
        30: b'{"status":"success"}',
        31: b'{"status":"failed"}',
        32: b'{"status":"pending"}',
        33: b'{"error":null}',
        34: b',"error":null',
        35: b'{"success":true}',
        36: b'{"success":false}',

        # Common LLM response structure
        40: b'{"id":"chatcmpl-',
        41: b'","object":"chat.completion",',
        42: b'"created":',
        43: b',"model":"',
        44: b'","choices":[{"index":0,"message":{"role":"',
        45: b'","content":"',
        46: b'"},"finish_reason":"stop"}],',

        # Common parameters
        50: b',"temperature":',
        51: b',"max_tokens":',
        52: b',"top_p":',
        53: b',"stream":false',
        54: b',"stream":true',

        # Array patterns
        60: b'[{"',
        61: b'"},{"',
        62: b'}]',
        63: b'":null,',
        64: b'":true,',
        65: b'":false,',

        # Common closures
        70: b'}]}',
        71: b'}}}',
        72: b'}]}}',
    },

    1: {
        # Domain 1: Training log templates
        # Repeated prefixes in training output

        0: b'[INFO] Epoch ',
        1: b'/10, Step ',
        2: b'/100, Loss: ',
        3: b', Accuracy: ',
        4: b', LR: ',
        5: b'[WARN] ',
        6: b'[ERROR] ',
        7: b'[DEBUG] ',
        8: b'Epoch ',
        9: b' Step ',
        10: b' Loss: ',
        11: b' Accuracy: ',
        12: b' Learning Rate: ',

        # Extended log patterns
        20: b'[INFO] ',
        21: b'[WARNING] ',
        22: b'[ERROR] ',
        23: b'[DEBUG] ',
        24: b'[CRITICAL] ',

        # Timestamp patterns
        30: b'2024-',
        31: b'2025-',
        32: b' INFO ',
        33: b' ERROR ',
        34: b' WARNING ',

        # Training metrics
        40: b'train_loss: ',
        41: b'val_loss: ',
        42: b'train_acc: ',
        43: b'val_acc: ',
        44: b'lr: ',
        45: b'epoch: ',
        46: b'step: ',
        47: b'batch: ',

        # Common phrases
        50: b'Training epoch ',
        51: b'Validation epoch ',
        52: b'Test epoch ',
        53: b'Best model saved at ',
        54: b'Checkpoint saved to ',
        55: b'Loading checkpoint from ',

        # Progress indicators
        60: b' - loss: ',
        61: b' - accuracy: ',
        62: b' - val_loss: ',
        63: b' - val_accuracy: ',
        64: b'ETA: ',
        65: b'Time: ',
    },

    2: {
        # Domain 2: Model checkpoint templates
        # Common patterns in checkpoint metadata

        0: b'"encoder.layer.',
        1: b'.attention.self.',
        2: b'.query.weight',
        3: b'.key.weight',
        4: b'.value.weight',
        5: b'.output.dense.weight',
        6: b'.output.LayerNorm.weight',
        7: b'.output.LayerNorm.bias',
        8: b'.intermediate.dense.weight',
        9: b'embeddings.word_embeddings.weight',
        10: b'embeddings.position_embeddings.weight',
        11: b'embeddings.token_type_embeddings.weight',
        12: b'embeddings.LayerNorm.weight',
        13: b'embeddings.LayerNorm.bias',

        # Transformer patterns
        20: b'model.layers.',
        21: b'.self_attn.',
        22: b'.q_proj.weight',
        23: b'.k_proj.weight',
        24: b'.v_proj.weight',
        25: b'.o_proj.weight',
        26: b'.mlp.gate_proj.weight',
        27: b'.mlp.up_proj.weight',
        28: b'.mlp.down_proj.weight',
        29: b'.input_layernorm.weight',
        30: b'.post_attention_layernorm.weight',

        # Common layer prefixes
        40: b'transformer.h.',
        41: b'transformer.wte.weight',
        42: b'transformer.wpe.weight',
        43: b'transformer.ln_f.weight',
        44: b'transformer.ln_f.bias',

        # Attention patterns
        50: b'.attn.c_attn.weight',
        51: b'.attn.c_attn.bias',
        52: b'.attn.c_proj.weight',
        53: b'.attn.c_proj.bias',
        54: b'.ln_1.weight',
        55: b'.ln_1.bias',
        56: b'.ln_2.weight',
        57: b'.ln_2.bias',

        # MLP patterns
        60: b'.mlp.c_fc.weight',
        61: b'.mlp.c_fc.bias',
        62: b'.mlp.c_proj.weight',
        63: b'.mlp.c_proj.bias',

        # BERT-style
        70: b'bert.encoder.layer.',
        71: b'.attention.output.dense.',
        72: b'.attention.output.LayerNorm.',
        73: b'.intermediate.dense.',
        74: b'.output.dense.',
        75: b'.output.LayerNorm.',
    },

    3: {
        # Domain 3: HTTP headers and common prefixes
        0: b'HTTP/1.1 200 OK\r\n',
        1: b'HTTP/1.1 201 Created\r\n',
        2: b'HTTP/1.1 400 Bad Request\r\n',
        3: b'HTTP/1.1 404 Not Found\r\n',
        4: b'HTTP/1.1 500 Internal Server Error\r\n',
        5: b'Content-Type: application/json\r\n',
        6: b'Content-Type: text/plain\r\n',
        7: b'Authorization: Bearer ',
        8: b'\r\nContent-Length: ',
        9: b'\r\n\r\n',

        # Additional status lines
        10: b'HTTP/1.1 ',
        11: b'HTTP/2 ',
        12: b' OK\r\n',
        13: b' Bad Request\r\n',
        14: b' Not Found\r\n',
        15: b' Internal Server Error\r\n',
        16: b' Unauthorized\r\n',
        17: b' Forbidden\r\n',

        # Common headers
        20: b'Content-Type: ',
        21: b'Content-Length: ',
        22: b'Authorization: ',
        23: b'Accept: ',
        24: b'User-Agent: ',
        25: b'Host: ',
        26: b'Connection: ',
        27: b'Cache-Control: ',
        28: b'Accept-Encoding: ',

        # Header endings
        30: b'\r\nContent-Type: application/json\r\n',
        31: b'\r\nContent-Type: text/plain\r\n',
        32: b'\r\nContent-Length: ',
        33: b'\r\nAuthorization: Bearer ',
        34: b'\r\nConnection: keep-alive\r\n',
        35: b'\r\nConnection: close\r\n',

        # Request lines
        40: b'GET /',
        41: b'POST /',
        42: b'PUT /',
        43: b'DELETE /',
        44: b' HTTP/1.1\r\n',
        45: b' HTTP/2\r\n',

        # Common paths
        50: b'/api/',
        51: b'/v1/',
        52: b'/health',
        53: b'/status',
        54: b'/metrics',
    },

    4: {
        # Domain 4: Common function signatures in Python ML code
        0: b'def __init__(self, ',
        1: b'def forward(self, ',
        2: b'def backward(self, ',
        3: b'def train(self, ',
        4: b'def eval(self, ',
        5: b'def predict(self, ',
        6: b'def fit(self, ',
        7: b'def transform(self, ',
        8: b'): -> ',
        9: b'import torch\n',
        10: b'import numpy as np\n',
        11: b'from typing import ',
        12: b'class ',
        13: b'    def ',
        14: b'self.',
        15: b'return ',

        # Extended imports
        20: b'import torch.nn as nn\n',
        21: b'import torch.nn.functional as F\n',
        22: b'from torch import Tensor\n',
        23: b'import tensorflow as tf\n',
        24: b'from tensorflow import keras\n',
        25: b'import pandas as pd\n',
        26: b'from dataclasses import dataclass\n',

        # Type hints
        30: b'def ',
        31: b'(self, ',
        32: b') -> ',
        33: b': int',
        34: b': float',
        35: b': str',
        36: b': bool',
        37: b': List[',
        38: b': Dict[',
        39: b': Tensor',
        40: b': Optional[',

        # Common patterns
        50: b'if __name__ == "__main__":\n',
        51: b'if __name__ == \'__main__\':\n',
        52: b'    pass\n',
        53: b'    return ',
        54: b'raise ValueError(',
        55: b'raise TypeError(',
        56: b'assert ',

        # ML-specific
        60: b'model = ',
        61: b'optimizer = ',
        62: b'criterion = ',
        63: b'loss = ',
        64: b'output = ',
        65: b'.to(device)',
        66: b'.cuda()',
        67: b'.cpu()',
    },

    5: {
        # Domain 5: Common docstring patterns
        0: b'"""',
        1: b'    Args:\n',
        2: b'    Returns:\n',
        3: b'    Raises:\n',
        4: b'    Examples:\n',
        5: b'        >>> ',
        6: b'    Parameters:\n',
        7: b'        ',
        8: b'\n    ',

        # Extended docstring
        10: b'"""\n',
        11: b'    """\n',
        12: b'    Parameters\n',
        13: b'    ----------\n',
        14: b'    Returns\n',
        15: b'    -------\n',
        16: b'    Notes\n',
        17: b'    -----\n',

        # Type documentation
        20: b'        type: ',
        21: b'        shape: ',
        22: b'        dtype: ',
        23: b'        default: ',
        24: b'        optional: ',

        # Common descriptions
        30: b'    Input tensor',
        31: b'    Output tensor',
        32: b'    Batch size',
        33: b'    Hidden dimension',
        34: b'    Number of ',
    },
}


def get_template(domain_id: int, template_id: int) -> bytes | None:
    """Return the Sb template bytes for a given (domain_id, template_id)."""
    table = _SB_TEMPLATES.get(domain_id)
    if table is None:
        return None
    return table.get(template_id)


def register_template(domain_id: int, template_id: int, value: bytes) -> bool:
    """Register a template value for (domain_id, template_id).

    Returns:
        True if the value was registered or already matched an existing
        entry, False if a conflicting value exists (caller should fall
        back to a non-table representation in that case).
    """
    table = _SB_TEMPLATES.setdefault(domain_id, {})
    existing = table.get(template_id)
    if existing is not None and existing != value:
        return False
    table[template_id] = value
    return True


def register_templates_for_domain(domain_id: int, templates: Mapping[int, bytes]) -> None:
    """Register or extend Sb templates for a specific domain.

    This helper mirrors :func:`semantic_sa.register_atoms_for_domain`
    and allows per-domain template catalogs to be populated in a single
    call. Conflicting entries (same template_id with different value)
    raise ``ValueError``.
    """
    if domain_id < 0:
        raise ValueError("domain_id must be non-negative")
    table = _SB_TEMPLATES.setdefault(domain_id, {})
    for template_id, value in templates.items():
        if template_id < 0:
            raise ValueError("template_id must be non-negative")
        bval = bytes(value)
        existing = table.get(template_id)
        if existing is not None and existing != bval:
            raise ValueError(
                f"conflicting Sb template for domain {domain_id}, id {template_id}"
            )
        table[template_id] = bval
