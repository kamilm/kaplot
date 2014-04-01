from setuptools import setup, find_packages
from kaplot import __version__

setup(
	name = 'kaplot',
	version = __version__,
	packages = find_packages(),
	install_requires = ['scipy','numpy','matplotlib','decorator'],

	author = 'Kamil Mielczarek',
	author_email = 'kamil.m@gmail.com',
	url = 'http://github.com/kamilm/kaplot',
	description = 'A plotting tool built around/on matplotlib',
)
