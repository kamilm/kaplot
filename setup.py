from setuptools import setup, find_packages

setup(
	name = 'kaplot',
	version = '0.7',
	packages = find_packages(),
	install_requires = ['scipy','numpy','matplotlib','decorator']
)
