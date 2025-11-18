from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="roi_rectangle",
    version='1.0.0',
    author="Isaac Yong",
    author_email="esakyong1866@naver.com",
    description="A module for handling rectangular regions of interest (ROI) in images.",
    url = "https://github.com/SJB7777/roi_rectangle",
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(exclude=["tests"]),
    install_requires=["numpy"],
    keywords=[],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows"
    ],
    python_requires='>=3.8',
)
