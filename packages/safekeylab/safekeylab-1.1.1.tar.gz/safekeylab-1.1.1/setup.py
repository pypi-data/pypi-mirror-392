"""
SafeKeyLab - Enterprise PII Detection and Data Protection
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="safekeylab",
    version="1.1.1",
    author="SafeKey Lab Inc.",
    author_email="team@safekeylab.com",
    description="Multimodal AI Privacy Shield - Enterprise PII detection across text, voice, images, video & documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/safekeylab/python-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.28.0",
        "colorama>=0.4.6",
        "tabulate>=0.9.0",
        "click>=8.1.0",
        "python-dotenv>=0.21.0",
        "tqdm>=4.65.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "safekeylab=safekeylab.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "safekeylab": ["data/*.json", "templates/*.txt"],
    },
)