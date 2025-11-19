from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aiotelebotuz",
    version="1.0.0",
    author="AioTeleBot",
    description="Aiogram 3 uchun o'zbekcha va juda oson kutubxona",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sizning-username/aiotelebot",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        'aiogram>=3.0.0',
    ],
)