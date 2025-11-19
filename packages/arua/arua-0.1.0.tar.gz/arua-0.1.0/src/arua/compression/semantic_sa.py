"""Sa atom table and helpers.

This module provides a minimal in-process atom table for the Sa codec.
It is intentionally simple and Python-only for now; the layout can
later be replaced by a memory-mapped binary table without changing
the external API.
"""

from __future__ import annotations

from typing import Dict, Mapping


# Sa atom tables keyed by domain_id -> {atom_id: bytes}
_SA_ATOMS: Dict[int, Dict[int, bytes]] = {
    0: {
        # Domain 0: Generic AI/ML common atoms
        # These appear frequently across LLM inference, training, and model serving

        # Common JSON keys
        0: b"id",
        1: b"type",
        2: b"name",
        3: b"model",
        4: b"status",
        5: b"data",
        6: b"result",
        7: b"error",
        8: b"message",
        9: b"content",
        10: b"role",
        11: b"object",
        12: b"created",
        13: b"index",
        14: b"finish_reason",
        15: b"usage",
        16: b"prompt_tokens",
        17: b"completion_tokens",
        18: b"total_tokens",
        19: b"timestamp",

        # Common values
        20: b"success",
        21: b"failed",
        22: b"pending",
        23: b"running",
        24: b"completed",
        25: b"error",
        26: b"warning",
        27: b"info",
        28: b"debug",
        29: b"trace",

        # LLM roles
        30: b"system",
        31: b"user",
        32: b"assistant",
        33: b"function",
        34: b"tool",
        35: b"developer",

        # Common stop reasons
        40: b"stop",
        41: b"length",
        42: b"content_filter",
        43: b"function_call",
        44: b"tool_calls",
        45: b"end_turn",

        # Model names (GPT)
        50: b"gpt-3.5-turbo",
        51: b"gpt-4",
        52: b"gpt-4-turbo",
        53: b"gpt-4o",
        54: b"gpt-4o-mini",

        # Model names (Claude)
        55: b"claude-3-opus",
        56: b"claude-3-sonnet",
        57: b"claude-3-haiku",
        58: b"claude-3-5-sonnet",

        # Model names (Open source)
        60: b"llama-2-7b",
        61: b"llama-2-13b",
        62: b"llama-2-70b",
        63: b"llama-3-8b",
        64: b"llama-3-70b",
        65: b"mistral-7b",
        66: b"mistral-8x7b",
        67: b"mixtral-8x22b",
        68: b"phi-2",
        69: b"phi-3",

        # Request types
        70: b"chat.completion",
        71: b"text.completion",
        72: b"embedding",
        73: b"fine-tune",
        74: b"inference",
        75: b"completion",

        # Common boolean/null
        80: b"true",
        81: b"false",
        82: b"null",
        83: b"True",
        84: b"False",
        85: b"None",

        # Common parameters
        90: b"temperature",
        91: b"max_tokens",
        92: b"top_p",
        93: b"frequency_penalty",
        94: b"presence_penalty",
        95: b"stream",
        96: b"n",
        97: b"logprobs",
        98: b"echo",
        99: b"best_of",

        # Additional keys
        100: b"choices",
        101: b"text",
        102: b"logit_bias",
        103: b"user",
        104: b"suffix",
        105: b"response",
        106: b"request",
        107: b"metadata",
        108: b"version",
        109: b"api_key",
        110: b"organization",

        # Common file/resource types
        120: b"json",
        121: b"yaml",
        122: b"xml",
        123: b"csv",
        124: b"txt",
        125: b"md",
        126: b"pdf",
        127: b"png",
        128: b"jpg",
        129: b"jpeg",

        # Common HTTP/API values
        130: b"application/json",
        131: b"text/plain",
        132: b"text/html",
        133: b"multipart/form-data",
        134: b"Bearer",
        135: b"Basic",

        # Common time units
        140: b"ms",
        141: b"sec",
        142: b"min",
        143: b"hour",
        144: b"day",

        # Common size units
        150: b"B",
        151: b"KB",
        152: b"MB",
        153: b"GB",
        154: b"TB",
    },

    1: {
        # Domain 1: Training/logging atoms
        0: b"epoch",
        1: b"step",
        2: b"loss",
        3: b"accuracy",
        4: b"learning_rate",
        5: b"batch_size",
        6: b"grad_norm",
        7: b"train",
        8: b"val",
        9: b"test",
        10: b"checkpoint",
        11: b"[INFO]",
        12: b"[WARN]",
        13: b"[ERROR]",
        14: b"[DEBUG]",
        15: b"Epoch",
        16: b"Step",
        17: b"Loss",
        18: b"Accuracy",
        19: b"[TRACE]",

        # Metric names
        20: b"precision",
        21: b"recall",
        22: b"f1_score",
        23: b"auc",
        24: b"mse",
        25: b"mae",
        26: b"rmse",
        27: b"perplexity",
        28: b"bleu",
        29: b"rouge",

        # Training phases
        30: b"training",
        31: b"validation",
        32: b"testing",
        33: b"evaluation",
        34: b"inference",

        # Optimizer names
        40: b"adam",
        41: b"adamw",
        42: b"sgd",
        43: b"rmsprop",
        44: b"adagrad",

        # Loss functions
        50: b"cross_entropy",
        51: b"mse_loss",
        52: b"bce_loss",
        53: b"nll_loss",
        54: b"kl_div",

        # Common log patterns
        60: b"INFO",
        61: b"WARN",
        62: b"WARNING",
        63: b"ERROR",
        64: b"DEBUG",
        65: b"CRITICAL",
        66: b"FATAL",

        # Time/iteration
        70: b"iteration",
        71: b"batch",
        72: b"global_step",
        73: b"total_steps",
        74: b"elapsed_time",
        75: b"remaining_time",

        # Checkpoint/model saving
        80: b"save",
        81: b"load",
        82: b"resume",
        83: b"best_model",
        84: b"last_checkpoint",
    },

    2: {
        # Domain 2: Model architecture atoms
        0: b"layer",
        1: b"weight",
        2: b"bias",
        3: b"attention",
        4: b"query",
        5: b"key",
        6: b"value",
        7: b"dense",
        8: b"embedding",
        9: b"LayerNorm",
        10: b"dropout",
        11: b"activation",
        12: b"hidden",
        13: b"output",
        14: b"input",
        15: b"encoder",
        16: b"decoder",
        17: b"self",
        18: b"cross",
        19: b"feedforward",
        20: b"intermediate",

        # Layer types
        30: b"linear",
        31: b"conv1d",
        32: b"conv2d",
        33: b"conv3d",
        34: b"maxpool",
        35: b"avgpool",
        36: b"batchnorm",
        37: b"groupnorm",
        38: b"instancenorm",

        # Activation functions
        40: b"relu",
        41: b"gelu",
        42: b"silu",
        43: b"sigmoid",
        44: b"tanh",
        45: b"softmax",
        46: b"leaky_relu",
        47: b"elu",
        48: b"swish",

        # Attention components
        50: b"multi_head",
        51: b"num_heads",
        52: b"head_dim",
        53: b"qkv",
        54: b"attn_dropout",
        55: b"proj",
        56: b"proj_dropout",

        # Common layer names
        60: b"embeddings",
        61: b"position",
        62: b"token_type",
        63: b"word_embeddings",
        64: b"position_embeddings",
        65: b"norm",
        66: b"ln_1",
        67: b"ln_2",
        68: b"mlp",
        69: b"c_fc",
        70: b"c_proj",

        # Architecture specific
        80: b"transformer",
        81: b"bert",
        82: b"gpt",
        83: b"llama",
        84: b"mistral",
        85: b"resnet",
        86: b"vit",
        87: b"clip",
    },

    3: {
        # Domain 3: Data types and formats
        0: b"float32",
        1: b"float16",
        2: b"int32",
        3: b"int64",
        4: b"bool",
        5: b"string",
        6: b"tensor",
        7: b"array",
        8: b"matrix",
        9: b"vector",
        10: b"scalar",
        11: b"shape",
        12: b"dtype",
        13: b"device",
        14: b"cuda",
        15: b"cpu",
        16: b"mps",
        17: b"rocm",

        # Additional dtypes
        20: b"bfloat16",
        21: b"float64",
        22: b"int8",
        23: b"int16",
        24: b"uint8",
        25: b"uint16",
        26: b"uint32",
        27: b"uint64",
        28: b"complex64",
        29: b"complex128",

        # Tensor ops
        30: b"transpose",
        31: b"reshape",
        32: b"squeeze",
        33: b"unsqueeze",
        34: b"flatten",
        35: b"view",
        36: b"permute",
        37: b"contiguous",

        # Data containers
        40: b"list",
        41: b"tuple",
        42: b"dict",
        43: b"set",
        44: b"ndarray",
        45: b"dataframe",
        46: b"series",

        # Hardware/accelerators
        50: b"cuda:0",
        51: b"cuda:1",
        52: b"cuda:2",
        53: b"cuda:3",
        54: b"gpu",
        55: b"tpu",
        56: b"npu",
        57: b"xpu",

        # Precision/quantization
        60: b"fp32",
        61: b"fp16",
        62: b"bf16",
        63: b"int4",
        64: b"int8",
        65: b"mixed_precision",
        66: b"quantized",
    },

    4: {
        # Domain 4: HTTP/API atoms
        0: b"GET",
        1: b"POST",
        2: b"PUT",
        3: b"DELETE",
        4: b"PATCH",
        5: b"HEAD",
        6: b"OPTIONS",

        # Status codes 2xx
        10: b"200",
        11: b"201",
        12: b"202",
        13: b"204",

        # Status codes 3xx
        20: b"301",
        21: b"302",
        22: b"304",

        # Status codes 4xx
        30: b"400",
        31: b"401",
        32: b"403",
        33: b"404",
        34: b"405",
        35: b"408",
        36: b"409",
        37: b"410",
        38: b"429",

        # Status codes 5xx
        40: b"500",
        41: b"501",
        42: b"502",
        43: b"503",
        44: b"504",

        # Content types
        50: b"application/json",
        51: b"text/plain",
        52: b"text/html",
        53: b"text/csv",
        54: b"application/xml",
        55: b"multipart/form-data",
        56: b"application/octet-stream",
        57: b"image/png",
        58: b"image/jpeg",

        # Headers
        60: b"Content-Type",
        61: b"Authorization",
        62: b"Accept",
        63: b"User-Agent",
        64: b"Content-Length",
        65: b"Host",
        66: b"Connection",
        67: b"Cache-Control",
        68: b"Accept-Encoding",
        69: b"Cookie",

        # Auth
        70: b"Bearer",
        71: b"Basic",
        72: b"Digest",
        73: b"API-Key",
        74: b"X-API-Key",

        # Common header values
        80: b"keep-alive",
        81: b"close",
        82: b"gzip",
        83: b"deflate",
        84: b"br",
        85: b"no-cache",
        86: b"max-age=",
    },

    5: {
        # Domain 5: Common prefixes/suffixes in ML
        0: b"_layer_",
        1: b"_weight",
        2: b"_bias",
        3: b".weight",
        4: b".bias",
        5: b"encoder.",
        6: b"decoder.",
        7: b"attention.",
        8: b".query",
        9: b".key",
        10: b".value",
        11: b"Layer",
        12: b"Norm",
        13: b"embeddings.",
        14: b"position_",
        15: b"token_",

        # Additional layer prefixes
        20: b"layers.",
        21: b"blocks.",
        22: b"transformer.",
        23: b"model.",
        24: b"module.",
        25: b"backbone.",

        # Common suffixes
        30: b".norm",
        31: b".ln",
        32: b".dropout",
        33: b".activation",
        34: b".proj",
        35: b".fc",
        36: b".conv",
        37: b".bn",

        # Numbered patterns
        40: b".0.",
        41: b".1.",
        42: b".2.",
        43: b".3.",
        44: b"_0",
        45: b"_1",
        46: b"_2",
        47: b"_3",

        # PyTorch/TensorFlow
        50: b"torch.",
        51: b"nn.",
        52: b"functional.",
        53: b"tf.",
        54: b"keras.",
        55: b"layers.",

        # Common operations
        60: b"forward",
        61: b"backward",
        62: b"__call__",
        63: b"__init__",
        64: b"__repr__",
    },
}

