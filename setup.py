# The following comment should be removed at some point in the future.
# mypy: disallow-untyped-defs=False

import codecs
import os
import sys

from setuptools import find_packages, setup


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

long_description = read('README.rst')

setup(
    name="trystatic",
    version="1.0.0",
    description="trystatic",
    long_description=long_description,

    license='MIT',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python",
    ],
    url='https://github.com/insilications/trystatic-clr',
    keywords='trystatic',
    project_urls={
        "Source": "https://github.com/insilications/trystatic-clr",
    },

    author='insilications',
    author_email='boboniboni@gmail.com',

    package_dir={"": "src"},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "trystatic=trystatic.__main__:main",
        ],
    },
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
)
