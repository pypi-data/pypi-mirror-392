"""Setup script for dropcountr-py package."""

from setuptools import setup, find_packages
from pathlib import Path

# Get the directory containing setup.py
here = Path(__file__).parent.resolve()

# Read the long description from README
long_description = (here / "README.md").read_text(encoding="utf-8")

# Define dependencies directly (more reliable than reading requirements.txt)
requirements = [
    "httpx>=0.24.0",
    "uritemplate>=4.1.1",
    "python-dotenv>=1.0.0",
]

setup(
    name="dropcountr-py",
    version="0.1.0",
    license="MIT",
    author="Aravind Murali",
    author_email="thearavindmurali@gmail.com",
    description="A Python client library for the Dropcountr API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/m-arav/dropcountr-py",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    keywords="dropcountr api client water usage",
)

