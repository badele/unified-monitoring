#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

from umonitoring import __version__

setup(
    name = 'umonitoring',
    version = __version__,
    description = 'Framework for ',
    author = 'Bruno Adelé',
    author_email = 'bruno@adele.im',
    url = 'http://github.com/badele/unified-monitoring',
    packages = ['umonitoring'],
    classifiers = [
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
