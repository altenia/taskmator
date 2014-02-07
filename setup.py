from distutils.core import setup
from setuptools import find_packages

setup(
    name='Taskmator',
    version='0.1dev',
    author=u'Young Suk Ahn Park',
    author_email='ys.ahnpark@gmail.com',
    packages=['taskmator'],
    #packages=find_packages(),
    url='https://github.com/altenia/taskmator',
    license='MIT, see LICENCE.txt',
    description='Task automation framework',
    long_description=open('README.md').read(),
    include_package_data=True,
    install_requires=['mako'],
)