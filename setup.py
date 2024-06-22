from setuptools import find_packages, setup

setup(
    name='dust',
    packages=find_packages(),
    version='0.1.0',
    description='Fast light weight web server',
    author='c0d3g0d',
    install_requires=[
        'werkzeug',
    ],
)

from setuptools import setup, find_packages

setup(
    name='dust',
    version='0.1',
    packages=find_packages(),
    description='Fast light weight web server',
    author='c0d3g0d',
    install_requires=[
        'werkzeug',
        'jinja2',
        'click',
        'websockets',
        'mkdocs',
        'pyjwt',
    ],
    entry_points={
        'console_scripts': [
            'dust=dust.cli:cli',
        ],
    },
)
