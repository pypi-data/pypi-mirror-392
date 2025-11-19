"""Semantic Table (St) codec.

St encodes tabular data with schema metadata. This codec is designed for
structured table data (CSV-like, database rows), storing schema information
(column names, types) separately from the columnar data.

The wire format embeds table schema as JSON alongside compressed columnar data:
    [2-byte schema_blob_length][schema_blob][compressed_table_data]

Example:
    table_data = b'{"columns": {...}}'  # columnar JSON
    schema = TableSchema(columns=[TableColumn("id", "int"), TableColumn("name", "string")])
    compressed = compress(table_data, schema=schema)
    data, decoded_schema = decompress(compressed)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
import struct
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple, TYPE_CHECKING

from .core import compress as core_compress
from .core import decompress as core_decompress
from .semantic_plans import SemanticPlan, decode_payload_to_plan

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from .semantic import SemanticHeader


@dataclass(frozen=True)
class TableColumn:
    """Column definition for a semantic table."""

    name: str
    type: str  # e.g. "string", "int", "float", "bool", "null", "mixed"


@dataclass(frozen=True)
class TableSchema:
    """Schema describing a table used with St."""

    columns: Tuple[TableColumn, ...]


_ST_TYPE_NULL = 0
_ST_TYPE_BOOL = 1
_ST_TYPE_INT = 2
_ST_TYPE_FLOAT = 3
_ST_TYPE_STR = 4
_ST_TYPE_BYTES = 5

_TABLE_HEADER_STRUCT = struct.Struct(">HI")  # num_columns:u16, num_rows:u32


def _infer_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int) and not isinstance(value, bool):
        return "int"
    if isinstance(value, float):
        return "float"
    return "string"


def infer_schema(rows: Sequence[Mapping[str, Any]]) -> TableSchema:
    """Infer a simple schema from a sequence of row dicts."""
    if not rows:
        return TableSchema(columns=tuple())
    first = rows[0]
    columns: List[TableColumn] = []
    for name, value in first.items():
        col_type = _infer_type(value)
        columns.append(TableColumn(name=name, type=col_type))
    return TableSchema(columns=tuple(columns))


def _rows_to_columnar(
    rows: Sequence[Mapping[str, Any]],
    schema: TableSchema,
) -> Dict[str, List[Any]]:
    """Convert row-major data into a simple column-major dict."""
    columns: Dict[str, List[Any]] = {col.name: [] for col in schema.columns}
    for row in rows:
        for col in schema.columns:
            columns[col.name].append(row.get(col.name))
    return columns


def encode_table_binary(
    rows: Sequence[Mapping[str, Any]],
    schema: TableSchema | None = None,
) -> bytes:
    """Encode rows into an experimental binary St body.

    Layout (big-endian):
        [num_columns:u16][num_rows:u32]
        [for each column:
            name_len:u8, name:name_len UTF-8 bytes]
        [for each column in order:
            for each row:
                encoded cell value...]

    Cell values are encoded using the tags defined above. This helper
    does not change the existing JSON-based encode_table/decode_table
    behaviour and is intended for future hot-path table layouts.
    """
    if schema is None:
        schema = infer_schema(rows)
    num_columns = len(schema.columns)
    num_rows = len(rows)
    if num_columns > 0xFFFF:
        raise ValueError("too many columns for binary St body")

    out = bytearray()
    out.extend(_TABLE_HEADER_STRUCT.pack(num_columns, num_rows))

    # Column descriptors: just column names for now; type remains in TableSchema.
    for col in schema.columns:
        name_bytes = col.name.encode("utf-8")
        if len(name_bytes) > 0xFF:
            raise ValueError("column name too long for binary St body")
        out.append(len(name_bytes))
        out.extend(name_bytes)

    # Encode cells column-major.
    for col in schema.columns:
        for row in rows:
            value = row.get(col.name)
            out.extend(_encode_cell(value))

    return bytes(out)


def decode_table_binary(payload: bytes) -> Tuple[List[Dict[str, Any]], TableSchema]:
    """Decode a binary St body produced by encode_table_binary."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decode_table_binary() expects a bytes-like object")
    view = memoryview(payload)
    if len(view) < _TABLE_HEADER_STRUCT.size:
        raise ValueError("St binary table payload too short for header")
    num_columns, num_rows = _TABLE_HEADER_STRUCT.unpack_from(view, 0)
    offset = _TABLE_HEADER_STRUCT.size

    columns: List[TableColumn] = []
    for _ in range(num_columns):
        if offset >= len(view):
            raise ValueError("St binary table payload truncated before column name length")
        name_len = view[offset]
        offset += 1
        if offset + name_len > len(view):
            raise ValueError("St binary table payload truncated in column name")
        name = bytes(view[offset : offset + name_len]).decode("utf-8")
        offset += name_len
        columns.append(TableColumn(name=name, type="mixed"))

    schema = TableSchema(columns=tuple(columns))

    rows: List[Dict[str, Any]] = [
        {col.name: None for col in schema.columns} for _ in range(num_rows)
    ]

    for col_idx, col in enumerate(schema.columns):
        for row_idx in range(num_rows):
            value, offset = _decode_cell(view, offset)
            rows[row_idx][col.name] = value

    return rows, schema


