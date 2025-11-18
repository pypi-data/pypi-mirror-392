from setuptools import setup, find_packages

setup(
    name="Codexify",
    version="0.1.0",
    description="Text-to-coded transformation library",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="maksalmaz",
    author_email="maksalmaz@gmail.com",
    packages=find_packages(),
    python_requires=">=3.8",
    license="MIT",
)