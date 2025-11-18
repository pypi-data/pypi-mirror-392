
from setuptools import setup

setup(
    name="automate-mts",
    version="1.0.0",
    description="Automatically bundles Cobol documentation into sub-directories based on unique filenames.",
    author="Ben Bastianelli",
    author_email="benbastianelli@gmail.com",
    packages=["automate_mts"],
    entry_points={
        'console_scripts': [
            'automate=automate_mts.__main__:automate'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
