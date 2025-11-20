from pathlib import Path
from setuptools import setup


version = "4.0.0a3"

long_description = (
    f"{Path('README.rst').read_text()}\n{Path('CHANGES.rst').read_text()}\n"
)

setup(
    name="plone.locking",
    version=version,
    description="webdav locking support",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.2",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 5",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="locking webdav plone",
    author="Plone Foundation",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://pypi.org/project/plone.locking",
    license="GPL version 2",
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    extras_require=dict(
        test=[
            "plone.app.contenttypes[test]",
            "plone.app.testing",
            "plone.dexterity",
            "plone.testing",
        ]
    ),
    install_requires=[
        "setuptools",
        "plone.base",
        "Zope",
    ],
)
