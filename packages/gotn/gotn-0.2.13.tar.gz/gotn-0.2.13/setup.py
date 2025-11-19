from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="gotn",
    version="0.2.13",
    packages=find_packages(),
     install_requires=[
        "requests",
        "argparse"
     ],
    entry_points={
        "console_scripts": [
            "gotn=gotn.cli:main",
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
)
