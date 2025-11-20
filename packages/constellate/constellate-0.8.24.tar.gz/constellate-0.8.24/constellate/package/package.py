import importlib.util


def package_available(name: str = None) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except ImportError:
        return False
