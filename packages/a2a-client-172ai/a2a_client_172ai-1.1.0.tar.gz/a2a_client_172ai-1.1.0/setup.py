from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="a2a-client-172ai",
    version="1.1.0",
    author="172.ai",
    author_email="support@172.ai",
    description="Official Python client library for 172.ai A2A (Agent-to-Agent) communication",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/172ai/a2a-client-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
    ],
    keywords="172ai a2a agent-to-agent container api-client sdlc",
)
