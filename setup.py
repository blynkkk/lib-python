from setuptools import setup, find_packages
from blynklib import __version__

setup(
    name='blynklib',
    version=__version__,
    packages=find_packages(include='blynklib.py'),
    url='https://github.com/blynkkk/lib-python',
    license='MIT',
    author='Anton Morozenko',
    author_email='',
    description='Blynk Python/Micropython library',
    setup_requires=['pytest-runner', ],
    tests_require=['pytest', ],
)
