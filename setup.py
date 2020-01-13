import sys

try:
    # noinspection PyUnresolvedReferences
    from setuptools import setup
except ImportError:
    print("Test result reporter now needs setuptools in order to build. Install it using"
          " your package manager (usually python-setuptools) or via pip (pip"
          " install setuptools).")
    sys.exit(1)

__version__ = '0.0.3'
__author__ = 'dimorinny'

# noinspection PyBroadException
try:
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()
except Exception:
    requirements = []
    print("Error while parsing requirements file")

setup(
    name='git-synchronization',
    version=__version__,
    description='Synchronize all remotes branches to local ones',
    author=__author__,
    install_requires=requirements,
    author_email='didika914@gmail.com',
    package_dir={'synchronization': 'synchronization'},
    packages=['synchronization'],
    include_package_data=True,
    scripts=[
        'bin/git-synchronization',
    ],
)
