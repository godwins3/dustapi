from setuptools import setup, find_packages

setup(
    name='dustapi',
    version='0.0.1',
    packages=find_packages(),
    description='Fast light weight web server',
    author='Praise Godwins',
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
            'dustapi=dustapi.cli:cli',
        ],
    },
)
