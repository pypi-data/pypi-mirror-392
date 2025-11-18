from setuptools import setup, find_packages

setup(
    name="stcchecker",
    version="0.1.0",
    packages=find_packages(),
    author="HARSHVARDHAN (@technopile)",
    author_email="youremail@example.com",
    description="A wrapper for STC API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/stcchecker/",
    license="Custom License - HARSHVARDHAN (@technopile)",
    install_requires=[
        "requests"
    ]
)

