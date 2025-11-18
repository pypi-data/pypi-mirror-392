from setuptools import setup
from pathlib import Path

# Read README.md (or README.txt if you really want, but md is better)
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="avadcaded-math",          
    version="0.0.7",                 
    description="A custom math module with more operations than the built-in math module",
    long_description=long_description,  # This is what PyPI will show
    long_description_content_type="text/markdown",  # Important for Markdown
    author="Nguy Nhat",
    py_modules=["avadcaded_math"], 
    install_requires=[
        "numpy",
        "sympy",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
