from setuptools import setup, find_packages
from kaplot import __version__

with open('longdesc.rst') as f:
    long_description = f.read()

setup(
	name = 'kaplot',
	version = __version__,
	packages = find_packages(),
	install_requires = ['scipy','numpy','matplotlib','decorator'],

	author = 'Kamil Mielczarek',
	author_email = 'kamil.m@gmail.com',
	url = 'http://github.com/kamilm/kaplot',
	description = 'A plotting tool built around/on matplotlib',
	long_description = long_description,
	classifiers = [
		'Development Status :: 4 - Beta',
		'Intended Audience :: Science/Research',
		'Topic :: Scientific/Engineering :: Visualization',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		'Operating System :: OS Independent',
		'License :: OSI Approved :: MIT License'
	],
	data_files=[('share/kaplot', ['README.md', 'longdesc.rst',
                                'LICENSE', 'CHANGES']),]
)
