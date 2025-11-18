from setuptools import setup, find_packages

setup(
    name="datarun",
    version="0.2.6",
    author="Arun Sundar K",
    author_email="karthicksundar2001@gmail.com",
    description="A simple data cleansing tool using pandas and Machine learning models",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/arunsundark01/datarun",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas"
    ],
)