from arua.compression.semantic_table import (
    TableColumn,
    TableSchema,
    encode_table_binary,
    decode_table_binary,
)


def test_st_binary_roundtrip_basic() -> None:
    rows = [
        {"id": 1, "name": "Alice", "active": True},
        {"id": 2, "name": "Bob", "active": False},
    ]
    schema = TableSchema(
        columns=(
            TableColumn(name="id", type="int"),
            TableColumn(name="name", type="string"),
            TableColumn(name="active", type="bool"),
        )
    )
    payload = encode_table_binary(rows, schema=schema)
    out_rows, out_schema = decode_table_binary(payload)

    assert len(out_rows) == 2
    assert out_rows[0]["id"] == 1
    assert out_rows[0]["name"] == "Alice"
    assert out_rows[0]["active"] is True
    assert out_rows[1]["id"] == 2
    assert out_rows[1]["active"] is False
    assert len(out_schema.columns) == 3

