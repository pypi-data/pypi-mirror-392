from setuptools import setup, find_packages

setup(
    name="xbyteruser",
    version="0.1.0",
    author="xbyter",
    author_email="xbyter@outlook.com",
    description="A Python package for xbyter user management",
    long_description=open("README.md").read() if open("README.md").read() else "A Python package for xbyter user management",
    long_description_content_type="text/markdown",
    url="https://github.com/xbyter001/xbyteruser",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "pydantic",
        "tortoise-orm",
    ],
)