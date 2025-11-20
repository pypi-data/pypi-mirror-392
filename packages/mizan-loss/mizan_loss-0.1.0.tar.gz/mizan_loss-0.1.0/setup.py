from setuptools import setup, find_packages

setup(
    name='mizan-loss',
    version='0.1.0',
    description='Mizan Balance Function: scale-invariant loss & similarity metric',
    author='Ahsan Shaokat',
    license='MIT',
    packages=find_packages(),
    install_requires=['torch'],
)