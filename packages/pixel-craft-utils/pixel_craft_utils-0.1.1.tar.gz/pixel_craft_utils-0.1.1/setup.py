from setuptools import setup, find_packages

setup(
    name="pixel_craft_utils",
    version="0.1.1",
    author="Shrey Kalkhnday",
    author_email="developershreyk@gmail.com",
    description="A lightweight Python gaming utility library with vector math, collisions, timers, and movement helpers.",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
