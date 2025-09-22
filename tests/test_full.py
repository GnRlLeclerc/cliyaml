def test_full():
    from cliyaml import handle, initialize, subcommand

    initialize()

    @subcommand("config.yaml")
    def f(**_):
        print("ok")

    handle()
