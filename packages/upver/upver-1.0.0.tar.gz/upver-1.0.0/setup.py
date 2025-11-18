from setuptools import setup, find_packages

#Add Readme File to PyPi:
with open("README.md", "r") as f:
    description = f.read()

setup(
    name='upver',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        # e.g. 'numpy>=1.11.1
    ],
    entry_points={
        "console_scripts": [
            "upver = upver:main",
        ],
    },
    long_description=description,
    long_description_content_type="text/markdown",
)