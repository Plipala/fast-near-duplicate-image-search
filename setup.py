#!/usr/bin/env python
# coding: utf-8
# Package and distribution management.

from setuptools import setup, find_packages
import versioneer

with open('LICENSE') as f:
    license = f.read()

setup(
    name='deduplication',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Fast Near-Duplicate Image Search and Delete.',
    long_description='This Python script is a command line tool for visualizing, checking and deleting near-duplicate '
                     'images from the target directory.',
    author='Umberto Griffo',
    author_email='umberto.griffo@gmail.com',
    url='https://github.com/umbertogriffo/fast-near-duplicate-image-search',
    license=license,
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
    ],
    # include all packages under src
    packages=find_packages('src', exclude=["experiments", "*.tests", "*.tests.*", "tests.*", "tests"]),
    # tell distutils packages are under src
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        "certifi==2019.3.9"
        , "cycler==0.10.0"
        , "ImageHash==4.0"
        , "kiwisolver==1.0.1"
        , "matplotlib==3.0.3"
        , "mkl-fft==1.0.6"
        , "mkl-random==1.0.1.1"
        , "natsort==5.5.0"
        , "numpy==1.16.2"
        , "olefile==0.44"
        , "opencv-contrib-python==4.0.0.21"
        , "pandas==0.24.2"
        , "patsy==0.5.1"
        , "Pillow==6.0.0"
        , "pyparsing==2.4.0"
        , "python-dateutil==2.8.0"
        , "pytz==2019.1"
        , "PyWavelets==1.0.3"
        , "scikit-learn==0.20.3"
        , "scipy==1.2.1"
        , "seaborn==0.9.0"
        , "six==1.12.0"
        , "statsmodels==0.9.0"
        , "tornado==6.0.2"
        , "tqdm==4.31.1"
        , "versioneer==0.18"],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'deduplication = deduplication.__main__:main'
        ]
    }
)
