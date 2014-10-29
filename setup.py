import re

from setuptools import find_packages, setup

version = re.search(r'(?m)^__version__ = [\'"](.+)[\'"]$',
                    open('antlr4/__init__.py').read()).group(1)

long_description = open('README.rst').read()

setup(
    name='antlr4-python-alt',
    version=version,

    description='Alternative Python runtime for ANTLR 4',
    long_description=long_description,
    author='Brian Kearns',
    author_email='bdkearns@gmail.com',
    url='https://github.com/bdkearns/antlr4-python-alt',
    license='BSD',

    packages=find_packages(),
)
