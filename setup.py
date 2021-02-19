from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name='dh-utils',
    version='0.1.21',
    description='Python package containing various utilities relevant in the field of digital humanities.',
    packages=find_packages(),
    install_requires=['regex', 'lxml', 'anytree', 'markdown', 'namedentities'],
    extras_require={
        'betacode': ['cltk']
    },
    keywords='digital humanities utilities unicode tei',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/andredelft/dh-utils",
    include_package_data=True,
    python_requires='>=3.6',
    author='André van Delft',
    author_email='andrevandelft@outlook.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3'
    ]
)
