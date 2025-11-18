from setuptools import setup, find_packages

setup(
    name="flask-ratelimit-simple",
    version="1.0.0",
    author="wallmarkets Team",
    packages=find_packages(),
    install_requires=["Flask>=2.0.0"],
    python_requires=">=3.7",
)
