from setuptools import setup
from Cython.Build import cythonize

setup(
name="ruleforge",
version="0.0.1",
packages=["ruleforge"],
install_requires = ["pandas"],
ext_modules=cythonize(["ruleforge/validators.pyx"], language_level=3),
)
