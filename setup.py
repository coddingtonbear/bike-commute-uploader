#!/usr/bin/python
import os
from setuptools import setup, find_packages
import uuid


requirements_path = os.path.join(
    os.path.dirname(__file__),
    'requirements.txt',
)
try:
    from pip.req import parse_requirements
    requirements = [
        str(req.req) for req in parse_requirements(
            requirements_path,
            session=uuid.uuid1()
        )
    ]
except ImportError:
    requirements = []
    with open(requirements_path, 'r') as in_:
        requirements = [
            req for req in in_.readlines()
            if not req.startswith('-')
            and not req.startswith('#')
        ]


setup_kwargs = {
    "name": "coddingtonbear-bike-commute-uploader",
    "version": "1.0",
    "description": (
        "Automatically upload GoPro videos from folder into Youtube."
    ),
    "author": "Adam Coddington",
    "author_email": "me@adamcoddington.net",
    "url": "https://github.com/coddingtonbear/bike-commute-uploader",
    "packages": find_packages(),
    "license": "GNU Public License v3.0",
    "classifiers": [
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    "install_requires": requirements,
    "entry_points": {
        'console_scripts': [
            'bike-commute-uploader = bike_commute_uploader.cmdline:main'
        ],
    }
}

setup(**setup_kwargs)
