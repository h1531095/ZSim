from setuptools import setup, Extension

module = Extension(
    'LinkedList',
    sources=[r'.\\data_struct\\LinkedList.c'],
)

setup(
    name='LinkedList',
    version='1.0',
    description='A simple linked list extension module',
    ext_modules=[module],
)