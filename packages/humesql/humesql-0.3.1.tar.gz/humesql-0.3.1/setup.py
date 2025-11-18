from pathlib import Path
from setuptools import setup, find_packages

here = Path(__file__).parent
readme = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="humesql",
    version="0.3.1",
    description="Natural language to SQL to JSON results using Gemini.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Nirajan Ghimire",
    author_email="nirajanghimire20@gmail.com",
    url="https://github.com/nirajang20/HumeSQL",
    project_urls={
        "Source": "https://github.com/nirajang20/HumeSQL",
    },
    packages=find_packages(include=("humesql", "humesql.*")),
    python_requires=">=3.9",
    install_requires=[
        "mysql-connector-python>=8.0.0",
        "google-genai>=0.3.0",  # adjust version as needed
    ],
    entry_points={
        "console_scripts": [
            "humesql=humesql.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries",
    ],
)
