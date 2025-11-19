from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="damaged_reads_simulator",
    version="0.1.0",
    author="Ariel Erijman (NEB Labs) ",
    author_email="aerijman@neb.com",
    description="A simulator for damaged DNA reads with base quality recalibration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nebiolabs/damaged_reads_simulator",
    py_modules=["generate_reference_and_reads"],
    packages=["libs"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "scipy",
        "pandas",
        "matplotlib",
        "seaborn",
        "biopython",
        "fast_string_replace",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "simulate-reads=generate_reference_and_reads:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.info", "*.tsv", "*.sh"],
    },
)