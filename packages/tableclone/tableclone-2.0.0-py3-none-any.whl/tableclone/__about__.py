#! python3  # noqa: E265

"""
    Metadata bout the package to easily retrieve informations about it.
    See: https://packaging.python.org/guides/single-sourcing-package-version/
"""

from datetime import date

__all__ = [
    "__author__",
    "__copyright__",
    "__email__",
    "__license__",
    "__summary__",
    "__title__",
    "__uri__",
    "__version__",
]

__author__ = "Valérian LEBERT"
__copyright__ = "2020 - {0}, {1}".format(date.today().year, __author__)
__email__ = ""
__executable_name__ = ""
__license__ = ""
__summary__ = "Tableclone processing tools"
__title__ = "Tableclone"
__title_clean__ = "".join(e for e in __title__ if e.isalnum())
__uri__ = "https://tableclone.com"

__version__ = "1.0.0"
__version_info__ = tuple(
    [
        int(num) if num.isdigit() else num
        for num in __version__.replace("-", ".", 1).split(".")
    ]
)
