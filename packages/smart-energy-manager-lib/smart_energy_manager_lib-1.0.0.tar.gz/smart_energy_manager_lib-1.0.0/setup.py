from setuptools import setup, find_packages
import os

# Read the README file


def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()


setup(
    name='smart_energy-manager_lib',
    version='1.0.0',
    author='Tejas Patil',
    author_email='20104123tejaspatil@gmail.com',
    description='A library for managing solar energy generation, consumption, and trading',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/x24250511/energy-manager',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='energy management solar renewable sustainability',
    python_requires='>=3.8',
    install_requires=[
        # No external dependencies - pure Python!
    ],
    extras_require={
        'dev': [
            'pytest>=7.0',
            'pytest-cov>=4.0',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/energy-manager/issues',
        'Source': 'https://github.com/yourusername/energy-manager',
    },
)
