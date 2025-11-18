"""
Setup configuration for pier-os-clock package.
"""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pier-os-clock",
    version="1.0.0",
    py_modules=["pier_os_clock"],
    entry_points={
        "console_scripts": [
            "pier-os-clock=pier_os_clock:main",
        ],
    },
    author="Dogukan Sahil",
    author_email="dogukansahil@protonmail.com",
    description="Minimal terminal clock tool for Linux/WSL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache-2.0",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Utilities",
    ],
    keywords="terminal clock tty cli linux",
)
