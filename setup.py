from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="transcript-to-brd",
    version="1.0.0",
    author="Utkarsh",
    author_email="",
    description="Production-ready Python project that converts Microsoft Teams meeting transcripts into Business Requirement Documents using RAG-based workflow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Utkarsh242000/transcript-to-brd",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Business and Finance",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "transcript-to-brd=app.main:cli",
        ],
    },
)
