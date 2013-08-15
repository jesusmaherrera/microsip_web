import os
from setuptools import setup
# this grabs the requirements from requirements.txt
REQUIREMENTS = [i.strip() for i in open("requirements/common.txt").readlines()]
# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
setup(
    install_requires=REQUIREMENTS
)