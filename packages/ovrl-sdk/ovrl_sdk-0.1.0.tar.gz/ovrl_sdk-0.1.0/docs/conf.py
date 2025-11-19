"""Sphinx configuration for the OVRL SDK documentation."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - fallback for older interpreters
    import tomli as tomllib  # type: ignore[assign]


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = PROJECT_ROOT / "ovrl_sdk"
PYPROJECT = PROJECT_ROOT / "pyproject.toml"

sys.path.insert(0, str(PROJECT_ROOT))

with PYPROJECT.open("rb") as fp:
    pyproject_data = tomllib.load(fp)

project = "OVRL SDK"
author = "Overlumens"
release = pyproject_data["project"]["version"]
version = release
current_year = datetime.utcnow().year
copyright = f"{current_year}, {author}"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

autodoc_typehints = "description"
autodoc_member_order = "bysource"
autosummary_generate = ["api.rst"]
napoleon_google_docstring = False
napoleon_numpy_docstring = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "stellar_sdk": ("https://stellar-sdk.readthedocs.io/en/latest", None),
}

templates_path = ["_templates"]
exclude_patterns: list[str] = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinxawesome_theme"
html_static_path = ["_static"]
html_show_sourcelink = True

html_theme_options = {}

rst_epilog = """
.. |project| replace:: OVRL SDK
"""

# Avoid importing heavy dependencies when building API docs locally/CI.
autodoc_mock_imports = ["stellar_sdk", "aiohttp"]
