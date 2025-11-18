from setuptools import setup, find_packages

setup(
    name='wecompush',
    version='0.0.2',
    packages=find_packages(),
    install_requires=[
        'httpx',
    ],
)