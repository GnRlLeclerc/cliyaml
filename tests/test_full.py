def test_full():
    from cliyaml import handle, initialize, subcommand

    initialize(None, "tests/subcommand.py")

    handle()
