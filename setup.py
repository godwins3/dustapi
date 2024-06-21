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

