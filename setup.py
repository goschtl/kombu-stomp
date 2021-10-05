import os

import setuptools


requires = [
    'kombu',
    'stomp.py==4.1.24',
    'six',
]

test_requires = [
    'mock',
    'pytest',
    'pytest-xdist',
    'pytest-cov'
]


setuptools.setup(
    version='0.3.1',
    zip_safe=True,
    install_requires=requires,
    tests_require=test_requires,
    setup_requires='d2to1',
    d2to1=True,
)
