"""
FlagSwift Python SDK Setup
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="flagswift",
    version="1.1.0",
    author="FlagSwift Team",
    author_email="info@flagswift.com",
    description="Official Python SDK for FlagSwift feature flags",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/flagswift/flagswift-python",
    project_urls={
        "Bug Tracker": "https://github.com/flagswift/flagswift-python/issues",
        "Documentation": "https://docs.flagswift.com",
        "Source Code": "https://github.com/flagswift/flagswift-python",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
    keywords="feature-flags feature-toggles flagswift deployment",
)