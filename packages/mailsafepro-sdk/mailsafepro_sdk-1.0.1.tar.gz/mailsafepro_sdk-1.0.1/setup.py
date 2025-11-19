"""
Setup script for EmailValidator SDK
Fallback for environments that don't support Poetry
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mailsafepro-sdk",
    version="1.0.1",
    author="MailSafePro Team",
    author_email="support@mailsafepro.com",
    description="Official Python SDK for Email Validation API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mailsafepro/mailsafepro-python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/mailsafepro/mailsafepro-python-sdk/issues",
        "Documentation": "https://docs.mailsafepro.com/sdk/python",
        "Source Code": "https://github.com/mailsafepro/mailsafepro-python-sdk",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Email",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "urllib3>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
            "types-requests>=2.31.0",
        ],
    },
)
