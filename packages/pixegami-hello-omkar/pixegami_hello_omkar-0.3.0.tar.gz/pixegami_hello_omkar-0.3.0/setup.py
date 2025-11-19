from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="pixegami-hello-omkar",
    version="0.3.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "pixegami-hello = pixegami_hello.main:main"
        ]
    },
    long_description=description,
    long_description_content_type="text/markdown",
)
