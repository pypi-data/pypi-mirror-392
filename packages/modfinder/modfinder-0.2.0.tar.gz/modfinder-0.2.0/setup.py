from setuptools import setup, find_packages

setup(
    name="modfinder",
    version="0.2.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "modfinder=modfinder.__main__:main",
        ],
    },
    install_requires=["requests"],
)