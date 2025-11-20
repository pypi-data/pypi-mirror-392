from setuptools import setup, find_packages

setup(
    name="getdates",
    version="0.2.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "getdates=getdates.cli:main",
        ],
    },
    install_requires=[],
    python_requires=">=3.7",
    description="A simple CLI tool to get current or previous datetime",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/getdates",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)

