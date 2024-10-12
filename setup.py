from setuptools import setup, find_packages

# Read the content of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='dustapi',
    version='0.0.7',
    packages=find_packages(),
    description='Fast light weight web server',
    long_description=long_description,
    long_description_content_type="text/markdown",  # Use "text/x-rst" if you have a reStructuredText README
    author='Praise G',
    install_requires=[
        'werkzeug',
        'jinja2',
        'click',
        'websockets',
        'mkdocs',
        'pyjwt',
        'typer',
        'pydantic',
    ],
    entry_points={
        'console_scripts': [
            'dustapi=dustapi.cli:cli',
        ],
    },
)
