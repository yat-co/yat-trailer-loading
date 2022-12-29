# -*- coding: utf-8 -*-
from ytl import __version__
from setuptools import setup

install_requires = ['numpy', 'matplotlib', ]

setup(
    name='ytl',
    version=__version__,
    author='Jarod Hart & Robert Goss',
    author_email='jhart@yat.ai',
    packages=[
        'ytl', 
    ],
    license="MIT",
    install_requires=install_requires,
    test_suite="tests",
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    description='YAT Trailer Loading Package',
    long_description=open('README.md').read(),
    zip_safe=True,
)
