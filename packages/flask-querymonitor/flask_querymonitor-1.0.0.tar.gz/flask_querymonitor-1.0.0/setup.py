from setuptools import setup, find_packages

setup(
    name="flask-querymonitor",
    version="1.0.0",
    author="wallmarkets Team",
    packages=find_packages(),
    install_requires=["Flask>=2.0.0", "SQLAlchemy>=1.4.0"],
    python_requires=">=3.7",
)
