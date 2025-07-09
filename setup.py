from setuptools import setup, find_packages

setup(
    name="release-notes-gpt",
    version="0.1.0",
    description="ClickUp-powered release notes generator for FieldSync",
    author="Lucy Kien",
    packages=find_packages(),
    install_requires=[
        "Flask",
        "requests",
        "python-dotenv"
    ],
)
