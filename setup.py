import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-easy-timezones',
    version='0.8.0',
    packages=find_packages(),
    include_package_data=True,
    license='Apache License',
    description='Easy timezones for Django based on MaxMind GeoIP2.',
    long_description=README,
    url='https://github.com/vivazzi/django-easy-timezones',
    author='Rich Jones',
    author_email='rich@openwatch.net',
    maintainer='Artem Maltsev',
    maintainer_email='maltsev.artjom@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'django>=2.0.0',
    ],
)
