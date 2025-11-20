from setuptools import setup, find_packages

setup(
    name="noyan-dataset",
    version="0.1.5",
    include_package_data=True,
    packages=find_packages(),
    package_data={"noyan.dataset": ["data/*.csv"]},
    install_requires=["pandas"],
    description="Noyan Publications' Custom datasets",
    author="Noyan Publications",
)
