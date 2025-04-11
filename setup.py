"""Setup script for the Bowens Island Private Parties connector."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bowens-island-private-parties",
    version="0.1.0",
    author="Lucas Barber",
    author_email="lucas@example.com",
    description="Python connector for syncing Bowens Island Private Party data between Cognito Forms and Excel",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lucasbarber78/bowens-island-private-parties",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "openpyxl>=3.1.2",
        "pandas>=2.1.0",
        "pyyaml>=6.0.1",
        "pydantic>=2.4.2",
    ],
    extras_require={
        "gui": ["tkinter>=8.6"],
        "excel": ["xlwings>=0.30.8"],
        "dev": [
            "pytest>=7.4.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "pre-commit>=3.3.3",
        ],
    },
    entry_points={
        "console_scripts": [
            "bowens-sync=src.__main__:main",
        ],
    },
)
