#!/usr/bin/env python
# -*-coding:utf-8-*-

import setuptools
import os
import sys
import shutil
import platform
from pathlib import Path

# Read README file
long_description = ""
readme_path = Path(__file__).parent.parent / 'README.md'
try:
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()
except Exception as e:
    print(f"Warning: Could not read README.md: {e}")
    long_description = ""
      


# Ensure source files exist
src_dir = Path(__file__).parent / "src"

# For source distributions, src should already be included via MANIFEST.in
if not src_dir.is_dir():
    # Try to copy from parent directory (for development builds)
    parent_src_dir = Path(__file__).parent.parent / "src"
    if parent_src_dir.is_dir():
        print(f"Copying source files from {parent_src_dir} to {src_dir}")
        shutil.copytree(parent_src_dir, src_dir)
    else:
        raise RuntimeError(
            "Source directory 'src' not found. "
            "This package requires C++ source files to build. "
            "Please ensure the source distribution includes the src/ directory."
        )

# Compiler flags
extra_compile_args = []
extra_link_args = []

if platform.system() == 'Windows':
    extra_compile_args.append("/utf-8")
else:
    extra_compile_args.append('-std=c++11')
    # macOS M1/ARM64 specific flags
    if platform.system() == 'Darwin' and platform.machine() == 'arm64':
        extra_compile_args.extend(['-arch', 'arm64'])
        extra_link_args.extend(['-arch', 'arm64'])


sxtwl_module = setuptools.Extension(
    '_sxtwl',
    include_dirs=['src'],
    sources=[
        'sxtwl_wrap.cxx',
        'src/eph.cpp',
        'src/JD.cpp',
        'src/SSQ.cpp',
        'src/lunar.cpp',
    ],
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
    language='c++'
)


setuptools.setup(
    name="sxtwl-modern",
    version="1.1.2",
    author="yuangu",
    author_email="lifulinghan@aol.com",
    description="Sxtwl_cpp wrapper for Python - Chinese Lunar Calendar Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="BSD",
    url="https://github.com/SIC98/sxtwl",
    ext_modules=[sxtwl_module],
    py_modules=["sxtwl"],
    python_requires='>=3.8',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: C++",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
