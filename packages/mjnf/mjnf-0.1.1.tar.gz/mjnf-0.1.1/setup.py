from setuptools import setup, find_packages

setup(
    name="mjnf",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[],
    entry_points={"console_scripts": ["mjnf = mjnf.main:main"]},
    author="zombyburger567",
    description="Решение части 1 и полностью 2 номер из кр Сучкова линал",
)
