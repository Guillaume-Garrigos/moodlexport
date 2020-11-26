import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="moodlexport",
    version="0.0.20",
    author="Guillaume Garrigos",
    author_email="guillaume.garrigos@lpsm.paris",
    license="MIT",
    description="A package to export test questions into Moodle from python or latex",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Guillaume-Garrigos/moodlexport",
    packages=['moodlexport', ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
    'texsoup == 0.2.1',
    'xmltodict >= 0.12.0',
    'lark-parser == 0.11.1'
    ],
    include_package_data=True,
)