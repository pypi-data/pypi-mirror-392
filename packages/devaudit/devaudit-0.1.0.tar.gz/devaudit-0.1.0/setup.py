"""
DevAudit - Developer Environment Auditing Tool
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="devaudit",
    version="0.1.0",
    author="John Doyle",
    author_email="john.doyle.mail@icloud.com",
    description="Cross-platform developer environment auditing and cleanup tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aramantos/devaudit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "rich>=13.7.0",
        "click>=8.1.0",
    ],
    entry_points={
        "console_scripts": [
            "devaudit=devaudit.cli:main",
        ],
    },
    keywords="audit dependencies docker python nodejs developer-tools devops",
    project_urls={
        "Bug Reports": "https://github.com/aramantos/devaudit/issues",
        "Source": "https://github.com/aramantos/devaudit",
    },
)
