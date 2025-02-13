"""Configuration de l'installation du package."""
from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name="rag_analyzer",
        version="1.0.0",
        packages=find_packages(
            where="src",
            include=["*"],
            exclude=["tests*"]
        ),
        package_dir={"": "src"},
        include_package_data=True,
        install_requires=[
            "PyQt6>=6.4",
            "sentence-transformers>=2.2",
            "torch>=2.0",
            "numpy>=1.24",
            "scikit-learn>=1.2",
            "aiosqlite>=0.19",
            "python-dotenv>=1.0",
            "pyyaml>=6.0",
        ],
        extras_require={
            "dev": [
                "pytest>=7.4.0",
                "pytest-asyncio>=0.21.0",
                "pytest-cov>=4.1.0",
                "pytest-mock>=3.11.0",
                "pytest-qt>=4.2.0"
            ]
        },
        entry_points={
            "console_scripts": [
                "rag-analyzer=src.ui.windows.main_window:main"
            ]
        },
        python_requires=">=3.10",
        author="Your Name",
        author_email="your.email@example.com",
        description="Application desktop d'analyse de documents avec RAG",
        long_description=open("README.md").read(),
        long_description_content_type="text/markdown",
        keywords="rag, nlp, document-analysis, qt",
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: End Users/Desktop",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Topic :: Text Processing :: General",
            "Topic :: Office/Business",
        ],
    )
