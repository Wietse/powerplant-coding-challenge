import sys
from setuptools import setup, find_packages


packages = find_packages('src')

setup(
    name='pcc',
    version=f'0.1.0',
    url='https://github.com/Wietse/powerplant-coding-challenge',
    license='MIT',
    description='powerplant-coding-challenge',
    author='wietse.j@gmail.com',
    package_dir={'': 'src'},
    packages=packages,
    # entry_points={
    #    'console_scripts': [],
    # },
)
