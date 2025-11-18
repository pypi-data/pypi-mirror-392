from setuptools import setup, find_packages

setup(
    name='starco-dj-utils',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='A Django pluggable app for telegram bot',
    author='Mojtaba',
    author_email='m.tahmasbi0111@yahoo.com',
    install_requires=[
        'Django>=4.0',
        'python-telegram-bot==22.5',
        'python-dotenv'
    ],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
    ],
)
