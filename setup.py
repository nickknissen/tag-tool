from setuptools import setup, find_packages

setup(
    name="tag-tool",
    version="0.0.1",
    description=("Git tagging tool to generate annotated tag with specified "
                 "format"),
    url="http://github.com/nickknissen/tag-tool",
    entry_points="""
        [console_scripts]
        tag-tool=tag_tool:cli
    """,
    author="Nick Nissen",
    author_email="nickknissen@gmail.com",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Topic :: Terminals",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: OS Independent",
        "Operating System :: POSIX"
    ],
    install_requires=[
        "Jinja2>=2.4",
        "click>=2.0",
        "requests>=2.3.0",
    ]
)
