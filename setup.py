import os
import re

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
NAME = 'aiorm'
with open(os.path.join(here, 'README.rst')) as readme:
    README = readme.read()
with open(os.path.join(here, 'CHANGES.rst')) as changes:
    CHANGES = changes.read()

with open(os.path.join(here, NAME, '__init__.py')) as version:
    VERSION = re.compile(r".*__version__ = '(.*?)'",
                         re.S).match(version.read()).group(1)


requires = ['venusian>=1.0a7', 'aiopg', 'zope.interface']
tests_require = ['coverage', 'nose']
extras_require = {'test': tests_require,
                  }

setup(name=NAME,
      version=VERSION,
      description='ORM for asyncio',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: BSD License',
        'Development Status :: 3 - Alpha',
        ],
      author='Guillaume Gauvrit',
      author_email='guillaume@gauvr.it',
      url='https://github.com/mardiros/aiorm',
      keywords='asyncio orm',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='{}.tests'.format(NAME),
      install_requires=requires,
      tests_require=tests_require,
      extras_require=extras_require,
      )
