def test_read_config():
    from cliyaml import configure

    parser = configure("config.yaml")
    args = parser.parse_args()

    assert args.string == "string"

    assert type(args.int) == int
    assert args.int == 0

    assert type(args.float) == float
    assert args.float == 0.0

    assert args.bool == False

    assert args.empty is None

    assert args.nested_one == 1
    assert args.nested_two == 2
