from setuptools import setup, Extension
from Cython.Build import cythonize
from pathlib import Path

# Путь к текущей папке
this_directory = Path(__file__).parent
# Читаем README.md
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Определяем Cython-модуль
extensions = [
    Extension(
        "aiocache_pro",          # имя модуля внутри пакета
        ["src/aiocache_pro.pyx"],    # путь к файлу .pyx
    )
]

setup(
    name="aiocache_pro",
    version="0.0.2",
    author="Maksym",
    author_email="",
    description="High-performance caching library with gevent and cython speedups",
    long_description=long_description,
    long_description_content_type="text/markdown",
    ext_modules=cythonize(extensions, language_level=3),
    install_requires=[
        "gevent",
        "ujson",
        "b64fx",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Cython",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)