"""
@Author: Rqk
@Date: 2021-05-22
@Description:
"""

from setuptools import setup, find_packages

version = "1.0.5"
setup(
    name="pyqidian",
    version=version,
    keywords=[
        "qidian",
        "qidian_api",
    ],
    description="",
    long_description="",
    license="MIT Licence",
    url="https://github.com/renqiukai/pyqidian",
    author="Renqiukai",
    author_email="renqiukai@qq.com",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["requests", "loguru"],
)
