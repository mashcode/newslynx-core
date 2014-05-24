from setuptools import setup, find_packages
from pip.req import parse_requirements

# install_reqs = [
#   str(ir.req) for ir in parse_requirements('requirements.txt')
#   ] 

setup(
  name='newslynx-core',
  version='0.0.1',
  description="",
  long_description="",
  classifiers=[
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    ],
  keywords='',
  author='Brian Abelson, Stijn Debrouwere, Michael Keller',
  author_email='brian@newslynx.org, stijn@newslynx.org, michael@newslynx.org',
  url='http://github.com/newslynx/newslynx-core',
  license='MIT',
  packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
  namespace_packages=[],
  include_package_data=False,
  zip_safe=False,
  install_requires=[],
  tests_require=[],
  entry_points = {
    'console_scripts': [
          'nlc = newslynx_core:cli.cli'
    ]
  }
)
