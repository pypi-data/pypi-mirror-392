from setuptools import setup, find_packages

setup(
    name="sreeharix-testv1-hello",
    version="1.0.2",
    packages=find_packages(),
    install_requires=[
         # add dependencies here

    ],

    entry_points={
        "console_scripts": [
            "test_hello=test_hello.main:hello",
        ],
    },


    
)