from setuptools import setup, find_packages

setup(
    name="r2d2",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
      'console_scripts': [
        'r2d2=r2d2.main',
      ],
    },
)