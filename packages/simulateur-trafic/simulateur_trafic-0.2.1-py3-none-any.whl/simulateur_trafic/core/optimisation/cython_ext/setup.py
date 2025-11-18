"""Script de construction pour l'extension Cython de mise à jour des positions."""

from __future__ import annotations

from pathlib import Path

from Cython.Build import cythonize
from setuptools import Extension, setup

MODULE_PATH = Path(__file__).parent

extensions = [
    Extension(
        name="core.optimisation.cython_ext._position_update",
        sources=[str(MODULE_PATH / "_position_update.pyx")],
        extra_compile_args=[],
    )
]

setup(
    name="cython-position-update",
    ext_modules=cythonize(
        extensions,
        language_level="3",
        annotate=False,
    ),
    version="0.1",
    author="Dhia BEN HAMOUDA",
    author
    
    zip_safe=False,
)

