from cliyaml import subcommand


@subcommand("config.yaml")
def f(**_):
    print("ok")
