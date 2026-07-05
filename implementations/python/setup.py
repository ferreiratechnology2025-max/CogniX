from setuptools import setup, find_packages

setup(
    name="aep",
    version="1.0.0",
    description="Agent Execution Protocol (AEP) - Python Implementation",
    author="KOS Contributors",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "aep=aep.cli.main:main",
        ],
    },
)