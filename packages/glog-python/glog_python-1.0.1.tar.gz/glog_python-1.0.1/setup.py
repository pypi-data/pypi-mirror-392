"""Setup script for glog package"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="glog-python",
    version="1.0.1",
    author="gw123",
    author_email="",
    description="Python logging library compatible with Go glog format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gw123/glog",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    keywords="logging glog structured-logging context-logging trace-id",
    project_urls={
        "Bug Reports": "https://github.com/gw123/glog/issues",
        "Source": "https://github.com/gw123/glog",
    },
)
