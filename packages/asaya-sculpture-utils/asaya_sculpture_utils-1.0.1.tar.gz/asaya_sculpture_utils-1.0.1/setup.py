from setuptools import setup, find_packages

setup(
    name="asaya_sculpture_utils",
    version="1.0.1",
    author="Asaya",
    author_email="contact@asayasculpture.com",
    description="Simple utility functions for sculpture websites",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://asayasculpture.com",
    project_urls={
        "Homepage": "https://asayasculpture.com",
        "Documentation": "https://asayasculpture.com",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)