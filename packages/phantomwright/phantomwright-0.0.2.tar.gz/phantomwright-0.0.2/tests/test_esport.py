def test_all_symbols_reexported():
    import patchright
    import phantomwright

    exported = [
        name for name in dir(patchright)
        if not name.startswith("_")  # 只检查公共 API
    ]

    for name in exported:
        assert hasattr(
            phantomwright, name
        ), f"{name} is missing from phantomwright"
