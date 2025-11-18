
from setuptools import setup

setup(
    name="change-extension-recurse",
    version="1.0.1",
    description="A command-line tool to change file extensions recursively in a directory.",
    author="Ben Bastianelli",
    author_email="benbastianelli@gmail.com",
    packages=["change_extension"],
    entry_points={
        'console_scripts': [
            'change=change_extension.__main__:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
