from setuptools import setup, find_packages

setup(
    name="orcatech_client",
    version="0.1.20",
    author="Kezman Saboi",
    author_email="saboi@ohsu.edu",
    description="A Python API client for ORCATECH",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["requests", "python-dotenv"],
    entry_points={
        "console_scripts": [
            "use_client=use_client:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
