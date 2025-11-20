from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="opgg.py",
    version="3.0.0",
    description="An unofficial Python library for scraping/accessing data from OP.GG",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ShoobyDoo/OPGG.py",
    author="ShoobyDoo",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="opgg, league-of-legends, web-scraping, summoner, data, riot-api",
    packages=find_packages(),
    python_requires=">=3.12, <4",
    install_requires=["aiohttp", "pydantic", "fake-useragent"],
    project_urls={
        "Bug Reports": "https://github.com/ShoobyDoo/OPGG.py/issues",
        "Source": "https://github.com/ShoobyDoo/OPGG.py",
    },
)
