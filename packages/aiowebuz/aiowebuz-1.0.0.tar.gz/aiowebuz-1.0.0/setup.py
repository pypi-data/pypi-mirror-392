from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="aiowebuz",
    version="1.0.0",
    author="oscoder",
    author_email="oscoderuz@gmail.com",
    description="O'zbek tilida mukammal web parsing va avtomatizatsiya kutubxonasi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oscoderuz/aiowebuz",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    keywords="web scraping parsing selenium automation uzbek",
    project_urls={
        "Bug Reports": "https://github.com/oscoderuz/aiowebuz/issues",
        "Source": "https://github.com/oscoderuz/aiowebuz",
    },
)