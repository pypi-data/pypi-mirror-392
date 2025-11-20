import argunparse


def to_arg_unparse(
    argunparser_kwargs: dict = None,
    command: str = None,
    sub_command: str = None,
    options: dict | list = None,
    arguments: list = None,
) -> list[str]:
    """
    Usage:
    to_arg_unparse(command="cmd", sub_command="sub", options={'foo':True, 'bar':'baz}, args=['file.txt'])
    > cmd sub --foo --bar=baz file.txt

    to_arg_unparse(command="cmd", sub_command="sub", options=['foo', True, 'bar', 'baz', 'bar', 'baz'], args=['file.txt'])
    > cmd sub --foo --bar=baz --bar=baz2 file.txt

    """
    if argunparser_kwargs is None:
        argunparser_kwargs = {}
    if arguments is None:
        arguments = []
    unparser = argunparse.ArgumentUnparser(**argunparser_kwargs)

    data = []
    if isinstance(options, dict):
        data = unparser.unparse_options_and_args_to_list(options, arguments)
    elif isinstance(options, list):
        # Convert options in list of tuple
        it = iter(options)
        for k, v in list(zip(it, it)):
            if k is None:
                continue

            if isinstance(v, bool) and v is True:
                data.append(f"--{k}")
            elif isinstance(v, bool) and v is False:
                pass
            elif not isinstance(v, bool) and v is not None:
                data.append(f"--{k}={v}")

        data.extend(arguments)

    data = [command, sub_command] + data
    return list(filter(lambda x: x is not None, iter(data)))
