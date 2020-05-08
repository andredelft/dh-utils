from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'dh-utils',
    version = '0.1.0',
    description = 'Python package containing various utilities relevant in the field of digital humanities.',
    packages = find_packages(),
    install_requires = ['regex'],
    keywords = 'ebook understanding nltk reading toolkit',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    python_requires = '>=3.6',
    author = 'Andre van Delft',
    author_email = 'andrevandelft@outlook.com',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3'
    ]
)
