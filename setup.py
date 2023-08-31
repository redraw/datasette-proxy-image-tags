from setuptools import setup
import os

VERSION = "0.1"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-proxy-image-tags",
    description="",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="redraw",
    url="https://github.com/redraw/datasette-proxy-image-tags",
    project_urls={
        "Issues": "https://github.com/redraw/datasette-proxy-image-tags/issues",
        "CI": "https://github.com/redraw/datasette-proxy-image-tags/actions",
        "Changelog": "https://github.com/redraw/datasette-proxy-image-tags/releases",
    },
    license="Apache License, Version 2.0",
    classifiers=[
        "Framework :: Datasette",
        "License :: OSI Approved :: Apache Software License"
    ],
    version=VERSION,
    packages=["datasette_proxy_image_tags"],
    entry_points={"datasette": ["proxy_image_tags = datasette_proxy_image_tags"]},
    install_requires=["datasette"],
    extras_require={"test": ["pytest", "pytest-asyncio"]},
    python_requires=">=3.7",
)
