from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="textql",
    version="0.3.3",
    author="TextQL Labs",
    description="Python client library for TextQL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={
        "textql": ["py.typed", "**/*.pyi"],
    },
    python_requires=">=3.8",
    install_requires=[
        "grpcio>=1.68.0",
        "protobuf>=5.28.0",
    ],
    extras_require={
        "dev": [
            "grpcio-tools>=1.68.0",
            "black",
            "mypy",
            "mypy-protobuf",
            "ruff>=0.1.0",
            "types-protobuf>=4.0.0",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Typing :: Typed",
    ],
)
