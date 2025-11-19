from setuptools import setup, find_packages

setup(
    name="qtom",
    version="1.0.0",
    description="Neural Network Quantum State Tomography Library",
    author="Manuel A. Garcia & Johan Garzon",
    author_email="mangarciama@unal.edu.co",
    url="https://github.com/alhazacod/qtom",
    packages=find_packages(),
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
