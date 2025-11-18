from setuptools import setup, find_packages

setup(
    name="gtpp",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "kivy>=2.2.0"
    ],
    python_requires=">=3.8",
    author="Ahmet ELCI",
    description="Game To PyPI - Virtual pet game with PYPI, Coding for play, not for make game",
    url="https://github.com/rabertsa/gtpp",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "gtpp = game_to_pypi.gui:main",
        ],
    },
)
