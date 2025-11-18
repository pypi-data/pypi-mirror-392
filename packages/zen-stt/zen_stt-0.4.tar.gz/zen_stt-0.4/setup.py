from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='Zen_STT',
    version='0.4',
    author='ZEN',
    author_email='zenloq7@gmail.com',
    description='Speech to Text automation package created by ZEN',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        'selenium',
        'webdriver_manager'
    ],
)
