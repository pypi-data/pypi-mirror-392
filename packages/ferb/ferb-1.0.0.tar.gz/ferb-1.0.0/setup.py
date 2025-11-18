from setuptools import setup, find_packages

setup(
    name="ferb",
    version="1.0.0",
    description="Link Checker: A GUI + JS-rendered multithreaded broken link checker for dynamic websites.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Shreyash Srivastva",
    packages=find_packages(),
    keywords=["broken links", "SEO", "crawler", "GUI", "playwright", "checker", "link checker"],
    install_requires=[
        "requests",
        "beautifulsoup4",
        "lxml",
        "playwright",
        "pillow",
        "rich"
    ],
    python_requires=">=3.8",
)