from setuptools import setup, find_packages

setup(
    name="query-optimizer",
    version="0.1.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "psycopg2-binary",
        "mysql-connector-python",
        "sqlparse",
        "rich",
    ],
    python_requires=">=3.8",
    author="El Mehdi Makroumi",
    description="Automatically optimize slow SQL queries across PostgreSQL, MySQL, and SQLite",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/makroumi/query-optimizer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
