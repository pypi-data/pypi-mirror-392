from setuptools import setup, find_packages

setup(
    name="colory-pprint",
    version="1.4.0",
    description="A color-coded JSON pretty printer for Python.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Ruhiddin",
    author_email="niddihur@example.com",
    url="https://github.com/Ruhiddin/colory-pprint",
    license="MIT",
    packages=find_packages(),
    py_modules=['colory_pprint'],
    install_requires=[
        "termcolor",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
