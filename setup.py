from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='blynklib',
    version='0.1.1',
    description='Blynk Python/Micropython library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/blynkkk/lib-python',
    license='MIT',
    author='Anton Morozenko',
    author_email='antoha.ua@gmail.com',
    setup_requires=['pytest-runner', ],
    tests_require=['pytest', 'pytest-mock', ],
    py_modules=['blynklib'],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
