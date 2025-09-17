from setuptools import setup

setup(
    name="simon-nb-cli",
    version="0.1.0",
    packages=["cli_tools"],
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "simon-nb=cli_tools.main:main",
        ],
    },
)
