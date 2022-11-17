from distutils.core import setup

setup(
    name="defparse",
    version="0.1.3",
    description="Command Line Arguments from Callable Signatures and Docstrings",
    long_description=open("README.md", "r").read(),
    long_description_content_type='text/markdown',
    author="Niclas Doll",
    author_email="niclas@amazonis.net",
    url="https://github.com/ndoll1998/defparse/tree/master",
    packages=['defparse'],
    package_dir={'defparse': 'defparse'},
    classifiers=[
        "License :: Freely Distributable",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.9"
    ],
    install_requires=['docstring-parser>=0.15']
) 
