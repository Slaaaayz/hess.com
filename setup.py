from setuptools import setup, find_packages

setup(
    name="ChessBotApi",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask",
        "opencv-python",
        "numpy",
    ],
    python_requires=">=3.7",
)
