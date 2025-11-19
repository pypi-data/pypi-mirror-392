from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="qtom",
    version="1.0.2",
    description="Neural Network Quantum State Tomography Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Manuel A. Garcia & Johan Garzon",
    author_email="mangarciama@unal.edu.co",
    url="https://github.com/alhazacod/qtom",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    install_requires=[
        "numpy>=1.19.0",
        "tensorflow>=2.5.0",
        "keras>=2.5.0",
    ],
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'qtnn-train=qtom.cli.train:main',
            'qtnn-evaluate=qtom.cli.evaluate:main',
            'qtnn-generate-data=qtom.cli.generate_data:main',
        ],
    },
    keywords="quantum, tomography, neural networks, machine learning",
    project_urls={
        "Bug Reports": "https://github.com/alhazacod/qtom/issues",
        "Source": "https://github.com/alhazacod/qtom",
    },
)
