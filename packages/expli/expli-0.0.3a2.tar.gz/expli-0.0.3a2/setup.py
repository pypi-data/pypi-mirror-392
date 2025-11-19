from setuptools import setup, find_packages

# Read the long description from the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="expli",
    version="0.0.3-alpha2",
    author="Daniel Olson",
    author_email="daniel@orphos.cloud",
    description="Enhanced dataclasses with automatic dict/JSON serialization for nested structures",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/daniel-junglr/cloud_socket",
    packages=find_packages(),
    package_data={
        'expli': ['*.pyi', 'py.typed'],
    },
    include_package_data=True,
    metadata_version="2.3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    install_requires=[
        'typing_extensions>=4.0.0; python_version < "3.11"'
    ],
    python_requires=">=3.10",
    keywords="dataclass, serialization, json, dict, nested, typing, dataclasses, decorator, deserialization",
)
