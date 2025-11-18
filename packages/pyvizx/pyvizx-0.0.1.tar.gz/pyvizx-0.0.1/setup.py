from setuptools import setup, find_packages

setup(
    name="pyvizx",
    version="0.0.1",
    description="Beginner-friendly simple visualization library",
    long_description=open("pyvizx.egg-info/pyvizx/pyvizx/README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Ganeshamoorthy",
    author_email="ganeshms1110@gmail.com",
    url="https://www.linkedin.com/in/ganeshamoorthy-s-8466b7332",
    license="MIT",

    packages=find_packages(),

    install_requires=[
        "matplotlib",
        "pandas"
    ],

    include_package_data=True,

    python_requires=">=3.7",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
