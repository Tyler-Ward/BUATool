from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="buatool",
    version="0.1.1",
    author="Tyler Ward",
    author_email="python@scorpia.co.uk",
    description="Tool to analyse backups",
    long_description=long_description,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["buatool"],
    install_requires=[
        "click"
    ],
    entry_points={
        'console_scripts': [
            'buatool=buatool.main:cli',
        ],
    },

)
