def test_scaffold_import():
    import hgfx
    assert hasattr(hgfx, "enable_x64")
