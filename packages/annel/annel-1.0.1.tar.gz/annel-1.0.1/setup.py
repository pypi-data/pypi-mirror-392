from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ann-dl-labs",
    version="1.0.1",
    author="Sameer Rizwan",
    author_email="xie19113@gmail.com",
    description="A collection of neural network implementations from ANN & DL lab assignments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "matplotlib>=3.3.0",
        "scikit-learn>=0.24.0",
        "torch>=1.9.0",
        "torchvision>=0.10.0",
        "tensorflow>=2.5.0",
        "Pillow>=8.0.0",
        "seaborn>=0.11.0",
        "pandas>=1.3.0"
    ],
    keywords=[
        "neural-networks",
        "machine-learning", 
        "deep-learning",
        "pytorch",
        "tensorflow",
        "adaline",
        "mlp",
        "cnn",
        "image-processing"
    ],
)