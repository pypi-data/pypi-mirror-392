from setuptools import setup, find_packages

setup(
    name="arz-tools-api",
    version="0.1.0",
    author="aurap0n",
    author_email="judinyaros24@mail.ru",
    description="Arizona ToolsApi",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        # список зависимостей
        "requests",
        "Flask",
        "beautifulsoup4",
    ],
)