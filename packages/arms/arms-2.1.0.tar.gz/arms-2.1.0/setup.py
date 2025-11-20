# coding: utf-8
"""
arms
~~~~
Archive and Replacement Management System

A command-line utility for creating and extracting markdown-based file archives
with intelligent text replacement capabilities.

Setup
-----
.. code-block:: bash
    > pip install arms
    > arms -h

"""

import ast
import re
from codecs import open  # To use a consistent encoding
from os import path

from setuptools import find_packages, setup  # Always prefer setuptools over distutils
from setuptools.command.install import install

_version_re = re.compile(r'__version__\s+=\s+(.*)')
version = str(ast.literal_eval(
    _version_re.search(
        open('arms/__init__.py').read()
    ).group(1)
))
here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


class MyInstall(install):
    def run(self):
        print("-- installing... --")
        install.run(self)


setup(
    name='arms',
    version=version,
    description='Archive and Replacement Management System - A markdown-based file archive utility with intelligent text replacement',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://pypi.python.org/pypi/arms',
    author='qorzj',
    author_email='inull@qq.com',
    license='MIT',
    platforms=['any'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Build Tools',
        'Topic :: System :: Archiving',
        'Topic :: Text Processing :: Markup :: Markdown',
    ],
    keywords='archive markdown replacement template packaging distribution',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'lesscli>=0.2.0',
    ],
    cmdclass={'install': MyInstall},
    entry_points={
        'console_scripts': [
            'arms = arms.main:main'
        ],
    },
)
