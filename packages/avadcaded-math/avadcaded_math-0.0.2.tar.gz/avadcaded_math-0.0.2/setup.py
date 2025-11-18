from setuptools import setup

setup(
    name="avadcaded_math",          
    version="0.0.2",                 
    description="a custom math module that has many operaton,new update!",
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
