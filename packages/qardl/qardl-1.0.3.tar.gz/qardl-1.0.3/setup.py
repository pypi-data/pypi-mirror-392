from setuptools import setup, find_packages
import os

def read_file(filename):
    """Read file content"""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

setup(
    name='qardl',
    version='1.0.3',
    author='Dr. Merwan Roudane',
    author_email='merwanroudane920@gmail.com',
    description='Quantile Autoregressive Distributed Lag (QARDL) Models - Cho, Kim & Shin (2015)',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/merwanroudane/qardl',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Office/Business :: Financial',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'numpy>=1.20.0',
        'scipy>=1.7.0',
        'pandas>=1.3.0',
        'statsmodels>=0.13.0',
        'matplotlib>=3.4.0',
        'seaborn>=0.11.0',
    ],
    keywords='econometrics quantile-regression ARDL cointegration time-series',
    project_urls={
        'Documentation': 'https://github.com/merwanroudane/qardl',
        'Source': 'https://github.com/merwanroudane/qardl',
        'Bug Reports': 'https://github.com/merwanroudane/qardl/issues',
    },
    include_package_data=True,
    zip_safe=False,
)
