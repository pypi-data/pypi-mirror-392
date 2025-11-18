from setuptools import setup, find_packages

setup(
    name="birthday_surprise",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "colorama",
        "pyfiglet",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "birthday=birthday_surprise:run"
        ]
    },
    author="Devika Harshey",
    description="A CLI birthday surprise package",
    python_requires=">=3.8"
)
