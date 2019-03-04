from setuptools import setup, find_packages
from blynklib import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='blynklib',
    version=__version__,
    packages=find_packages(include='blynklib.py'),
    description='Blynk Python/Micropython library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/blynkkk/lib-python',
    license='MIT',
    author='Anton Morozenko',
    author_email='antoha.ua@gmail.com',
    setup_requires=['pytest-runner', ],
    tests_require=['pytest', ],
)
