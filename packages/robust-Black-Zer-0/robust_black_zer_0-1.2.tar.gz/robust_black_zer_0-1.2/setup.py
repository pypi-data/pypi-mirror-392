from setuptools import setup, find_packages

setup(
    name="robust-Black-Zer-0",
    version="1.2",
    packages=find_packages(),
    install_requires=[
        "requests",
	"aiohttp",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "robust=robust.main:run"
        ]
    },
    author="BLACK-ZER-0",
    description="A powerful tool by BLACK ZERO",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/BLACK-ZER-0/robust",
    license="MIT",
)
