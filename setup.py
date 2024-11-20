from setuptools import setup, find_packages

def parse_description_from_readme() -> str:
    with open("README.md", "r") as file:
        return file.read().splitlines()[1]

setup(
    name='mi_py_essentials',               # Replace with your package's name
    version='0.2.2',
    packages=find_packages(),        # Automatically find sub
    author='Michael Mueller',
    author_email='michaelmuelleronline@gmx.de',
    description=parse_description_from_readme(),
    url='https://github.com/MichaelMueller/mi_py_essentials_lib.git',  # Link to your repository
)
