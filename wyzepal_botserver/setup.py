#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
if False:
    from typing import Any, Dict, Optional

WYZEPAL_BOTSERVER_VERSION = "0.5.9"

# We should be installable with either setuptools or distutils.
package_info = dict(
    name='wyzepal_botserver',
    version=WYZEPAL_BOTSERVER_VERSION,
    description='WyzePal\'s Flask server for running bots',
    author='WyzePal Open Source Project',
    author_email='wyzepal-devel@googlegroups.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Communications :: Chat',
    ],
    url='https://www.wyzepal.com/',
    entry_points={
        'console_scripts': [
            'wyzepal-botserver=wyzepal_botserver.server:main',
        ],
    },
    test_suite='tests',
)  # type: Dict[str, Any]

setuptools_info = dict(
    install_requires=[
        'wyzepal',
        'wyzepal_bots',
        'flask>=0.12.2',
    ],
)

try:
    from setuptools import setup, find_packages
    package_info.update(setuptools_info)
    package_info['packages'] = find_packages(exclude=['tests'])

except ImportError:
    from distutils.core import setup
    from distutils.version import LooseVersion
    from importlib import import_module

    # Manual dependency check
    def check_dependency_manually(module_name, version=None):
        # type: (str, Optional[str]) -> None
        try:
            module = import_module(module_name)  # type: Any
            if version is not None:
                assert(LooseVersion(module.__version__) >= LooseVersion(version))
        except (ImportError, AssertionError):
            if version is not None:
                print("{name}>={version} is not installed.".format(
                    name=module_name, version=version), file=sys.stderr)
            else:
                print("{name} is not installed.".format(name=module_name), file=sys.stderr)
            sys.exit(1)

    check_dependency_manually('wyzepal')
    check_dependency_manually('wyzepal_bots')
    check_dependency_manually('flask', '0.12.2')

    package_info['packages'] = ['wyzepal_botserver']


setup(**package_info)
