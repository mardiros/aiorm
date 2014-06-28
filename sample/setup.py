import os
import re

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
NAME = 'sample'
README = ''
CHANGES = ''

VERSION = '0.0'

requires = []


setup(name=NAME,
      version=VERSION,
      description='sample',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        ],
      author='Guillaume Gauvrit',
      author_email='guillaume@gauvr.it',
      url='',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      # test_suite=NAME,
      install_requires=requires,
      )
