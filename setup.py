# -*- coding:utf-8 -*-
VERSION = '0.1'

setup(
    name="osc-bsu-backup",
    version=VERSION,
    packages=find_packages(),
    author='Outscale SAS',
    author_email='remi.jouannet@outscale.com',
    description="Outscale ",
    url="http://www.outscale.com/",
    entry_points={
        'console_scripts': [
            'osc-bsu-backup = osc-bsu-backup.cli:main',
        ]
    },
    install_requires=[
        'boto3'
    ]
)
