import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="maya-head_parser",
    version="0.00.01",
    author="Christian Martinsson",
    license='MIT',
    author_email="chrillemz@gmail.com",
    description="Parser thar read/write maya header data (fileinfo/required plugin)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ChrilleMZ/maya-head-parser",
    packages=setuptools.find_packages(),
    package_data={'': ['*.*']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)



