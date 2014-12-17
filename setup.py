#!/usr/bin/env python

from setuptools import setup

from pip.req import parse_requirements
install_reqs = parse_requirements('requirements.txt')

setup(name='Configify',
      version='0.0.1',
      description='Templated output, from templated context parameters',
      author='Ricky Cook',
      author_email='mail@thatpanda.com',
      url='https://github.com/RickyCook/configify',
      py_modules=['configify'],
      scripts=['configify'],
      install_requires=[str(pip_req.req) for pip_req in install_reqs],
     )
