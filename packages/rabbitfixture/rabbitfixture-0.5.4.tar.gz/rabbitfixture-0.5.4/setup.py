import codecs
import os

from setuptools import setup, find_packages


HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """Return the contents of the read file.

    - Build an absolute path from *parts*
    - Return the contents of the resulting file.
    - Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()


LONG = read("README.rst") + "\n\n" + read("NEWS.rst")

install_requires = [
    "amqp >= 2.0.0",
    "fixtures >= 0.3.6",
    "setuptools",
    'subprocess32; python_version < "3"',
    "testtools >= 0.9.12",
]

setup(
    name="rabbitfixture",
    version="0.5.4",
    packages=find_packages("."),
    package_dir={"": "."},
    include_package_data=True,
    zip_safe=False,
    author="Launchpad developers",
    maintainer="Launchpad developers",
    description=open("README.rst").readline().strip(),
    long_description=LONG,
    long_description_content_type="text/x-rst",
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <3.8",
    install_requires=install_requires,
    url="https://launchpad.net/rabbitfixture",
    project_urls={
        "Source": "https://code.launchpad.net/rabbitfixture",
        "Issue Tracker": "https://bugs.launchpad.net/rabbitfixture",
    },
    license="AGPL-3.0-only",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    extras_require={
        "test": [
            "six",
        ],
    },
)
