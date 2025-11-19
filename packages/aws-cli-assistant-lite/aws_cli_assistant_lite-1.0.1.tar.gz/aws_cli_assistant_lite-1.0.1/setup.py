"""
AWS CLI Assistant - Lite Edition
Setup and installation configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ''

version = '1.0.1'

setup(
    name='aws-cli-assistant-lite',
    version=version,
    description='Natural language to AWS CLI converter with real-time validation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Malini Agrawal',
    author_email='aws2minutes@gmail.com',
    url='https://github.com/maliniagrawal/aws-cli-assistant-lite',
    license='Commercial',
    
    packages=find_packages(where='.'),
    package_dir={'': '.'},
    include_package_data=True,
    
    install_requires=[
        'fastmcp>=0.2.0',
        'pydantic>=2.12.0',
        'loguru>=0.7.0',
        'boto3>=1.40.0',
        'botocore>=1.40.0',
        'fastapi>=0.115.0',
        'uvicorn>=0.32.0',
        'transformers>=4.57.0',
        'torch>=2.5.0',
        'anthropic>=0.70.0',
        'python-dotenv>=1.2.0',
    ],
    
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
        ],
    },
    
    python_requires='>=3.10',
    
    entry_points={
        'console_scripts': [
            'aws-cli-assistant=aws_cli_assistant.mcp_server:main',
        ],
    },
    
    package_data={
        'aws_cli_assistant.config': ['defaults.json'],
    },
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)