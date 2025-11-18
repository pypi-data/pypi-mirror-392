from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="quickeda-kit",
    version="0.1.0",
    author="Ashish",
    author_email="ashishbearyy@gmail.com",
    description="A completely automatic EDA (Exploratory Data Analysis) library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ashishali/auto_eda",
    project_urls={
        "Bug Reports": "https://github.com/ashishali/auto_eda/issues",
        "Source": "https://github.com/ashishali/auto_eda",
        "Documentation": "https://github.com/ashishali/auto_eda#readme",
    },
    packages=find_packages(exclude=["test_eda_output", "*.tests", "*.tests.*", "tests.*", "tests"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "scipy>=1.7.0",
        "scikit-learn>=1.0.0",
    ],
    keywords="data-science, eda, exploratory-data-analysis, machine-learning, data-analysis, pandas, automation",
    zip_safe=False,
)


