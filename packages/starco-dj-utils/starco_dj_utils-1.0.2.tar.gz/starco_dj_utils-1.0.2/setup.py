
from setuptools import setup, find_packages

setup(
    name='starco-dj-utils',
    version='1.0.2',
    packages=['dj_utils'],
    include_package_data=True,
    license='MIT',
    description='A Django pluggable app for utilities and database management',
    author='Mojtaba',
    author_email='m.tahmasbi0111@yahoo.com',
    install_requires=[
        'Django>=4.0',
    ],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
    ],
)
