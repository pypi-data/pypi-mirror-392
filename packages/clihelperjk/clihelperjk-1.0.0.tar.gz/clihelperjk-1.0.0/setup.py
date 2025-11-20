from setuptools import setup, find_packages
import io
import os

here = os.path.abspath(os.path.dirname(__file__))
long_description = ""
readme_path = os.path.join(here, "README.md")
if os.path.exists(readme_path):
    with io.open(readme_path, encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="clihelperjk",
    version="1.0.0",
    description="CLI interactivo para administrar Microsoft Office 2016/2019/2021",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Juan Kraudy",
    author_email="",
    url="",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Utilities",
    ],
    entry_points={
        "console_scripts": [
            "clihelperjk=clihelperjk.__main__:main"
        ]
    },
)
