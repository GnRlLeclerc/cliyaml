def test_register():
    import cliyaml
    from cliyaml import initialize

    initialize(None, "tests/subcommand.py")

    assert "f" in cliyaml.__commands__
