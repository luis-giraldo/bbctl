from setuptools import setup, find_packages

setup(
    name="bbctl",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "requests",
        "python-dotenv",
    ],
    entry_points={
        'console_scripts': [
            'bbctl=bbctl.cli:cli',
        ],
    },
)