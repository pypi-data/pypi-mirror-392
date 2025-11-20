import logging

import colorlog


def builder(
    class_name: str = None, format: str = None, date_fmt: str = None, defaults: dict = None
):
    if class_name == "logging.Formatter":
        kwargs = {
            "fmt": format,
            "datefmt": date_fmt,
        }
        kwargs["defaults"] = defaults
        return logging.Formatter(**kwargs)
    if class_name == "colorlog.ColoredFormatter":
        kwargs = {
            "fmt": format,
            "datefmt": date_fmt,
        }
        kwargs["defaults"] = defaults
        return colorlog.ColoredFormatter(**kwargs)

    raise NotImplementedError(f"class_name={class_name}")
