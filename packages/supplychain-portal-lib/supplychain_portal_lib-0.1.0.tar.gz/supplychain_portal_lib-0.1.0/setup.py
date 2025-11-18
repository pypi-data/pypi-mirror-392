from setuptools import setup, find_packages

setup(
    name="supplychain-portal-lib",          # This is the PyPI package name
    version="0.1.0",                        # Increase this number for new releases
    description="Analytics helpers for Supply Chain Portal bookings",
    author="Vishnu Vardhan",
    author_email="adnvishnu@gmail.com",         # optional but recommended
    url="https://pypi.org/project/supplychain-portal-lib/",
    packages=find_packages(),
    python_requires=">=3.8",
)


