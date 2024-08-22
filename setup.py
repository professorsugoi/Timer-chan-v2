from setuptools import setup, find_packages

setup(
    name="timer_app",
    version="0.1",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        # List your dependencies here
    ],
    entry_points={
        "console_scripts": [
            "timer_app=timer_app.main:main",
        ],
    },
)