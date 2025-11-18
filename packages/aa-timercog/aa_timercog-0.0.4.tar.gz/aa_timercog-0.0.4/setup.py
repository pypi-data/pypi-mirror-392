import re
from pathlib import Path

from setuptools import find_packages, setup


def get_version():
    """Read version from timercog/__init__.py without importing it."""
    version_file = Path(__file__).parent / "timercog" / "__init__.py"
    version_content = version_file.read_text(encoding="utf-8")
    version_match = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        version_content,
        re.MULTILINE,
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def get_long_description():
    """Read the README.md file."""
    readme_file = Path(__file__).parent / "README.md"
    return readme_file.read_text(encoding="utf-8")


setup(
    name="aa-timercog",
    version=get_version(),
    author="crazydisi",
    author_email="crazydisiofficial@gmail.com",
    description="Discord bot command extension for aa-structuretimers",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/aa-timercog",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "allianceauth>=4.0.0",
        "allianceauth-discordbot>=3.0.0",
        "aa-structuretimers>=1.0.0",
        "py-cord>=2.0.0",
    ],
    extras_require={
        "dev": [
            "black>=24.0.0",
            "flake8>=7.0.0",
            "isort>=5.13.0",
            "pytest>=8.0.0",
            "pytest-django>=4.7.0",
            "pytest-cov>=4.1.0",
        ],
    },
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
