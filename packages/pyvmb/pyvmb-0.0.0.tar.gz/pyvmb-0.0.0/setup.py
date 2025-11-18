# setup.py

import setuptools

# Lê o conteúdo do README para a descrição longa
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Lê a versão do __init__.py para ter uma única fonte
with open("pyvmb/__init__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"')
            break

setuptools.setup(
    name="pyvmb",
    version=version,
    author="Neuroquidit Research and Development",
    author_email="luciano.silva@neuroqudit.io",
    description="A Python framework for simulating Mini-Brain (Brain Organoid) intelligence and dynamics.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seu-usuario/pyvmb", # Substitua pelo seu link do GitHub
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
    ],
    python_requires='>=3.8',
    license="MIT", # Campo de licença explícito
)
