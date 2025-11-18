from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="flask-querymonitor",
    version="1.0.2",
    author="wallmarkets Team",
    author_email="team@wallmarkets.store",
    description="Detect and eliminate N+1 queries in Flask-SQLAlchemy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wallmarkets/flask-querymonitor",
    packages=find_packages(),
    install_requires=["Flask>=2.0.0", "Flask-SQLAlchemy>=3.0.0"],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Flask",
    ],
    keywords="flask sqlalchemy n+1 query-monitoring performance optimization",
    project_urls={
        "Bug Reports": "https://github.com/wallmarkets/flask-querymonitor/issues",
        "Source": "https://github.com/wallmarkets/flask-querymonitor",
    },
)
