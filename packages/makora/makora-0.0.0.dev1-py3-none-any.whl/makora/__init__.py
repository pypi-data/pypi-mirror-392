from .utils import (
    static_property,
    add_module_properties,
)


def _get_version() -> str:
    from . import version

    return version.version


def _get_has_repo() -> bool:
    from . import version

    return version.has_repo


def _get_repo() -> str:
    from . import version

    return version.repo


def _get_commit() -> str:
    from . import version

    return version.commit


__version__: str
__has_repo__: bool
__repo__: str
__commit__: str


__all__ = [
    "__version__",
    "__has_repo__",
    "__repo__",
    "__commit__",
]


add_module_properties(
    __name__,
    {
        "__version__": static_property(staticmethod(_get_version)),
        "__has_repo__": static_property(staticmethod(_get_has_repo)),
        "__repo__": static_property(staticmethod(_get_repo)),
        "__commit__": static_property(staticmethod(_get_commit)),
    },
)
