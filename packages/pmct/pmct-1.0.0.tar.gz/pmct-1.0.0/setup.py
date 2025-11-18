"""
Setup configuration for pmct package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_long_description():
    here = os.path.abspath(os.path.dirname(__file__))
    readme_path = os.path.join(here, 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

setup(
    name='pmct',
    version='1.0.0',
    author='Dr. Merwan Roudane',
    author_email='merwanroudane920@gmail.com',
    description='Python Module for Cointegration Tests with Two Endogenous Structural Breaks',
    long_description=read_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/merwanroudane/pmct',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    keywords='cointegration econometrics time-series structural-breaks unit-root',
    python_requires='>=3.7',
    install_requires=[
        'numpy>=1.19.0',
        'pandas>=1.1.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.10',
            'sphinx>=3.0',
            'black>=20.0',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/merwanroudane/pmct/issues',
        'Source': 'https://github.com/merwanroudane/pmct',
        'Documentation': 'https://github.com/merwanroudane/pmct#readme',
    },
    license='GPL-3.0',
    include_package_data=True,
)
