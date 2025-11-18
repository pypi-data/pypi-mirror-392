"""Setup configuration for Flask-SuperCache."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="flask-supercache",
    version="1.0.0",
    author="wallmarkets Team",
    author_email="team@wallmarkets.store",
    description="A 3-tier caching system for Flask with zero external dependencies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wallmarkets/flask-supercache",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Flask",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.7",
    install_requires=[
        "Flask>=2.0.0",
        "flask-caching>=1.10.0",
    ],
    extras_require={
        "redis": ["redis>=3.5.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
    keywords="flask cache caching redis lru ttl performance",
    project_urls={
        "Bug Reports": "https://github.com/wallmarkets/flask-supercache/issues",
        "Source": "https://github.com/wallmarkets/flask-supercache",
        "Documentation": "https://github.com/wallmarkets/flask-supercache#readme",
    },
)
