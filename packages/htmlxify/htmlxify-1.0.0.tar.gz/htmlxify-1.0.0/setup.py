"""
Setup script for htmlxify - Web Markup Compiler
Allows installation via: pip install .
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme = Path('README.md')
long_description = readme.read_text(encoding='utf-8') if readme.exists() else ''

setup(
    name='htmlxify',
    version='1.0.0',
    description='htmlxify - A simplified web markup language compiler that transpiles to HTML, CSS, and JavaScript',
    long_description=long_description,
    long_description_content_type='text/markdown',
    
    author='Aquib489',
    author_email='aquib.gaming9@gmail.com',
    url='https://github.com/Aquib489/htmlxify',
    
    # Package discovery
    packages=find_packages(exclude=['tests', 'tests.*']),
    
    # Include non-Python files
    package_data={
        'htmlxify.parser': ['grammar.lark'],
    },
    
    # Dependencies
    install_requires=[
        'attrs==25.4.0',
        'black==23.12.1',
        'cattrs==25.3.0',
        'click==8.3.0',
        'colorama==0.4.6',
        'coverage==7.11.2',
        'cssbeautifier==1.15.4',
        'EditorConfig==0.17.1',
        'iniconfig==2.3.0',
        'jsbeautifier==1.15.4',
        'lark==1.1.9',
        'lsprotocol==2023.0.1',
        'mypy==1.7.1',
        'mypy_extensions==1.1.0',
        'packaging==25.0',
        'pathspec==0.12.1',
        'platformdirs==4.5.0',
        'pluggy==1.6.0',
        'pygls==1.3.0',
        'pytest==7.4.3',
        'pytest-cov==4.1.0',
        'six==1.17.0',
        'sourcemap==0.2.1',
        'tinycss2==1.2.1',
        'typing_extensions==4.15.0',
        'webencodings==0.5.1',
    ],
    
    # Command-line scripts
    entry_points={
        'console_scripts': [
            'htmlxify=htmlxify.cli:main',
        ],
    },
    
    # Metadata
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Compilers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    
    keywords='html compiler web markup transpiler htmlxify',
    
    python_requires='>=3.8',
    
    # License
    license='GPL-3.0',
)
