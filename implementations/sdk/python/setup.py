from setuptools import setup, find_packages

setup(
    name="aep-sdk",
    version="1.0.0",
    description="AEP SDK for Python - Agent Execution Protocol",
    author="KOS Contributors",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)