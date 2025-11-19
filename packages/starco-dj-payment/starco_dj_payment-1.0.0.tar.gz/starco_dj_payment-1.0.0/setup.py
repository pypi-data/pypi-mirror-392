
from setuptools import setup, find_packages

setup(
    name='starco-dj-payment',
    version='1.0.0',
    packages=['dj_payment'],
    include_package_data=True,
    license='MIT',
    description='A Django pluggable app for payments.',
    author='Mojtaba',
    author_email='m.tahmasbi0111@yahoo.com',
    install_requires=[
        'Django>=4.0',
        'starco-dj-utils',
        'requests',
        'starco-utility==1.3.4'
    ],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
    ],
)
