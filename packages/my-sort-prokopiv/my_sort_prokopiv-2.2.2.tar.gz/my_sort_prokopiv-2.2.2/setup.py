# setup.py
from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="my-sort-prokopiv",
    version="2.2.2",
    description="A small implementation of Unix sort (supports -r and -n) implemented with Click",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Ваше Ім'я",
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[
        "click>=8.0"
    ],
    entry_points={
        "console_scripts": [
            "my_sort = my_sort.cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
#fdfdfdf