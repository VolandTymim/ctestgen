from setuptools import setup, find_packages
import ctestgen

with open('README.md', 'r') as readme_file:
    long_description = readme_file.read()

setup(
    name='ctestgen',
    version=ctestgen.__version__,
    author='Vasilkin Vladislav',
    author_email='volandtymim@gmail.com',
    description='https://github.com/VolandTymim/ctestgen',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/VolandTymim/ctestgen',
    keywords='python c code-generation code-generator autotesting',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
