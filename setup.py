from setuptools import setup, find_packages

setup(
    name='dustapi',
    version='0.0.3',
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
        'typer',
    ],
    entry_points={
        'console_scripts': [
            'dustapi=dustapi.cli:cli',
        ],
    },
)
