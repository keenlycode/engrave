import setuptools


with open('README.md') as fh:
    long_description = fh.read()


setuptools.setup(
    name="pillari",
    version="0.0.1",
    author="Nitipit Nontasuwan",
    author_email="nitipit@gmail.com",
    description="Static website generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nitipit/pillari",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'pillari=pillari:run'
        ]
    },
    install_requires=[
        'jinja2==2.11.2',
        'mistune==2.0.0a5',
        'watchgod==0.6',
    ]
)
