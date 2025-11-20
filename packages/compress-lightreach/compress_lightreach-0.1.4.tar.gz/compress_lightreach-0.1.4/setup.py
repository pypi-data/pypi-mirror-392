"""Setup script for compress-lightreach package."""

from setuptools import setup, find_packages
import os

# Get backend directory (parent of pypi folder where this file is located)
# Use realpath to follow symlinks to the actual file location
SETUP_DIR = os.path.dirname(os.path.realpath(__file__))

# Determine backend directory - handle both development and build scenarios
# In development: setup.py is in backend/pypi/, so backend is parent
# In build: setup.py might be in temp_dir/pypi/ or temp_dir/, README.md is in temp_dir/
# When building from sdist, setup.py might be copied to the root of the temp directory
if os.path.basename(SETUP_DIR) == "pypi":
    BACKEND_DIR = os.path.dirname(SETUP_DIR)  # Go up one level from pypi/ to backend/
elif os.path.exists(os.path.join(SETUP_DIR, "README.md")):
    # If README.md is in the same directory as setup.py, we're in the root
    BACKEND_DIR = SETUP_DIR
elif os.path.exists(os.path.join(os.path.dirname(SETUP_DIR), "README.md")):
    # If README.md is one level up, go up one level
    BACKEND_DIR = os.path.dirname(SETUP_DIR)
else:
    # Fallback: assume we're in the backend/ or build root
    BACKEND_DIR = SETUP_DIR

# Read README for long description - try multiple possible locations
# Handle both development (backend/pypi/) and build (temp_dir/ or temp_dir/pypi/) scenarios
readme_candidates = [
    os.path.join(BACKEND_DIR, "README.md"),  # Standard location (backend/ or temp root)
    os.path.join(os.path.dirname(SETUP_DIR), "README.md"),  # Parent of setup.py dir
    os.path.join(SETUP_DIR, "README.md"),    # Same dir as setup.py (fallback)
    os.path.join(SETUP_DIR, "..", "README.md"),  # One level up from setup.py
]

readme_path = None
for candidate in readme_candidates:
    if os.path.exists(candidate):
        readme_path = candidate
        break

if readme_path is None:
    raise FileNotFoundError(f"README.md not found. Tried: {readme_candidates}")

with open(readme_path, "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version from _version.py - try multiple possible locations
def get_version():
    version_candidates = [
        os.path.join(BACKEND_DIR, "pcompresslr", "_version.py"),  # Standard location
        os.path.join(SETUP_DIR, "..", "pcompresslr", "_version.py"),  # Relative from pypi/
        os.path.join(os.path.dirname(SETUP_DIR), "pcompresslr", "_version.py"),  # From parent
    ]
    
    for version_file in version_candidates:
        version_file = os.path.normpath(version_file)
        if os.path.exists(version_file):
            with open(version_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("__version__"):
                        return line.split("=")[1].strip().strip('"').strip("'")
    
    return "0.1.0"

setup(
    name="compress-lightreach",
    version=get_version(),
    author="Light Reach",
    author_email="jonathankt@lightreach.io",
    description="Intelligent compression algorithms for LLM prompts that reduce token usage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://compress.lightreach.io",
    project_urls={
        "Homepage": "https://compress.lightreach.io",
        "Documentation": "https://compress.lightreach.io/docs",
        "Source": "https://github.com/lightreach/compress-lightreach",
        "Bug Tracker": "https://github.com/lightreach/compress-lightreach/issues",
    },
    packages=find_packages(exclude=["tests", "scripts", "api", "compressors", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "tiktoken>=0.5.0",
        "requests>=2.31.0",
        "urllib3>=2.0.0",
    ],
    include_package_data=True,
    extras_require={
        "api": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "pydantic>=2.0.0",
            "python-multipart>=0.0.6",
        ],
    },
    entry_points={
        "console_scripts": [
            "pcompresslr=pcompresslr.cli:main",
        ],
    },
)

