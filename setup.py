import setuptools

with open("README.md") as fh:
    long_description = fh.read()

setuptools.setup(
    name="markusapi",
    version="0.0.1",
    author="Alessio Di Sandro, Misha Schwartz",
    author_email="mschwa@cs.toronto.edu",
    description="Interface to interact with MarkUs API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)