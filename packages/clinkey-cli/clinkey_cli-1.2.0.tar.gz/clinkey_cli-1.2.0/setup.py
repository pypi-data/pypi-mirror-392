from setuptools import setup, find_packages

setup(
    name='clinkey-cli',
    version='1.2.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'clinkey = clinkey_cli.cli:main',
        ],
    },
    install_requires=[
        'click>=8.3.0',
        'rich>=14.1.0',
    ],
)