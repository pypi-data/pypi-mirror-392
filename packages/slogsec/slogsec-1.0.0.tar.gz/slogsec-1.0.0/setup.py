from setuptools import setup,find_packages
import sys
 
includeFiles = ["*"]
setup(
    
    name="slogsec",
    version="1.0.0",
    description="The Perfect Fusion of Beauty & Security",
    long_description=open("README.md", "r", encoding="utf-8").read(),   
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={
        'slogsec': includeFiles, 
    }, 
    install_requires=[ 
        'logcrypt>=1.0.0',
        'colorlog>=3.0.0'
    ],
    include_package_data=True, 
    license='Apache License 2.0',
    author="ciaorama",
    author_email="ciaorama@tutamail.com"
)