def _encode_cell(value: Any) -> bytes:
    """Encode a single cell value into a compact binary representation."""
    if value is None:
        return bytes([_ST_TYPE_NULL])
    if isinstance(value, bool):
        return bytes([_ST_TYPE_BOOL, 1 if value else 0])
    if isinstance(value, int) and not isinstance(value, bool):
        out = bytearray()
        out.append(_ST_TYPE_INT)
        out.extend(int(value).to_bytes(8, "big", signed=True))
        return bytes(out)
    if isinstance(value, float):
        out = bytearray()
        out.append(_ST_TYPE_FLOAT)
        out.extend(struct.pack(">d", float(value)))
        return bytes(out)
    if isinstance(value, str):
        data = value.encode("utf-8")
        out = bytearray()
        out.append(_ST_TYPE_STR)
        out.extend(len(data).to_bytes(4, "big"))
        out.extend(data)
        return bytes(out)
    if isinstance(value, (bytes, bytearray)):
        data = bytes(value)
        out = bytearray()
        out.append(_ST_TYPE_BYTES)
        out.extend(len(data).to_bytes(4, "big"))
        out.extend(data)
        return bytes(out)
    # Fallback: JSON-stringify unknown types and store as string.
    text = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
    data = text.encode("utf-8")
    out = bytearray()
    out.append(_ST_TYPE_STR)
    out.extend(len(data).to_bytes(4, "big"))
    out.extend(data)
    return bytes(out)


def _decode_cell(view: memoryview, offset: int) -> Tuple[Any, int]:
    """Decode a single cell value from view starting at offset."""
    if offset >= len(view):
        raise ValueError("St binary table payload truncated before cell tag")
    tag = view[offset]
    offset += 1
    if tag == _ST_TYPE_NULL:
        return None, offset
    if tag == _ST_TYPE_BOOL:
        if offset >= len(view):
            raise ValueError("St binary table payload truncated in bool cell")
        return bool(view[offset]), offset + 1
    if tag == _ST_TYPE_INT:
        if offset + 8 > len(view):
            raise ValueError("St binary table payload truncated in int cell")
        raw = bytes(view[offset : offset + 8])
        offset += 8
        return int.from_bytes(raw, "big", signed=True), offset
    if tag == _ST_TYPE_FLOAT:
        if offset + 8 > len(view):
            raise ValueError("St binary table payload truncated in float cell")
        (val,) = struct.unpack_from(">d", view, offset)
        offset += 8
        return float(val), offset
    if tag in (_ST_TYPE_STR, _ST_TYPE_BYTES):
        if offset + 4 > len(view):
            raise ValueError("St binary table payload truncated before length")
        length = int.from_bytes(view[offset : offset + 4], "big")
        offset += 4
        if offset + length > len(view):
            raise ValueError("St binary table payload length out of range")
        raw = bytes(view[offset : offset + length])
        offset += length
        if tag == _ST_TYPE_STR:
            return raw.decode("utf-8"), offset
        return raw, offset
    raise ValueError(f"unknown St cell tag: {tag}")


def encode_table(
    rows: Sequence[Mapping[str, Any]],
    domain_id: int = 0,
    template_id: int | None = None,
    schema: TableSchema | None = None,
) -> bytes:
    """Encode rows as an St semantic payload.

    Args:
        rows: Sequence of mapping-like row objects (e.g. dicts).
        domain_id: Domain identifier to embed in the St header.
        template_id: Optional template id; ``None`` encodes as 0.
        schema: Optional precomputed :class:`TableSchema`. When omitted,
            the schema is inferred from the first row.
    """
    if schema is None:
        schema = infer_schema(rows)

    schema_payload = [
        {"name": col.name, "type": col.type} for col in schema.columns
    ]
    columns = _rows_to_columnar(rows, schema)
    table_obj = {"schema": schema_payload, "columns": columns}

    text = json.dumps(table_obj, separators=(",", ":"), ensure_ascii=False)
    body = text.encode("utf-8")

    # Local import to avoid circular dependency at module import time.
    from .semantic import semantic_compress

    return semantic_compress(body, codec="St", domain_id=domain_id, template_id=template_id)


