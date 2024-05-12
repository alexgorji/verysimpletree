import setuptools
from pathlib import Path

long_description = (Path(__file__).parent / "README.rst").read_text()
setuptools.setup(
    name="musictree",
    version="0.1beta",
    author="Alex Gorji",
    author_email="aligorji@hotmail.com",
    description="lightweight tree data structure for musicxml and musicscore",
    url="https://github.com/alexgorji/musictree.git",
    packages=setuptools.find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True
)
