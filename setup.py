# -*- coding:utf-8 -*-
from setuptools import find_packages, setup
from osc_bsu_backup import __version__

setup(
    name="osc-bsu-backup",
    version=__version__,
    packages=find_packages(),
    author='Outscale SAS',
    author_email='remi.jouannet@outscale.com',
    description="Outscale ",
    url="http://www.outscale.com/",
    entry_points={
        'console_scripts': ['osc-bsu-backup = osc_bsu_backup.cli:main']
    },
    install_requires=[
        'boto3'
    ]
)
