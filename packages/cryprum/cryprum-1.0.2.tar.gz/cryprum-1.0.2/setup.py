from pathlib import Path
from setuptools import find_packages, setup

from cryprum.__version__ import __title__, __description__, __version__

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

requirements = [
    "httpx>=0.23.0",
]

setup(
    name=__title__,
    version=__version__,
    author="Cryprum",
    author_email="support@cryprum.com",
    license="MIT",
    url="https://cryprum.com",
    install_requires=requirements,
    keywords=[
        "tiktok api",
        "tiktok-api",
        "tiktok",
    ],
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
