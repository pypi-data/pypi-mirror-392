from setuptools import setup,find_packages

setup(
    name='yapi',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'mcp==1.13.1',
        'requests==2.32.5'
    ],
)