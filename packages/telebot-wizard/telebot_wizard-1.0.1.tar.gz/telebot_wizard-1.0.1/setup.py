"""
TeleBot Wizard - Setup Configuration
TeleBot uchun zero-code bot builder kutubxonasi.
Author: Yoqubov javohir
Version: 1.0.0
License: MIT
"""

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

requirements = [
    "pyTelegramBotAPI>=4.0.0",
]

test_requirements = [
    "pytest>=6.0.0",
    "pytest-cov>=2.0.0",
    "black>=21.0.0",
    "flake8>=3.9.0",
    "mypy>=0.910",
]

setup(
    name="telebot-wizard",
    version="1.0.1",
    author="Yoqubov Javohir",
    author_email="rakuzenuz@gmail.com",
    description="Zero-Code Telegram Bot Builder for TeleBot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://t.em/UzMaxBoy",
    project_urls={
        "Bug Tracker": "https://t.me/UzMaxBoy",
        "Documentation": "https://t.me/UzMaxBoy",
        "Source Code": "https://t.me/UzMaxBoy",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Topic :: Communications :: Chat',
        "Topic :: Communications :: Internet Phone",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": test_requirements,
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "telebot-wizard=telebot_wizard.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="Telegram bot telebot zero-code builder",
    platforms="any",
)