# Reverse mapping domain_id -> {value: atom_id}
_SA_REVERSE: Dict[int, Dict[bytes, int]] = {
    domain_id: {value: atom_id for atom_id, value in atoms.items()}
    for domain_id, atoms in _SA_ATOMS.items()
}


def get_atom(domain_id: int, atom_id: int) -> bytes | None:
    """Return the Sa atom bytes for a given (domain_id, atom_id)."""
    atoms = _SA_ATOMS.get(domain_id)
    if atoms is None:
        return None
    return atoms.get(atom_id)


def lookup_atom_id(domain_id: int, value: bytes) -> int | None:
    """Return the atom_id for a given (domain_id, value), if present."""
    reverse = _SA_REVERSE.get(domain_id)
    if reverse is None:
        return None
    return reverse.get(value)


def register_atoms_for_domain(domain_id: int, atoms: Mapping[int, bytes]) -> None:
    """Register or extend Sa atoms for a specific domain.

    This helper allows callers (or tests) to define per-domain Sa atom
    catalogs without changing the on-disk table structure. Existing
    entries are preserved; new atom_ids are added, and collisions must
    map to the same value.
    """
    if domain_id < 0:
        raise ValueError("domain_id must be non-negative")
    table = _SA_ATOMS.setdefault(domain_id, {})
    reverse = _SA_REVERSE.setdefault(domain_id, {})
    for atom_id, value in atoms.items():
        if atom_id < 0:
            raise ValueError("atom_id must be non-negative")
        bval = bytes(value)
        existing = table.get(atom_id)
        if existing is not None and existing != bval:
            raise ValueError(f"conflicting Sa atom for domain {domain_id}, id {atom_id}")
        existing_id = reverse.get(bval)
        if existing_id is not None and existing_id != atom_id:
            raise ValueError(f"conflicting Sa atom id for domain {domain_id} and value {bval!r}")
        table[atom_id] = bval
        reverse[bval] = atom_id
