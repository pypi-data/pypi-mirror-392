"""
OPERA - Operadic Pattern Discovery and Verification
MCP server for discovering, quarantining, and goldenizing workflow patterns
"""
from setuptools import setup, find_packages

setup(
    name='opera-mcp',
    version='0.1.0',
    description='OPERA - Operadic pattern discovery and verification system',
    author='Isaac',
    packages=find_packages(),
    install_requires=[
        'fastmcp>=2.0.0',
        'heaven-framework>=0.1.0',
    ],
    entry_points={
        'console_scripts': [
            'opera-server=opera.opera_mcp:main',
        ],
    },
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='mcp ai patterns opera operadic starsystem',
)
