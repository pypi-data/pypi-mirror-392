from setuptools import setup, find_packages

setup(
    name='Zen-STT',
    version='0.2',
    author='ZEN',
    author_email='zenloq7@gmail.com',
    description='Speech to Text automation package created by ZEN',
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        'selenium',
        'webdriver_manager'
    ],
)
