"""
Allows for backend switching without editing source code.

Usage:

	from kaplot_backend import set_backend
	set_backend('BACKEND')
	import kaplot

Allowed backends include:

- pdf
- macosx
- agg
- wxagg (requires wx module)

Refer to [matplotlib documentation](http://matplotlib.org/faq/usage_faq.html#what-is-a-backend) for more information.
"""

_backend = None

def set_backend(backend):
	"""
	Switches the backend variable to what is passed by the user.

	TODO: Have some level of error checking here.
	"""
	global _backend
	_backend = backend
	return

def get_backend():
	"""
	Returns the currently selected backend.
	"""
	global _backend
	return _backend