from setuptools import setup, find_packages

setup(
    name='abcdWrangler',
    version='0.0.1',
    author='Katie Bottenhorn',
    description='A package for wrangling ABCD Study data, for various data science tasks.',
    packages=find_packages(),
    install_requires=[
        'pandas >=1.5.3',
        'numpy >=1.20.3',
        'nilearn >=0.8.1',
        'matplotlib >=3.5.2',
        'seaborn >=0.12.2'
        ],
    include_package_data=True
)