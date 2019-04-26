import ast
import re

import setuptools

from pluralize import __version__

setuptools.setup(
    name = "pluralize",
    version = __version__,
    url = 'https://github.com/web2py/pluralize',
    license = 'BSD',
    author = 'Massimo Di Pierro',
    author_email = 'massimo.dipierro@gmail.com',
    maintainer = 'Massimo Di Pierro',
    maintainer_email = 'massimo.dipierro@gmail.com',
    description = 'i18n + pluralization library with multi-plural form support and thread safe for web',
    long_description = "Yet another internationalizaton and pluralization library designed for efficiency and concurrency",
    long_description_content_type = "text/markdown",
    packages = ['pluralize'],
    include_package_data = True,
    zip_safe = False,
    platforms = 'any',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML'
    ],
)
