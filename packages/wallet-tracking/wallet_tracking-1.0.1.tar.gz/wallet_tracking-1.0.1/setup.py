"""
Setup script for Wallet Tracking Package
A standalone Python package for Discord webhook integration.
This package is designed to be a compiled module - source code is hidden.
"""

from setuptools import setup, find_packages
import py_compile
import os
import shutil

# Compile Python files to bytecode for obfuscation
def compile_package():
    """Compile .py files to .pyc to hide source code."""
    package_dir = "wallet_tracking"
    if os.path.exists(package_dir):
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        py_compile.compile(file_path, doraise=True)
                    except py_compile.PyCompileError as e:
                        print(f"Warning: Could not compile {file_path}: {e}")

# Compile before building
compile_package()

setup(
    name="wallet-tracking",
    version="1.0.1",
    author="Private",
    author_email="",
    description="copy trading bot tracking",
    long_description="copy trading bot tracking",
    long_description_content_type="text/plain",
    url="",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
    ],
    include_package_data=True,
    zip_safe=True,  # Package can be installed as zip (hides source better)
)

