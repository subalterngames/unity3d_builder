from setuptools import setup
from pathlib import Path

setup(
    name="unity3d_builder",
    packages={"unity3d_builder"},
    version="1.0",
    license="MIT",
    description="Create Unity3D standalone applications of a project for Windows, OS X, and Linux.",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Seth Alter",
    author_email="subalterngames@gmail.com",
    url="https://github.com/subalterngames/unity3d_builder",
    keywords=["unity3d"],
    install_requires=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
)
