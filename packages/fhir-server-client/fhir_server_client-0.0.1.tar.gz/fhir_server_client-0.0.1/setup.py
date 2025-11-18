from setuptools import setup, find_packages

setup(
    name="fhir-server-client",
    version="0.0.1",
    packages=find_packages(),
    install_requires=open('requirements.txt').read().splitlines(),
    description="A Python client for FHIR servers",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/TobiKuehn7/fhir-client",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
