#!/usr/bin/env python

from setuptools import setup

setup(
    name='Configify',
    version='0.0.2',
    description='Templated output, from templated context parameters',
    author='Ricky Cook',
    author_email='mail@thatpanda.com',
    url='https://github.com/RickyCook/configify',
    py_modules=['configify'],
    scripts=['configify'],
    install_requires=[
        'Jinja2==2.7.3',
        'MarkupSafe==0.23',
        'PyYAML==3.11',
    ],
 )
