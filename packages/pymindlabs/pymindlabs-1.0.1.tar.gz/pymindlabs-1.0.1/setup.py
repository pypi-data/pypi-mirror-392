from setuptools import find_packages
from setuptools import setup
import os

root_path = os.path.dirname(__file__)
require = open(os.path.join(root_path, 'requirements.txt')).readlines()

setup(
    name='pymindlabs',
    version='1.0.1',
    url='https://github.com/housenli/pyMIND',
    description='Python implementation of Multiscale Nemirovski Dantzig Estimators',
    packages=find_packages(),
    package_dir={'pymindlabs': 'pymindlabs'},
    author={'Leo Claus Weber', 'Housen Li'},
    install_requires=[require]
)
