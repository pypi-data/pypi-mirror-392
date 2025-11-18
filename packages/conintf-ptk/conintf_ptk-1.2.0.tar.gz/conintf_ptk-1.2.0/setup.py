from setuptools import setup, find_packages

setup(
    name="conintf_ptk",
    version="1.2.0",
    packages=find_packages(),
    install_requires=[
        "prompt_toolkit>=3.0"
    ],
    python_requires=">=3.8",
    author="Warat Thongsuwan",
    author_email="jimnd55512@gmail.com",
    description="Lightweight async console interface wrapper around prompt_toolkit",
    url="https://github.com/TonpalmUnmain/conintf_ptk",
    license="GPLv3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
