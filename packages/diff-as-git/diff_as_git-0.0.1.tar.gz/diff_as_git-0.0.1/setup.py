from setuptools import setup


with open("README.md", "r") as arq:
    readme = arq.read()

setup(
    name="diff_as_git",
    version="0.0.1",
    license="MIT License",
    author="Lucas de Souza e Sousa",
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email="lucas11souza97@gmail.com",
    keywords="DIff as git",
    description="This lib is an implementation of the `git diff` tool in Python using the Myers Difference algorithm.",
    packages=["diff_as_git"],
    install_requires=["requests"],
)
