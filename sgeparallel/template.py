from functools import reduce
from os.path import basename


def params_substitute(params_template, replacement):
    """
    :type params_template: dict[str, object]
    :type replacement: str
    :rtype: dict[str, object]
    """

    return {
        name: parse_arg(value, replacement) \
                if isinstance(value, str) \
              else value
        for name, value in params_template.items()
    }


def command_substitute(command_template, replacement):
    """
    :type command_template: list[str]
    :type replacement: str
    :rtype: list[str]
    """
    return [command_template[0]] + [parse_arg(arg, replacement)for arg in command_template[1:]]


def parse_arg(arg, repacement):
    for tpl, func in REPL_STRINGS.items():
        if tpl in arg:
            arg = arg.replace(tpl, func(repacement))
    return arg


def crop_extention(x):
    return '.'.join(x.split('.')[:-1])


def first(x):
    return x.split()[0]


def second(x):
    return x.split()[1]


def compose(*funcs):
    def wrapper(x):
        return reduce(lambda v, f: f(v), reversed(funcs), x)
    return wrapper


REPL_STRINGS = {
    '[]': lambda x: x,
    '[1]': first,
    '[2]': second,

    '[/]': basename,
    '[1/]': compose(basename, first),
    '[2/]': compose(basename, second),

    '[.]': crop_extention,
    '[1.]': compose(crop_extention, first),
    '[2.]': compose(crop_extention, second),

    '[/.]': compose(crop_extention, basename),
    '[1/.]': compose(crop_extention, basename, first),
    '[2/.]': compose(crop_extention, basename, second),
}