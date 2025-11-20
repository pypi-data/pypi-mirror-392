"""
GaussBio3D: Multiscale Gauss Linking Integral Library for Biomolecular 3D Topology
GaussBio3D: 用于生物分子3D拓扑的多尺度高斯链接积分库
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gaussbio3d",
    version="0.1.1",
    author="Your Name",
    author_email="your.email@example.com",
    description="Multiscale Gauss Linking Integral Library for Biomolecular 3D Topology / 用于生物分子3D拓扑的多尺度高斯链接积分库",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/GaussBio3D",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.20.0",
        "biopython>=1.79",
        "rdkit-pypi>=2021.9.1",
        "tqdm>=4.66",
    ],
    extras_require={
        "jit": [
            "numba>=0.56",
        ],
        "gpu": [
            "torch",
        ],
        "topology": [
            "ripser>=0.6",
        ],
        "all": [
            "numba>=0.56",
            "torch",
            "ripser>=0.6",
        ],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
)
