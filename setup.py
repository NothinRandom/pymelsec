from setuptools import setup

__version__      = '0.2.4'
__license__      = 'MIT'
__author__       = 'Tri Quach'
__author_email__ = 'nothinrandom@gmail.com'
__url__          = 'https://github.com/NothinRandom/pymelsec'

setup(
    name="pymelsec",
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    url=__url__,
    description="A Python MELSEC Communication library for communicating with Mitsubishi PLCs.",
    license="MIT",
    packages=["pymelsec"],
    python_requires=">=3.7.0",
)
