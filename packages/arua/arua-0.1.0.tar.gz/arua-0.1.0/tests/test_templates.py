from arua.templates import TemplateLibrary


def test_template_library_add_get_remove():
    lib = TemplateLibrary()
    lib.add(
        domain_id=1,
        template_id=42,
        pattern="Hello, {name}!",
        metadata={"route": "chat"},
    )

    t = lib.get(1, 42)
    assert t is not None
    assert t.domain_id == 1
    assert t.template_id == 42
    assert t.pattern == "Hello, {name}!"
    assert t.metadata.get("route") == "chat"

    lib.remove(1, 42)
    assert lib.get(1, 42) is None
