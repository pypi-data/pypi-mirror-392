from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="selenium-ui-test-tool",
    version="1.0.7",
    author="Yann Dipita",
    author_email="dipitay@gmail.com",
    description="Bibliothèque Python pour faciliter les tests UI automatisés avec Selenium",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/selenium-ui-test-tool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "selenium>=4.15.0",
        "python-dotenv>=1.0.0",
        "webdriver-manager>=4.0.1",
    ],
)

