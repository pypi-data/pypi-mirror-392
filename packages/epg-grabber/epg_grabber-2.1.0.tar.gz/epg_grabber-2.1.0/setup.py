# MIT License
#
# Copyright (c) 2025 Róbert Malovec
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from setuptools import setup, find_packages


with open("VERSIONS.txt") as changes:
    latest_version = changes.readline().split(',')[0]
    changes.seek(0)
    release_notes = f"## Release Notes\n\n{changes.read()}"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="epg-grabber",
    version=latest_version,
    author="Róbert Malovec",
    author_email="epg-grabber@malovec.sk",
    description="Czech TV EPG Grabber for XMLTV format with multi-source support",
    long_description=f"{long_description}\n\n{release_notes}",
    long_description_content_type="text/markdown",
    url="https://github.com/robco/czech-tv-epg-grabber",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Multimedia :: Video",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests",
        "tqdm",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "epg-grabber=epg_grabber.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "epg_grabber": ["*.json", "*.txt"],
    },
)