def decode_table(
    payload: bytes,
) -> Tuple[List[Dict[str, Any]], TableSchema, SemanticHeader, SemanticPlan]:
    """Decode an St semantic payload back into rows and schema.

    Returns:
        (rows, schema, header, plan)

    Raises:
        ValueError: if the payload does not use the ``St`` codec label or
        if the decoded JSON does not match the expected shape.
    """
    header, plan, _ = decode_payload_to_plan(payload)
    if plan.codec_label != "St":
        raise ValueError(f"expected St payload, got codec {plan.codec_label!r}")
    # Local import to avoid circular dependency at module import time.
    from .semantic import semantic_decompress

    raw = semantic_decompress(payload)
    if not isinstance(raw, (bytes, bytearray)):
        raise TypeError("St payload body must be bytes-like")

    try:
        obj = json.loads(raw.decode("utf-8"))
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError("invalid St payload JSON") from exc

    if not isinstance(obj, dict) or "schema" not in obj or "columns" not in obj:
        raise ValueError("St payload must contain 'schema' and 'columns' keys")

    schema_list = obj["schema"]
    columns_obj = obj["columns"]
    if not isinstance(schema_list, list) or not isinstance(columns_obj, dict):
        raise ValueError("invalid St schema or columns layout")

    columns: List[TableColumn] = []
    for entry in schema_list:
        if not isinstance(entry, dict) or "name" not in entry or "type" not in entry:
            raise ValueError("invalid St schema entry")
        columns.append(TableColumn(name=str(entry["name"]), type=str(entry["type"])))
    schema = TableSchema(columns=tuple(columns))

    # Reconstruct rows from columnar representation.
    num_rows = 0
    if columns:
        first_col = columns_obj.get(columns[0].name, [])
        if not isinstance(first_col, list):
            raise ValueError("St column values must be lists")
        num_rows = len(first_col)

    rows: List[Dict[str, Any]] = []
    for row_idx in range(num_rows):
        row: Dict[str, Any] = {}
        for col in schema.columns:
            col_values = columns_obj.get(col.name, [])
            if not isinstance(col_values, list):
                raise ValueError("St column values must be lists")
            value = col_values[row_idx] if row_idx < len(col_values) else None
            row[col.name] = value
        rows.append(row)

    return rows, schema, header, plan




def compress(data: bytes, schema: TableSchema | None = None) -> bytes:
    """Compress table data with optional schema metadata.

    Args:
        data: The table payload to compress (typically columnar JSON).
        schema: Optional TableSchema with column definitions.
                If None, an empty schema is encoded.

    Returns:
        Compressed payload with embedded table schema.

    The wire format is:
        [2-byte schema_blob_length][schema_blob][compressed_data]

    Where schema_blob is JSON-encoded table schema, and compressed_data
    is the core compressed payload.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("compress() expects a bytes-like object")

    # Encode table schema
    if schema is None:
        schema = TableSchema(columns=tuple())
    
    schema_dict = {"columns": [{"name": col.name, "type": col.type} for col in schema.columns]}
    schema_blob = json.dumps(schema_dict, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    # Enforce schema blob size limit (64KB max for 2-byte length prefix)
    if len(schema_blob) > 0xFFFF:
        raise ValueError("table schema too large (max 65535 bytes)")

    # Compress the actual data payload
    compressed_data = core_compress(bytes(data), method="auto")

    # Pack: [2-byte length][schema_blob][compressed_data]
    schema_length = len(schema_blob)
    length_bytes = bytes([(schema_length >> 8) & 0xFF, schema_length & 0xFF])

    return length_bytes + schema_blob + compressed_data


def decompress(payload: bytes) -> tuple[bytes, TableSchema]:
    """Decompress an St payload and extract table schema.

    Args:
        payload: The compressed payload with embedded table schema.

    Returns:
        A tuple of (decompressed_data, schema).

    Raises:
        TypeError: If payload is not bytes-like.
        ValueError: If payload is malformed.
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("decompress() expects a bytes-like object")

    data = bytes(payload)
    if len(data) < 2:
        raise ValueError("St payload too short for length header")

    # Read 2-byte schema blob length
    schema_length = (data[0] << 8) | data[1]

    # Validate we have enough data
    if len(data) < 2 + schema_length:
        raise ValueError("St payload truncated before schema blob")

    # Extract schema blob and compressed data
    schema_blob = data[2 : 2 + schema_length]
    compressed_data = data[2 + schema_length :]

    # Decode table schema
    try:
        schema_dict = json.loads(schema_blob.decode("utf-8"))
    except Exception as exc:
        raise ValueError("invalid St payload JSON") from exc

    if not isinstance(schema_dict, dict) or "columns" not in schema_dict:
        raise ValueError("St payload must contain a schema with columns")

    columns = []
    for col_dict in schema_dict["columns"]:
        if not isinstance(col_dict, dict) or "name" not in col_dict or "type" not in col_dict:
            raise ValueError("St column must have name and type")
        columns.append(TableColumn(name=str(col_dict["name"]), type=str(col_dict["type"])))

    schema = TableSchema(columns=tuple(columns))

    # Decompress data
    decompressed_data = core_decompress(compressed_data)

    return decompressed_data, schema
