"""
Setup configuration for Sports AI Bettor.
Enterprise-grade sports betting prediction system with ML models.
"""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

# ============================================================================
# PROJECT METADATA & PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.resolve()
VERSION_FILE = PROJECT_ROOT / "sports_ai_bettor" / "__version__.py"
README_FILE = PROJECT_ROOT / "README.md"
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"

# ============================================================================
# VERSION MANAGEMENT
# ============================================================================

def get_version():
    """Extract version from __version__.py or setup.py fallback."""
    try:
        if VERSION_FILE.exists():
            version_dict = {}
            with open(VERSION_FILE, 'r', encoding='utf-8') as f:
                exec(f.read(), version_dict)
            return version_dict.get('__version__', '1.0.1')
    except Exception:
        pass
    return "1.0.1"  # Fallback version


def get_long_description():
    """Safely read long description from README."""
    try:
        if README_FILE.exists():
            return README_FILE.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Warning: Could not read README: {e}", file=sys.stderr)
    return "AI-powered sports betting predictions system"


def get_requirements(requirements_file=None):
    """Parse requirements from requirements.txt or fallback to inline list."""
    if requirements_file and Path(requirements_file).exists():
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                return [
                    line.strip() 
                    for line in f 
                    if line.strip() and not line.startswith('#')
                ]
        except Exception as e:
            print(f"Warning: Could not read {requirements_file}: {e}", file=sys.stderr)
    
    # Fallback to inline requirements
    return [
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
    ]


# ============================================================================
# PLATFORM-SPECIFIC DEPENDENCIES
# ============================================================================

install_requires = get_requirements(REQUIREMENTS_FILE)

# Platform-specific packages
if sys.platform == 'darwin':  # macOS
    pass  # No special requirements for macOS

elif sys.platform.startswith('linux'):  # Linux
    pass  # No special requirements for Linux

elif sys.platform == 'win32':  # Windows
    pass  # No special requirements for Windows


# ============================================================================
# PACKAGE DATA & DISCOVERY
# ============================================================================

# Discover all packages
packages = find_packages(
    exclude=['tests', 'tests.*', 'docs', '*.tests', 'build', 'dist']
)

# Package data to include
package_data = {
    'sports_ai_bettor': [
        'config/*.py',
        'src/*.py',
        'models/.gitkeep',
        'logs/.gitkeep',
        'data/.gitkeep',
    ],
}


# ============================================================================
# SETUP CONFIGURATION
# ============================================================================

setup(
    # ========================================================================
    # BASIC METADATA
    # ========================================================================
    name="sports-ai-bettor",
    version=get_version(),
    description="AI-powered sports betting predictions with value bet analysis",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    
    # ========================================================================
    # AUTHOR & REPOSITORY INFORMATION
    # ========================================================================
    author="Monsterx411",
    author_email="monsterx411@users.noreply.github.com",
    maintainer="Monsterx411",
    maintainer_email="monsterx411@users.noreply.github.com",
    
    # ========================================================================
    # PROJECT URLs
    # ========================================================================
    url="https://github.com/Monsterx411/sports-ai-bettor",
    project_urls={
        "Bug Tracker": "https://github.com/Monsterx411/sports-ai-bettor/issues",
        "Documentation": "https://github.com/Monsterx411/sports-ai-bettor#readme",
        "Source Code": "https://github.com/Monsterx411/sports-ai-bettor",
        "Changelog": "https://github.com/Monsterx411/sports-ai-bettor/releases",
    },
    
    # ========================================================================
    # LICENSE & KEYWORDS
    # ========================================================================
    license="MIT",
    keywords=[
        "sports",
        "betting",
        "machine-learning",
        "ai",
        "predictions",
        "soccer",
        "football",
        "value-betting",
        "sports-analytics",
    ],
    
    # ========================================================================
    # PACKAGE CONFIGURATION
    # ========================================================================
    packages=packages,
    package_data=package_data,
    include_package_data=True,
    python_requires=">=3.8,<4.0",
    
    # ========================================================================
    # DEPENDENCIES
    # ========================================================================
    install_requires=install_requires,
    
    extras_require={
        # Core data science & visualization
        "viz": [
            "plotly>=5.17.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
        ],
        
        # Development tools
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-xdist>=3.3.0",
            "black>=23.9.0",
            "flake8>=6.0.0",
            "pylint>=2.17.0",
            "mypy>=1.5.0",
            "isort>=5.12.0",
        ],
        
        # Documentation
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
            "sphinx-autodoc-typehints>=1.24.0",
        ],
        
        # Testing with coverage
        "test": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-xdist>=3.3.0",
            "coverage[toml]>=7.3.0",
        ],
        
        # Production deployment
        "prod": [
            "gunicorn>=21.2.0",
            "python-dotenv>=1.0.0",
        ],
        
        # All extras
        "all": [
            "plotly>=5.17.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-xdist>=3.3.0",
            "black>=23.9.0",
            "flake8>=6.0.0",
            "pylint>=2.17.0",
            "mypy>=1.5.0",
            "isort>=5.12.0",
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
            "sphinx-autodoc-typehints>=1.24.0",
            "gunicorn>=21.2.0",
            "coverage[toml]>=7.3.0",
        ],
    },
    
    # ========================================================================
    # CONSOLE SCRIPTS & ENTRY POINTS
    # ========================================================================
    entry_points={
        "console_scripts": [
            # Using script wrapper approach for root-level cli_app.py
            "sports-ai-bettor=cli_app:cli",
            "sab=cli_app:cli",  # Shorthand alias
        ],
    },
    
    # Include root-level Python files
    py_modules=['cli_app', 'data_fetch', 'predictor', 'web_app'],
    
    # ========================================================================
    # CLASSIFIER METADATA
    # ========================================================================
    classifiers=[
        # Development Status
        "Development Status :: 4 - Beta",
        
        # Intended Audience
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        
        # Topics
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        
        # License
        "License :: OSI Approved :: MIT License",
        
        # Programming Language
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        
        # Natural Language
        "Natural Language :: English",
        
        # Operating System
        "Operating System :: OS Independent",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
    ],
    
    # ========================================================================
    # BUILD & TESTING OPTIONS
    # ========================================================================
    test_suite="tests",
    zip_safe=False,  # Don't install as zip for compatibility
    
    # ========================================================================
    # METADATA
    # ========================================================================
    download_url="https://github.com/Monsterx411/sports-ai-bettor/releases",
)