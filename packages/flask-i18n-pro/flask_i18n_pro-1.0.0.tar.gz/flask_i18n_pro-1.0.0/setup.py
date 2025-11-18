"""Setup configuration for Flask-I18N-Pro."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="flask-i18n-pro",
    version="1.0.0",
    author="wallmarkets Team",
    author_email="team@wallmarkets.store",
    description="Production-grade i18n for Flask with Cyrillic and Asian language support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wallmarkets/flask-i18n-pro",
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
        "Topic :: Software Development :: Internationalization",
        "Natural Language :: English",
        "Natural Language :: Russian",
        "Natural Language :: Chinese (Simplified)",
    ],
    python_requires=">=3.7",
    install_requires=[
        "Flask>=2.0.0",
        "Flask-Babel>=2.0.0",
        "Babel>=2.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    keywords="flask i18n internationalization localization babel cyrillic russian mongolian chinese translation",
    project_urls={
        "Bug Reports": "https://github.com/wallmarkets/flask-i18n-pro/issues",
        "Source": "https://github.com/wallmarkets/flask-i18n-pro",
        "Documentation": "https://github.com/wallmarkets/flask-i18n-pro#readme",
    },
)
