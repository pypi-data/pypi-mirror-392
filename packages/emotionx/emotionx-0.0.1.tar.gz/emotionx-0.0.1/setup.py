from setuptools import setup, find_packages

setup(
    name="textemotionx",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[],
    author="Shawn",
    description="A text emotion detection tool",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
)
