from setuptools import setup, find_packages

setup(
    name="interactif_netflix_eda",
    version="0.1.1",
    author="GeeksterLab",
    description="Un bref résumé…",
    long_description="file: README.rst",
    long_description_content_type="text/x-rst",
    url="https://github.com/…",
    package_dir={"": "interactif_netflix_eda"},      # pointe sur ton dossier de code
    packages=find_packages(where="interactif_netflix_eda"),
    python_requires=">=3.10",
    install_requires=[
        "pandas>=2.0.0,<3.0.0",
        "rapidfuzz>=3.9.0,<4.0.0",
        "tqdm>=4.0.0,<5.0.0",
        "fpdf>=1.7.0,<2.0.0",
        "matplotlib>=3.0.0,<4.0.0",
        "seaborn>=0.13.0,<0.14.0",
    ],
    entry_points={
        "console_scripts": [
            "netflix-report=interactif_netflix_eda.classifier_history:main",
            # etc.
        ],
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
