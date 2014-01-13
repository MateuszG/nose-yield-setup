import sys
try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass

from setuptools import setup

setup(
    name='Yield With SetUp',
    version='0.1',
    author='Mateusz Galganek',
    author_email = 'galganek.mateusz@gmail.com',
    description = 'Run setUp on generators and display full path in output during test',
    license = 'GNU LGPL',
    py_modules = ['yield'],
    entry_points = {
        'nose.plugins.0.10': [
            'yield = yield:YieldWithSetUp'
            ]
        }

    )
