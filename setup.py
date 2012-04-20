# -*- coding: utf-8 -*-

from os import path
try:
    from setuptools import setup, find_packages
except:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

README_RST = path.join(path.dirname(__file__), 'README.rst')

setup(
    name = 'django-flatblocks',
    version = '0.7.0',
    description = 'django-flatblocks acts like django.contrib.flatpages but '
                  'for parts of a page; like an editable help box you want '
                  'show alongside the main content.',
    long_description = open(README_RST).read(),
    keywords = 'django apps',
    license = 'New BSD License',
    author = u'Armando Pérez (Horst Gutmann)',
    # author_email = 'zerok@zerokspot.com',
    url = 'http://github.com/mandx/django-flatblocks/',
    dependency_links = [],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages = find_packages(exclude=['ez_setup', 'test_project']),
    include_package_data = True,
    zip_safe = False,
)
