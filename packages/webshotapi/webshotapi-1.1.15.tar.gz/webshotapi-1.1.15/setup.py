from setuptools import setup, find_packages,  find_namespace_packages
import os
import re

ROOT_PATH = os.path.dirname(__file__)
PKG_NAME = "webshotapi"
PKG_PATH = os.path.join(ROOT_PATH, PKG_NAME.replace("-", "_"))

def read_version():
    version_file = os.path.join(PKG_NAME, "version.py")
    with open(version_file, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'__version__\s*=\s*"([^"]+)"', content)
    if not match:
        raise RuntimeError("Unable to find __version__ in version.py")
    return match.group(1)

def load_requirements(file_path="requirements.txt"):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

with open('README.md','r') as r:
    long_description = r.read()

setup(
    name='webshotapi',
    version=read_version(),
    packages=find_packages(exclude=["tests", "tests.*"]),
    author="WebShotApi.com",
    author_email="contact@webshotapi.com",
    description="Api client for WebShotApi.com. \
        Website screenshot api client, \
        extract html from rendered website \
        extract words with coordinates from website, \
        extract styles from HTML selectors(elements)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://webshotapi.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Bug Tracker": "https://github.com/webshotapi/python-client/issues",
        "Documentation": "http://webshotapi.com/docs/sdk/python/",
        "Source Code": "https://github.com/webshotapi/python-client",
    },
    install_requires=load_requirements(),
    license="MIT",
    python_requires='>=3.8',
)