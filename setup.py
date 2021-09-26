from sa._version import __version__
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Source Assist",
    version=__version__,
    author="Kyle Petryszak",
    author_email="",
    description="A DevOps automation tool for incrementing version numbers and git repo management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/projectinitiative/SourceAssist",
    project_urls={"Bug Tracker": "https://github.com/projectinitiative/SourceAssist/issues",},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    install_requires=[
        "gitpython",
        "docker"
    ],
    python_requires=">=3.6",
    entry_points={"console_scripts": ["sa = sa.source_assist:main",],},
)
