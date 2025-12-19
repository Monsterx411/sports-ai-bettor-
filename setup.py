"""Setup configuration for Sports AI Bettor."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8") if (this_directory / "README.md").exists() else ""

setup(
    name="sports-ai-bettor",
    version="1.0.0",
    description="AI-powered sports betting predictions with value bet analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Sports AI Bettor Team",
    author_email="your@email.com",
    url="https://github.com/yourusername/sports-ai-bettor",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "requests>=2.31.0",
        "urllib3>=2.0.0",
        "click>=8.1.0",
        "streamlit>=1.28.0",
        "plotly>=5.17.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "python-dotenv>=1.0.0",
        "pytz>=2023.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.9.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "sports-ai-bettor=cli_app:cli",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
