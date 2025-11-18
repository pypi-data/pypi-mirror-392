from setuptools import setup, find_packages

setup(
    name="kigo-gui-framework",
    version="0.1.0",
    description="A simple GUI library built on Tkinter",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="swiss.armyknife@github.com",
    url="",  # Leave empty for now, add GitHub link later
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)