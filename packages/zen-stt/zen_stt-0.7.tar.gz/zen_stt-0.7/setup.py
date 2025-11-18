from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="zen_stt",
    version="0.7",
    author="ZEN",
    author_email="zenloq7@gmail.com",
    description="Speech to Text automation package created by ZEN",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/zen_stt/",
    packages=find_packages(),
    install_requires=[
        "selenium",
        "webdriver-manager"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries"
    ],
    include_package_data=True,
)
