"""
kaplot is a plotting tool built around matplotlib. It combines the flexibilty and fantastic plot
generation potential of matplotlib with an easier to use, object oriented, interface. The interface
is simple enough to quickly prototype plots, or fine tune for publication quality results.

NOTES
=====
	- plot_type = boxplot : kwargs passed to any iteration of add_plotdata() will be used for all instances of add_plotdata

TODO
====
	- 	sanitize linestyle/ls = '-',... vs 'solid','dashed','dashdot','dotted'
	-	find a way to implement '\!' (negative space) into latex strings to remove that annoying whitespace after a super/sub script
	- 	need to add loadObj()
	- 	fix latex output to use the same font
"""

from copy import deepcopy
# required to make pydocs work
from decorator import decorator
import matplotlib
matplotlib.use('TkAgg')
# attempt to fix issues with cropping of labels
from matplotlib import rcParams
rcParams.update({'figure.autolayout':True})

from kaplot.defaults import default
from kaplot import defaults as kd
import matplotlib.pyplot as plt
import pickle
from scipy.interpolate import UnivariateSpline
from numpy import linspace
from matplotlib.ticker import ScalarFormatter
import numpy as np


__author__		= 'Kamil'
__version__		= '1.0.7'
__name__		= 'kaplot'

@decorator
def check_name(fn,self,*args,**kwargs):
		"""
		decorator function for kaplot class. checks if the `name` kwarg is
		valid and inserts `ind` into the kwarg list. additionally, changes all
		kwargs to be lower case.
		** args **
		fn 	- function
		"""
		if 'name' not in kwargs:
				kwargs['name'] = 'main'
		if kwargs['name'].lower() in self._LAYER_NAMES:
			oind = self._LAYER_NAMES.index(kwargs['name'].lower())
			kwargs['ind'] = oind
			# rebuild kwargs
			new_kwargs = {}
			for key,val in kwargs.items():
				new_kwargs[key.lower()] = val
			return fn(self,*args,**new_kwargs)
		raise AttributeError('No layer/axes named %s' % kwargs['name'])

class kaplot(object):
	"""
	multi layer plotting class

	mpobj = matplotlib axes object

	organization ;
	a PLOT contains any number of LAYERS,
	each LAYER has a NAME associated with it,
	the NAME is how a LAYER can be identified,
	each LAYER can have any number of features added to it.
	"""

	# used to make latex output same font
	matplotlib.rcParams['font.family'] 		= 'sans-serif'
	matplotlib.rcParams['font.sans-serif']	= 'Arial, Helvetica, sans-serif'
	matplotlib.rcParams['mathtext.default']	= 'regular'

	LAYER_SETTINGS		=	{ 	'twin'			:	None 	, \
								'twin_ref'		:	None}
	# do not add to label/legend if the value exists
	SKIP_LABELS	 		= 	['_nolegend_']

	def __init__(self,settings=None,mpobj=None):
		'''Make `kaplot` object: list of layers and associated properties. Also allows for dictionary,
		or list of dictionaries, to be passed as `settings` to adjust plot settings.'''
		self.GLOBAL_MPOBJ		= None
		self._SAVED				= None
		self._LAYER_NAMES		= []
		self._LAYER_OBJECTS		= []
		self._LAYER_SETTINGS	= []
		self._LAYER_PLT_OBJECT	= []
		self._LAYER_NAMES.append('main')
		self._LAYER_OBJECTS.append(deepcopy(kaxes()))
		self._LAYER_SETTINGS.append(deepcopy(self.LAYER_SETTINGS))
		# Add settings
		self.load_settings(settings)
		if mpobj == None:
			plt.clf()
			plt.cla()
		else:
			plt.cla()
			self.GLOBAL_MPOBJ = mpobj
		return

	def load_settings(self,settings):
		"""
		Reads the settings from `settings`, adds default settings from kaplot.defaults.default,
		and stores in object.
		`settings` may be a list or single dictionary. If a list, each setting within the list is applied in the order
		of the list. It may also be a single or list of strings, in which case kaplot will try to import from
		kaplot.defaults.
		"""
		if not settings:
			# nothing custom was passed
			for key,value in default.items():
				setattr(self,key,value)
			return
		# otherwise there are at least 1 additional settings provided in `settings`
		# since not all groups of settings might be updated, we loop through the default settings,
		# update that group's dictionary with override settings, if present, and add to `self`.
		# Note that some entries in the settings/default dictionary are actually lists. For those
		# we simply overwrite.
		if type(settings) != type([]):
			settings = [settings,]
		for key,value in default.items():
			for setting in settings:
				if type(setting) == type(''):
					try:
						setting = getattr(kd,setting)
					except AttributeError:
						raise AttributeError('%s not found in kaplot.defaults or .kaplotdefaults.rc' % setting)
				if key in setting:
					if type(value) == type({}):
						value.update(setting[key])
					else:
						value = deepcopy(setting[key])
				# else, we're just using the default value anyway
			setattr(self,key,value)

	def set_style(self,mpl_style):
		"""
		sets the matplotlib style via pyplot.style.use('style_name')
		** args **
		mpl_style 	- valid style name
		"""
		self.PLOT_SETTINGS['style'] = mpl_style
		return

	def set_tight(self,tl_bool):
		"""
		updates the tight_layout boolean

		** args **
		tl_bool 	- True/False for tight layout
		"""
		if type(tl_bool) is type(True):
			self.PLOT_SETTINGS['tight_layout'] = tl_bool
		return

	def set_xkcd(self,xk_bool):
		"""
		updates the xkcd mode boolean

		** args **
		xk_bool 	- True/False for xkcd mode
		"""
		if type(xk_bool) is type(True):
			self.PLOT_SETTINGS['xkcd'] = xk_bool
		return

	def add_layer(self,name,location=None,twin=None,twin_ref='main'):
		"""
		adds a new layer to the plot with name `name`

		** args **
		name 		- layer name
		location 	- either None, 'upper left/right' , 'lower left/right' or a 4 coordinate list
		twin 		- either 'x' or 'y' , this will make the new layer share axes 'x' or 'y' with twin_ref
		twin_ref 	- layer name with which this layer will share an axes with
		"""
		if name.lower() not in self._LAYER_NAMES:
			# add layer
			self._LAYER_NAMES.append(name.lower())
			# add layer object and location settings
			k = kaxes()
			k.set_location(location)
			self._LAYER_OBJECTS.append(k)
			# add layer settings
			tmp = deepcopy(self.LAYER_SETTINGS)
			if twin is not None and twin.lower() in ['x', 'y']:
				tmp['twin']		= twin.lower()
				tmp['twin_ref']	= twin_ref.lower()
			self._LAYER_SETTINGS.append(tmp)
		else:
			print('kaplot: add_layer error. layer exists.')
		return

	@check_name
	def set_plot_type(self,ptype,**kwargs):
		"""
		sets the plot type of the layer

		** args **
		ptype 	- line, bar, hist(ogram), box(plot), boxscatter

		** kwargs **
		name 	- layer name if not main
		"""
		k = self._LAYER_OBJECTS[kwargs['ind']]
		if ptype.lower() in ['line', 'bar','hist','histogram', 'box', 'boxplot', 'boxscatter']:
			if ptype.lower() in ['hist', 'histogram']:
				ptype = 'hist'
			if ptype.lower() in ['box', 'boxplot']:
				ptype = 'boxplot'
			if ptype.lower() in ['boxscatter']:
				ptype = 'boxscatter'
			k.set_plot_type(ptype)
		else:
			print('kaplot Error. Not a valid plot')
		return

	@check_name
	def set_legend(self,lbool,**kwargs):
		"""
		sets a legend for the layer

		** args **
		lbool 			- True/False for displaying a legend

		** kwargs **
		name 			- layer name, if not main

		loc 			- location 'upper', 'lower', 'left' , 'right', 'center'
		numpoints		- number of markers to show
		markerscale		- marker scaling
		frameon			- True/False , show frame
		fancybox		- True/False , use a curved frame
		shadow			- True/False , draw a shadow behind the frame
		framealpha		- alpha level for the frame
		ncol 			- number of legend columns
		title 			- legend title
		borderpad		- padding inside the legend
		labelspacing	- spacing between labels
		handletextpad	- spacing between legend handle and text
		columnspacing	- spacing between columns

		** font prop kwargs **
		family			- font family , 'sans-serif' 'serif' 'monospace' 'fantasy'
		weight			- 'normal' 'regular' 'semibold' 'bold' 'black'
		size 			- font size , #points 'xx-small' 'medium' 'xx-large'
		"""
		k 		= self._LAYER_OBJECTS[kwargs['ind']]
		ldict 	= update_default_kwargs(self._LEGEND_DEFAULTS,kwargs)
		fdict 	= update_default_kwargs(self._LEGEND_FONTPROPS,kwargs)
		ldict['bool'] = lbool
		k.set_legend(fdict=fdict,**ldict)
		return

	@check_name
	def set_title(self,title,**kwargs):
		"""
		adds a title to the layer

		** args **
		title 		- layer title

		** kwargs **
		name 		- layer name

		family		- font family , 'sans-serif' 'serif' 'monospace' 'fantasy'
		weight		- 'normal' 'regular' 'semibold' 'bold' 'black'
		size 		- font size , #points 'xx-small' 'medium' 'xx-large'
		color 		- font color
		alpha 		- alpha level
		va 			- vertical alignment , 'center' 'top' 'bottom' 'baseline'
		ha 			- horizontal alignment , 'center' , 'right' , 'left'
		rotation	- rotate text by some degree
		"""
		fdict 	= update_default_kwargs(self._FONT_TITLE,kwargs)
		k 		= self._LAYER_OBJECTS[kwargs['ind']]
		k.set_title(title,**fdict)
		return

	@check_name
	def set_grid(self,gbool,**kwargs):
		"""
		adds grid lines to the layer

		** args **
		gbool 	- True/False for turning grid bool

		** kwargs **
		name 	- layer name
		alpha	- alpha level
		color 	- line color
		ls 		- line style
		lw 		- line width
		"""
		k 		= self._LAYER_OBJECTS[kwargs['ind']]
		gdict	= update_default_kwargs(self._GRID_SETTINGS,kwargs)
		k.set_grid(gbool,**gdict)
		return

	@check_name
	def set_axes_type(self,ptype='linear',**kwargs):
		"""
		sets the axes type for the layer

		** args **
		ptype 	- axes type , 'linear' 'log-log' 'semilog-x' 'semilog-y'

		** kwargs **
		name 	- layer name
		"""
		if ptype.lower() in ['linear','log-log','semilog-x','semilog-y']:
			k 	= self._LAYER_OBJECTS[kwargs['ind']]
			k.set_axes_type(ptype.lower())
		else:
			print('kaplot: set_axes_type error. ptype must be either linear,log-log,semilog-x,semilog-y.')
		return

	@check_name
	def set_base(self,basex=1.0,basey=1.0,**kwargs):
		"""
		sets the base for the axis, useful for semilog and log-log axis

		** args **
		basex 	- x base
		basey 	- y base

		** kwargs **
		name 	- layer name
		"""
		try:
			basex = float(basex)
			basey = float(basey)
			k = self._LAYER_OBJECTS[kwargs['ind']]
			k.set_base(basex,basey)
		except:
			print('kaplot: set_base error. basex or basey must be a valid float.')

	@check_name
	def set_xlabel(self,lab='',unit=None,**kwargs):
		"""
		adds a xlabel to the layer

		** args **
		lab 		- long label
		unit 		- label unit

		** kwargs **
		name 		- layer name

		family		- font family , 'sans-serif' 'serif' 'monospace' 'fantasy'
		weight		- 'normal' 'regular' 'semibold' 'bold' 'black'
		size 		- font size , #points 'xx-small' 'medium' 'xx-large'
		color 		- font color
		alpha 		- alpha level
		va 			- vertical alignment , 'center' 'top' 'bottom' 'baseline'
		ha 			- horizontal alignment , 'center' , 'right' , 'left'
		rotation	- rotate text by some degree
		"""
		fdict 	= update_default_kwargs(self._FONT_XLABEL,kwargs)
		if unit is not None:
			lab 	= '%s%s%s%s' % (lab,self.PLOT_SETTINGS['x_label_sep_l'],unit,self.PLOT_SETTINGS['x_label_sep_r'])
		else:
			lab 	= '%s' % lab
		k 		= self._LAYER_OBJECTS[kwargs['ind']]
		k.set_xlabel(lab,**fdict)
		return

	@check_name
	def set_ylabel(self,lab='',unit=None,**kwargs):
		"""
		adds a ylabel to the layer

		** args **
		lab 		- long label
		unit 		- label unit

		** kwargs **
		name 		- layer name

		family		- font family , 'sans-serif' 'serif' 'monospace' 'fantasy'
		weight		- 'normal' 'regular' 'semibold' 'bold' 'black'
		size 		- font size , #points 'xx-small' 'medium' 'xx-large'
		color 		- font color
		alpha 		- alpha level
		va 			- vertical alignment , 'center' 'top' 'bottom' 'baseline'
		ha 			- horizontal alignment , 'center' , 'right' , 'left'
		rotation	- rotate text by some degree
		"""
		fdict 	= update_default_kwargs(self._FONT_YLABEL,kwargs)
		if unit is not None:
			lab 	= '%s%s%s%s' % (lab,self.PLOT_SETTINGS['y_label_sep_l'],unit,self.PLOT_SETTINGS['y_label_sep_r'])
		else:
			lab 	= '%s' % lab
		k 		= self._LAYER_OBJECTS[kwargs['ind']]
		k.set_ylabel(lab,**fdict)
		return

	@check_name
	def set_xticks(self,start=None,stop=None,incr=None,log=False,**kwargs):
		"""
		sets the values of the ticks , can be logarithmic or custom
		if `myList` is specified it will overwrite all other values

		** args **
		start 		- start value
		end 		- finish value
		icnr		- increment
		log 		- multiply instead of add boolean

		** kwargs **
		name 		- layer name
		mylist		- custom list
		mylabels	- custom labels
		coerce_float- force float precision 

		family		- font family , 'sans-serif' 'serif' 'monospace' 'fantasy'
		size 		- font size , #points 'xx-small' 'medium' 'xx-large'
		weight		- 'normal' 'regular' 'semibold' 'bold' 'black'
		color 		- font color
		alpha 		- alpha level
		va 			- vertical alignment , 'center' 'top' 'bottom' 'baseline'
		ha 			- horizontal alignment , 'center' , 'right' , 'left'
		rotation	- rotate text by some degree
		"""
		fdict 			= update_default_kwargs(self._FONT_XTICK,kwargs)
		k 				= self._LAYER_OBJECTS[kwargs['ind']]
		tick_list		= []
		tick_labels		= []
		if start is not None:
			# start, stop, incr are specified
			tick_list 	= srange(start,stop,incr,log)
			tick_labels	= srange(start,stop,incr,log)
			# crazy float representation issues, KM, 10/11/2018
			if kwargs.get('coerce_float',False):
				tick_list 	= [float('%.12f'% t) for t in tick_list]
				tick_labels = [float('%.12f'% t) for t in tick_list]
			# custom labels
			if 'mylist' in kwargs and 'mylabels' in kwargs:
				for i,val in enumerate(kwargs['mylist']):
					try:
						li = tick_labels.index(val)
						tick_labels[li] = kwargs['mylabels'][i]
					except ValueError:
						print('The Value ',val,' is not in ',tick_labels,'. Ignoring.')
			# custom ticks but no labels
			elif 'mylist' in kwargs and 'mylabels' not in kwargs:
				tick_list 	= kwargs['mylist']
				tick_labels	= kwargs['mylist']
		k.set_xticks(tick_list,tick_labels,**fdict)
		return

	@check_name
	def set_yticks(self,start=None,stop=None,incr=None,log=False,**kwargs):
		"""
		sets the values of the ticks , can be logarithmic or custom
		if `myList` is specified it will overwrite all other values

		** args **
		start 		- start value
		end 		- finish value
		icnr		- increment
		log 		- multiply instead of add boolean

		** kwargs **
		name 		- layer name
		mylist		- custom list
		mylabels 	- custom labels
		coerce_float- force float precision 

		family		- font family , 'sans-serif' 'serif' 'monospace' 'fantasy'
		size 		- font size , #points 'xx-small' 'medium' 'xx-large'
		weight		- 'normal' 'regular' 'semibold' 'bold' 'black'
		color 		- font color
		alpha 		- alpha level
		va 			- vertical alignment , 'center' 'top' 'bottom' 'baseline'
		ha 			- horizontal alignment , 'center' , 'right' , 'left'
		rotation	- rotate text by some degree
		"""
		fdict 			= update_default_kwargs(self._FONT_YTICK,kwargs)
		k 				= self._LAYER_OBJECTS[kwargs['ind']]
		tick_list		= []
		tick_labels 	= []
		if start is not None:
			# start, stop, incr are specified
			tick_list 	= srange(start,stop,incr,log)
			tick_labels	= srange(start,stop,incr,log)
			# crazy float representation issues, KM, 10/11/2018
			if kwargs.get('coerce_float',False):
				tick_list 	= [float('%.12f'% t) for t in tick_list]
				tick_labels = [float('%.12f'% t) for t in tick_list]
			# custom labels
			if 'mylist' in kwargs and 'mylabels' in kwargs:
				for i,val in enumerate(kwargs['mylist']):
					try:
						li = tick_labels.index(val)
						tick_labels[li] = kwargs['mylabels'][i]
					except ValueError:
						print('The Value ',val,' is not in ',tick_labels,'. Ignoring.')
			# custom ticks but no labels
			elif 'mylist' in kwargs and 'mylabels' not in kwargs:
				tick_list 	= kwargs['mylist']
				tick_labels	= kwargs['mylist']
		k.set_yticks(tick_list,tick_labels,**fdict)
		return

	@check_name
	def set_xlim(self,**kwargs):
		"""
		set the upper and lower values of the plot

		** kwargs **
		name 	- layer names
		min 	- lower value
		max 	- upper value
		"""
		xmin = None
		xmax = None
		if 'min' in kwargs:
			xmin = kwargs['min']
		if 'max' in kwargs:
			xmax = kwargs['max']
		k 	= self._LAYER_OBJECTS[kwargs['ind']]
		k.set_xlim(xmin,xmax)
		return

	@check_name
	def set_ylim(self,**kwargs):
		"""
		set the upper and lower values of the plot

		** kwargs **
		name 	- layer names
		min 	- lower value
		max 	- upper value
		"""
		ymin = None
		ymax = None
		if 'min' in kwargs:
			ymin = kwargs['min']
		if 'max' in kwargs:
			ymax = kwargs['max']
		k 	= self._LAYER_OBJECTS[kwargs['ind']]
		k.set_ylim(ymin,ymax)
		return

	@check_name
	def set_tick_params(self,axis='both',**kwargs):
		"""
		sets the properties of ticks, tick labels and axes labels

		** args **
		axis 		- which axis to modify, 'both' 'x' 'y'

		** kwargs **
		name 		- layer name

		direction 	- in / out
		length		- length of tick in points
		width 		- width of tick in points
		color 		- color of tick
		pad 		- padding between tick and label
		labelsize	- tick label font size
		labelcolor 	- tick label font color

		maxticks	- number of ticks

		* valid in x-axis * (both is experimental)
		labeltop	- True/False
		labelbottom	- True/False
		top 		- True/False , draw ticks
		bottom		- True/False , draw ticks

		* valid in y-axis * (both is experimental)
		labelleft	- True/False
		labelright	- True/False
		left 		- True/False , draw ticks
		right		- True/False , draw ticks
		"""
		k 	= self._LAYER_OBJECTS[kwargs['ind']]
		# gets both lists, regardless
		x_params= update_default_kwargs(self._XTICK_PARAMS,kwargs)
		y_params= update_default_kwargs(self._YTICK_PARAMS,kwargs)
		if axis == 'both':
			k.set_x_tick_params(**y_params)
			k.set_y_tick_params(**y_params)
		elif axis == 'x':
			k.set_x_tick_params(**x_params)
		elif axis == 'y':
			k.set_y_tick_params(**y_params)
		return

	@check_name
	def set_tick_format(self,axis='both',**kwargs):
		"""
		sets the tick label formatting, i.e. allows for scientific notation

		** args **
		axis 		- which axis to modify , 'both' 'x' 'y'

		** kwargs **
		name 		- layer name
		style 		- 'plain' or 'sci'
		sci_min		- min for sci notation
		sci_max		- max for sci notation
		useOffset  	- bool
		"""
		k 	= self._LAYER_OBJECTS[kwargs['ind']]
		x_format = update_default_kwargs(self._XTICK_FORMAT,kwargs)
		y_format = update_default_kwargs(self._YTICK_FORMAT,kwargs)
		if axis == 'both':
			k.set_x_tick_format(**x_format)
			k.set_y_tick_format(**y_format)
		elif axis == 'x':
			k.set_x_tick_format(**x_format)
		elif axis == 'y':
			k.set_y_tick_format(**y_format)
		return

	@check_name
	def set_frames(self,**kwargs):
		"""
		removes frames from plots , this function should
		be used in combination with set_tick_params() to
		remove ticks

		** kwargs **
		name 	- layer name
		top 	- True/False
		bottom 	- True/False
		left 	- True/False
		right 	- True/False
		"""
		k 		= self._LAYER_OBJECTS[kwargs['ind']]
		k.set_frames(**kwargs)
		return

	@check_name
	def set_unique_colors(self,ubool,**kwargs):
		"""
		changes the program to use unique colors for the layer

		** kwargs **
		name 	- layer name
		cmap 	- MPL color map name
		"""
		if 'cmap' not in kwargs:
			kwargs['cmap'] = self.PLOT_SETTINGS['color_map']
		k = self._LAYER_OBJECTS[kwargs['ind']]
		k.set_unique_colors(ubool,kwargs['cmap'])
		return

	@check_name
	def add_axhline(self,location,**kwargs):
		"""
		adds a horizontal line to the layer at location y = `location`

		** args **
		location 	- the y-intercept of the horizontal line

		** kwargs **
		name 		- layer name
		min 		- minimum x value
		max 		- maximum x value
		alpha 		- alpha level
		ls			- line style
		lw			- line width
		color 		- line color
		"""
		k 	= self._LAYER_OBJECTS[kwargs['ind']]
		ax = update_default_kwargs(self._AX_LINE,kwargs)
		ax['y']			= float(location)
		if 'min' in kwargs:
			ax['xmin']		= ax.pop('min')
		if 'max' in kwargs:
			ax['xmax']		= ax.pop('max')
		# remove all 'auto' values
		k.add_axhline(**ax)
		return

	@check_name
	def add_axvline(self,location,**kwargs):
		"""
		adds a vertical line to the layer at location x = `location`

		** args **
		location 	- the x-intercept of the vertical line

		** kwargs **
		name 		- layer name
		min 		- minimum y value
		max 		- maximum y value
		alpha 		- alpha level
		ls			- line style
		lw			- line width
		color 		- line color
		"""
		k 	= self._LAYER_OBJECTS[kwargs['ind']]
		ax = update_default_kwargs(self._AX_LINE,kwargs)
		ax['x']			= float(location)
		if 'min' in kwargs:
			ax['ymin']		= ax.pop('min')
		if 'max' in kwargs:
			ax['ymax']		= ax.pop('max')
		# remove all 'auto' values
		k.add_axvline(**ax)
		return

	@check_name
	def add_text(self,txt,x,y,**kwargs):
		"""
		adds text to the layer at the point `x`,`y`

		** args **
		txt 		- text to be added
		x 			- x-coordinate in data coordinates
		y 			- y-coordinate in data coordinates

		** kwargs **
		name 		- layer name
		family		- font family , 'sans-serif' 'serif' 'monospace' 'fantasy'
		weight		- 'normal' 'regular' 'semibold' 'bold' 'black'
		size 		- font size , #points 'xx-small' 'medium' 'xx-large'
		color 		- font color
		alpha 		- alpha level
		va 			- vertical alignment , 'center' 'top' 'bottom' 'baseline'
		ha 			- horizontal alignment , 'center' , 'right' , 'left'
		rotation	- rotate text by some degree
		"""
		k 		= self._LAYER_OBJECTS[kwargs['ind']]
		tdict 	= update_default_kwargs(self._TEXT_FONT,kwargs)
		tdict['txt'] = txt
		tdict['x']	 = x
		tdict['y']	 = y
		k.add_text(**tdict)
		return

	@check_name
	def add_plotdata(self,x,y,**kwargs):
		"""
		adds plot data to the layer

		** args **
		x 			- x data array/list
		y 			- y data array/list

		** kwargs **
		name 		- layer name
		xerr		- x-error data array/list
		yerr		- y-error data array/list
		label 		- data label to be used in legend
		increment 	- True/False , increment the auto color/marker/fill

		color 		- line color
		ls 			- line style
		lw 			- line width
		ecolor 		- error line color
		elinewidth	- error line width
		capsize		- error cap size
		alpha 		- alpha level

		** line plot kwargs **
		marker		- marker
		mec 		- marker edge color
		ms 			- marker size
		markevery 	- marker every data points
		mfc 		- marker face color

		** spline kwargs **
		spline 		- boolean to use a spline
		sp_order 	- spline order, order of the fit
		sp_smooth 	- smoothing parameter, if None the spline will pass through all values
		sp_points 	- use #points between xmin/xmax

		** bar chart kwargs **
		edgecolor	- edge color
		align		- alignment (center or left)
		width		- width
		fill		- fill (True/False)
		hatch 		- hatching
		facecolor 	- fill color
		width 		- array with width for each value
		bottom		- y starting point
		log 		- True/False

		** histogram chart kwargs **
		http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.hist
		bins		- bins to uses during binning
		min 		- lower value for bins, less than min are ignored
		max 		- upper value for bins, grather than max are ignored
		normed 		- True/False : normalize the values, integral is 1
		cumulative	- True/False : each bin is sum of previous bins + new values
		histtype 	- 'bar' , 'barstacked' , 'step' , 'stepfilled'
		align 		- alignment (left, mid, right)
		orientation - 'horizontal' or 'vertical'
		log 		- True/False : Use log scale?
		color 		- color
		label 		- data label
		stacked 	- True/False : stack data on top of each other (true) or next to each other (false)
		alpha 		- alpha level
		edgecolor	-
		facecolor 	-
		fill 		- True/False
		hatch 		-
		ls 			- line style
		lw 			- line width

		** boxplot chart kwargs **
		http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.boxplot
		vert 		- True/False 	:	plot verical or horizontal
		whis 		- 1.5			:	size of the whiskers, $whis$ * Quartile
		loc 		- axes location : 	maps to positions (array)
		width 		- width of box 	: 	maps to widths	(array)
		box_fill_color - 	 		: 	color to fill the box using
		meanline 	- True/False 	:	show a mean as a line
		showmean 	- True/False 	: 	show the mean according to meanprops (maps to showmeans)
		showcap		- True/False 	: 	show the caps at the end of whiskers (maps to showcaps)
		showbox 	- True/False 	: 	show the box portion of boxplot
		showfliers	- True/False 	:	show the outliers
		boxprops	- dictionary 	: 	properties for the box
		label 		- the label 	: 	maps to labels (array)
		flierprops	- dictionary 	: 	properties for fliers
		medianprops	- dictionary	: 	properties for median line
		meanprops 	- dictionary	: 	properties for the mean line
		capprops 	- dictionary	:	properties for the caps
		whiskerprops- dictionary 	: 	properties for the whisker lines
		manage_xticks- True/False 	: 	whether or not 'label' is given to the tick
		"""
		k 			= self._LAYER_OBJECTS[kwargs['ind']]
		kwargs['x']	= x
		kwargs['y'] = y
		k.add_plotdata(**kwargs)
		return

	@check_name
	def add_rectangle(self,top,bottom,**kwargs):
		"""
		adds a rectangle to the plot with coordinates defined by top/bottom

		** args **
		top 		- (x,y) tuple for the top left corner
		bottom 		- (x,y) tuple for the bottom right corner

		** kwargs **
		name 		- layer name
		increment 	- True/False , increment the auto color/marker/fill
		color 		- line color
		ec 			- edge color
		fc 			- fill color
		fill		- fill true/false
		hatch		- hatching
		ls 			- line style
		lw 			- line width
		alpha 		- alpha level
		"""
		k 		= self._LAYER_OBJECTS[kwargs['ind']]
		x_tup 	= [top[0],bottom[0]]
		y_tup	= [top[1],bottom[1]]
		xmin , xmax = sorted(x_tup)
		ymin , ymax = sorted(y_tup)
		kwargs 	= update_default_kwargs(self._RECTANGLE_DEFAULTS,kwargs)
		kwargs['xmin'] , kwargs['xmax'] = xmin , xmax
		kwargs['ymin'] , kwargs['ymax'] = ymin , ymax
		k.add_rectangle(**kwargs)
		return

	@check_name
	def add_arrow(self,start,finish,**kwargs):
		"""
		adds arrow to the text with the coordinates given by start and finish

		** args **
		start 					- (x,y) tuple with starting coordinates , the tail
		finish					- (x,y) tuple with the final coordinates , the tip (arrow head)

		** kwargs **
		name 					- layer name
		width 					- width of full arrow tail
		length_includes_head	- include head in the length, usually false
		head_width				- width of the arrow head
		head_length				- length of arrow head
		shape					- 'full' , 'left' , 'right'
		overhang				- fraction of head which is swept back , default is 0
		alpha					- alpha level
		ec 						- edge color
		fc 						- face color
		fill 					- True/False, fill
		hatch 					- hatch style
		ls						- line style
		lw						- line width
		"""
		k 		= self._LAYER_OBJECTS[kwargs['ind']]
		x 		= start[0]
		dx		= finish[0] - start[0]
		y 		= start[1]
		dy 		= finish[1] - start[1]
		kwargs 	= update_default_kwargs(self._ARROW_DEFAULTS,kwargs)
		kwargs['x']		= x
		kwargs['y'] 	= y
		kwargs['dx']	= dx
		kwargs['dy']	= dy
		k.add_arrow(**kwargs)
		return

	def makePlot(self):
		"""
		generates the matplotlib object from all inputs
		"""
		## helper
		def color_marker_fill_index(cnt,clist,mlist,flist):
			"""
			helper function which uses the cnt number to determine which
			color , marker , fill will be used

			** args **
			cnt 	- integer number

			returns tuple (color_index , marker_index , fill_index)
			"""
			cind = cnt%len(clist)
			mind = (cnt // len(clist)) % len(mlist)
			find = (cnt // (len(clist)*len(mlist))) % len(flist)
			return (cind,mind,find)
		## PLOTTING PORTION
		if self.PLOT_SETTINGS['style'] is not None:
			plt.style.use(self.PLOT_SETTINGS['style'])
		if self.PLOT_SETTINGS['xkcd']:
			plt.xkcd()
		for i,name in enumerate(self._LAYER_NAMES):
			name 	= self._LAYER_NAMES[i]
			k 		= self._LAYER_OBJECTS[i]
			setting = self._LAYER_SETTINGS[i]
			# if axes is twin'd
			if setting['twin'] is not None:
				# grab the axes object to copy
				ind 	= self._LAYER_NAMES.index(setting['twin_ref'])
				mpobj 	= self._LAYER_PLT_OBJECT[ind]
				if setting['twin'] == 'x':
					mpobj = mpobj.twinx()
				else:
					mpobj = mpobj.twiny()
			elif k.SETTINGS['location'] is None:
				if self.GLOBAL_MPOBJ == None:
					mpobj 	= plt.axes()
				else:
					mpobj 	= self.GLOBAL_MPOBJ
			else:
				loc_txt = k.SETTINGS['location']
				if type(loc_txt) is type([]):
					loc_cor = loc_txt
				elif self.PLOT_SETTINGS['tight_layout']:
					loc_cor = self._LOCATION_TIGHT[loc_txt]
				else:
					loc_cor = self._LOCATION[loc_txt]
				if self.GLOBAL_MPOBJ == None:
					mpobj = plt.axes(loc_cor)
				else:
					mpobj = self.GLOBAL_MPOBJ
			# AXES TYPE AND BASE SETTING
			if k.SETTINGS['axes_type'] in ['log-log','semilog-x','semilog-y']:
				if k.SETTINGS['axes_type'] == 'log-log':
					mpobj.set_xscale('log',basex=k.SETTINGS['x_base'])
					mpobj.set_yscale('log',basey=k.SETTINGS['y_base'])
				elif k.SETTINGS['axes_type'] == 'semilog-y':
					mpobj.set_yscale('log',basey=k.SETTINGS['y_base'])
				else:
					mpobj.set_xscale('log',basex=k.SETTINGS['x_base'])
			else:
				mpobj.set_xscale('linear')
				mpobj.set_yscale('linear')
				## Format Helper
				## 5/17/2017 - kamil - after struggling with the axis formatting, this seemed to fix things, it's not robust nor has it been tested
				frmtr = ScalarFormatter(useOffset=False)
				mpobj.get_yaxis().set_major_formatter(frmtr)
				mpobj.get_xaxis().set_major_formatter(frmtr)
			# TITLE
			if k.SETTINGS['title'] is not None:
				mpobj.set_title(k.SETTINGS['title'],**k.SETTINGS['title_prop'])
			# GRID
			if k.SETTINGS['grid_bool']:
				mpobj.grid(**k.SETTINGS['grid_prop'])
			# ADD PLOTDATA
			if len(k.DATA_LIST) != 0:
				for i,pd in enumerate(k.DATA_LIST):
					# update plt settings
					if k.SETTINGS['plot_type'] == 'line':
						npd 			= update_default_kwargs(self._LINE_DEFAULTS,pd)
						k.DATA_LIST[i] 	= npd
					elif k.SETTINGS['plot_type'] == 'bar':
						npd 			= update_default_kwargs(self._BAR_DEFAULTS,pd)
						npd['left']		= pd['x']
						npd['height']	= pd['y']
						k.DATA_LIST[i] 	= npd
					elif k.SETTINGS['plot_type'] == 'hist':
						npd 			= update_default_kwargs(self._HIST_DEFAULTS,pd)
						npd['x']		= pd['y']
						if 'min' in npd.keys() or 'max' in npd.keys():
							npd['range'] = [None,None]
							if 'min' in npd.keys():
								npd['range'][0] = npd.pop('min')
							if 'max' in npd.keys():
								npd['range'][1] = npd.pop('max')
						k.DATA_LIST[i]	= npd
					elif k.SETTINGS['plot_type'] in ['boxplot', 'boxscatter']:
						npd 			= update_default_kwargs(self._BOXPLOT_DEFAULTS,pd)
						npd['boxscatter'] = update_default_kwargs(self._BOXSCATTER_DEFAULTS,{})
						npd['x']		= pd['y']
						k.DATA_LIST[i]	= npd
				if k.SETTINGS['plot_type'] in ['line','bar']:
					# generate color,marker,fill list for the plot
					inc_cnt = 0
					for pd in k.DATA_LIST:
						if pd['increment']:
							inc_cnt += 1
					cnt = 0
					for pd in k.DATA_LIST:
						# line plots
						if k.SETTINGS['plot_type'] == 'line':
							if k.SETTINGS['uniq_cols']:
								cols = unique_colors(inc_cnt+1,k.SETTINGS['color_map'])
								col , mar , fill = cols[cnt] , None , None
							else:
								cind , mind , find = color_marker_fill_index(cnt,self._COLOR_LIST,self._MARKER_LIST,self._MARKER_FILL_LIST)
								col , mar , fill = self._COLOR_LIST[cind] , self._MARKER_LIST[mind] , self._MARKER_FILL_LIST[find]
							if pd['increment']:
								cnt += 1
							if 'color' not in pd:
								pd['color'] = col
							if 'marker' not in pd:
								pd['marker'] = mar
							if 'mfc' not in pd:
								pd['mfc'] = fill
							# spline portion
							sp_key 		= ['color','lw','ls']
							if pd['spline']:
								x_spline 	= linspace(pd['x'][0],pd['x'][-1],pd['sp_points'])
								y_spline 	= UnivariateSpline(pd['x'],pd['y'],k=pd['sp_order'],s=pd['sp_smooth'])(x_spline)
								sp_dict 	= {}
								for sp in sp_key:
									if sp in pd:
										sp_dict[sp] = pd[sp]
								pd['lw'] = 0
								pd['ls'] = ''
								mpobj.errorbar(x=x_spline,y=y_spline,**sp_dict)
							pd.pop('spline')
							pd.pop('sp_smooth')
							pd.pop('sp_order')
							pd.pop('sp_points')
							pd.pop('increment')
							mpobj.errorbar(**pd)
						# bar plots
						elif k.SETTINGS['plot_type'] in ['bar']:
							if k.SETTINGS['uniq_cols']:
								cols = unique_colors(inc_cnt+1,k.SETTINGS['color_map'])
								col , hat , fill = cols[cnt] , None , None
							else:
								cind , hind , find 	= color_marker_fill_index(cnt,self._COLOR_LIST,self._HATCH_LIST,self._HATCH_FILL_LIST)
								col , hat , fill 	= self._COLOR_LIST[cind] , self._HATCH_LIST[hind] , self._HATCH_FILL_LIST[find]
							if pd['increment']:
								cnt += 1
							# do not overwrite user specified values
							if 'color' not in pd:
								pd['color'] = col
							if 'hatch' not in pd:
								pd['hatch'] = hat
							if 'fill' not in pd:
								pd['fill'] = fill
							pd.pop('increment')
							mpobj.bar(**pd)
				elif k.SETTINGS['plot_type'] in ['hist','boxplot', 'boxscatter']:
					# generate color,marker,fill list for the plot
					inc_cnt = 0
					for pd in k.DATA_LIST:
						if pd['increment']:
							inc_cnt += 1
					cnt = 0
					if k.SETTINGS['plot_type'] == 'hist':
						x_list		= []
						labels 		= []
						colors		= []
						histargs	= {}
						for i,pd in enumerate(k.DATA_LIST):
							if k.SETTINGS['uniq_cols']:
								cols = unique_colors(inc_cnt+1,k.SETTINGS['color_map'])
								col = cols[cnt]
							else:
								cind , hind , find 	= color_marker_fill_index(cnt,self._COLOR_LIST,self._HATCH_LIST,self._HATCH_FILL_LIST)
								col = self._COLOR_LIST[cind]
							if pd['increment']:
								cnt += 1
							pd.pop('increment')
							# do not overwrite user specified values
							if 'color' not in pd:
								colors.append(col)
							else:
								colors.append(pd['color'])
								pd.pop('color')
							# data addition
							x_list.append(pd['x'])
							pd.pop('x')
							# data labels
							if 'label' in pd:
								if pd['label'] not in self.SKIP_LABELS:
									labels.append(pd['label'])
								else:
									labels.append('')
								pd.pop('label')
							else:
								labels.append('')
							# build large plot args
							for key,val in pd.items():
								histargs[key] = val
						mpobj.hist(x=x_list,label=labels,color=colors,**histargs)
					elif k.SETTINGS['plot_type'] in ['boxplot', 'boxscatter']:
						x_list 		= []
						labels 		= []
						positions	= []
						bpargs 		= {}
						bsargs 		= {}
						bx_fill_col = []
						for i,pd in enumerate(k.DATA_LIST):
							# add data to plot
							x_list.append(pd['x'])
							# pop off the values that are not required anymore.
							pd.pop('x')
							pd.pop('increment')
							# update colors
							bx_fill_col.append(pd.get('box_fill_color','Auto'))
							pd.pop('box_fill_color',None)
							# add labels to the data sets
							if 'label' in pd:
								if pd['label'] not in self.SKIP_LABELS:
									labels.append(pd['label'])
								else:
									labels.append(None)
								pd.pop('label')
							else:
								labels.append(None)
							# customize the positions
							if 'loc' in pd:
								positions.append(pd['loc'])
								pd.pop('loc')
							else:
								positions.append(i+1)
							# update bpargs with user passed variabls and preform rename if required
							bsargs = pd['boxscatter']
							pd.pop('boxscatter')
							for key,val in pd.items():
								if key in ['width','showmean','showcap']:
									key = key+'s'
								bpargs[key] = val

						# make the box plot complete with box filling
						res_dict = mpobj.boxplot(x=x_list,labels=labels,positions=positions,**bpargs)
						for ind,box in enumerate(res_dict['boxes']):
							# update box fill color
							color = bx_fill_col[ind]
							if color != 'Auto':
								box.set_facecolor(color)
								box.set_zorder(0)
							else:
								box.set_facecolor('None')

						# add the scatter option overtop
						if k.SETTINGS['plot_type'] == 'boxscatter':
							def helper_boxplot(vals):
								# removes the outliers
								quart3,quart1 = np.percentile(vals,[75.0,25.0])
								iqr = quart3 - quart1
								up_lim = (1.5*iqr) + quart3
								dn_lim = quart1 - (1.5*iqr)
								ret_list = []
								for v in vals:
									if v <= up_lim and v >= dn_lim:
										ret_list.append(v)
								# check for single value
								if len(ret_list) == 1:
									ret_list = []
								return ret_list

							pos_array = []
							val_array = []
							for ind,pos in enumerate(positions):
								vals = helper_boxplot(x_list[ind])
								pos_array_ent = [pos]*len(vals)
								pos_array = pos_array + pos_array_ent
								val_array = val_array + vals
							# make it jitter
							rands = np.random.random_integers(-4,4,len(val_array))
							rands = rands/100.0
							# update pos array
							new_pos = []
							for i,ent in enumerate(pos_array):
								new_pos.append(ent+rands[i])
							if bpargs.get('vert',True) == False:
								# horizontal boxplot, swap
								x_, y_ = val_array, new_pos
							else:
								x_, y_ = new_pos, val_array
							mpobj.scatter(x_, y_,**bsargs)

			# AXES LABELS, TICKS, FORMATTING, and PARAMETERS
			if k.SETTINGS['xlabel'] is not None:
				mpobj.set_xlabel(k.SETTINGS['xlabel'],**k.SETTINGS['xlab_prop'])
			if k.SETTINGS['ylabel'] is not None:
				mpobj.set_ylabel(k.SETTINGS['ylabel'],**k.SETTINGS['ylab_prop'])
			if k.SETTINGS['xticks'] is not None:
				mpobj.set_xticks(k.SETTINGS['xticks'])
				mpobj.set_xticklabels(k.SETTINGS['xtick_labels'],**k.SETTINGS['xtick_prop'])
			elif k.SETTINGS['xtick_prop'] is not None:
				# change settings even if no ticks are specified
				mpobj.set_xticklabels(mpobj.get_xticklabels(),**k.SETTINGS['xtick_prop'])
			if k.SETTINGS['yticks'] is not None:
				mpobj.set_yticks(k.SETTINGS['yticks'])
				mpobj.set_yticklabels(k.SETTINGS['ytick_labels'],**k.SETTINGS['ytick_prop'])
			elif k.SETTINGS['ytick_prop'] is not None:
				# change settings even if no ticks are specified
				mpobj.set_yticklabels(mpobj.get_yticklabels(),**k.SETTINGS['ytick_prop'])
#			if k.XTICK_FORMAT is not None:
#				mpobj.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
#				mpobj.ticklabel_format(axis='x',**k.XTICK_FORMAT)
#			if k.YTICK_FORMAT is not None:
#				mpobj.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
#				mpobj.ticklabel_format(axis='y',**k.YTICK_FORMAT)
			if k.XTICK_PARAM is not None:
				if 'maxticks' in k.XTICK_PARAM.keys():
					mpobj.locator_params(axis='x',nbins=k.XTICK_PARAM['maxticks'])
					k.XTICK_PARAM.pop('maxticks')
				mpobj.tick_params(axis='x',**k.XTICK_PARAM)
			if k.YTICK_PARAM is not None:
				if 'maxticks' in k.YTICK_PARAM.keys():
					mpobj.locator_params(axis='y',nbins=k.YTICK_PARAM['maxticks'])
					k.YTICK_PARAM.pop('maxticks')
				mpobj.tick_params(axis='y',**k.YTICK_PARAM)
			# AXES LIMITS
			if k.SETTINGS['x_limit'] is not None:
				xmin , xmax = k.SETTINGS['x_limit']
				if xmin is not None:
					mpobj.set_xlim(xmin=xmin)
				if xmax is not None:
					mpobj.set_xlim(xmax=xmax)
			if k.SETTINGS['y_limit'] is not None:
				ymin , ymax = k.SETTINGS['y_limit']
				if ymin is not None:
					mpobj.set_ylim(ymin=ymin)
				if ymax is not None:
					mpobj.set_ylim(ymax=ymax)
			# FRAME ELEMENTS
			if not k.FRAMES['top']:
				mpobj.spines['top'].set_color('None')
			if not k.FRAMES['bottom']:
				mpobj.spines['bottom'].set_color('None')
			if not k.FRAMES['right']:
				mpobj.spines['right'].set_color('None')
			if not k.FRAMES['left']:
				mpobj.spines['left'].set_color('None')
			# ADD AXHLINE
			if len(k.AXHLINE_LIST) != 0:
				for ax in k.AXHLINE_LIST:
					# convert xmin and xmax values to x,y values
					if 'xmin' in ax.keys():
						xmin , err = convert_xy(mpobj,ax['xmin'],0)
						ax['xmin'] = xmin
					if 'xmax' in ax.keys():
						xmax , err = convert_xy(mpobj,ax['xmax'],0)
						ax['xmax'] = xmax
					mpobj.axhline(**ax)
			# ADD AXVLINE
			if len(k.AXVLINE_LIST) != 0:
				for ax in k.AXVLINE_LIST:
					# convert ymin and xmax values to x,y values
					if 'ymin' in ax.keys():
						err , ymin = convert_xy(mpobj,0,ax['ymin'])
						ax['ymin'] = ymin
					if 'ymax' in ax.keys():
						err, ymax  = convert_xy(mpobj,0,ax['ymax'])
						ax['ymax'] = ymax
					mpobj.axvline(**ax)
			# ADD TEXT
			if len(k.TEXT_LIST) != 0:
				for txt in k.TEXT_LIST:
					txt['s'] = txt.pop('txt')
					mpobj.text(**txt)
			# ADD RECTANGLE
			if len(k.RECT_LIST) != 0:
				inc_cnt = 0
				for rd in k.RECT_LIST:
					if rd['increment']:
						inc_cnt += 1
				# plotting portion
				cnt = 0
				for rd in k.RECT_LIST:
					if k.SETTINGS['uniq_cols']:
						cols = unique_colors(inc_cnt+1,k.SETTINGS['color_map'])
						color , h , fill = cols[cnt] , None , None
					else:
						cind , hind , find 	= color_marker_fill_index(cnt,self._COLOR_LIST,self._HATCH_LIST,self._HATCH_FILL_LIST)
						color , h , fill 	= self._COLOR_LIST[cind] , self._HATCH_LIST[hind] , self._HATCH_FILL_LIST[find]
					if rd['increment']:
						cnt += 1
					# do not overwrite user specified values
					if 'color' not in rd:
						rd['color'] = color
					if 'hatch' not in rd:
						rd['hatch']	= h
					if 'fill' not in rd:
						rd['fill']	= fill
					# y-coords are in data , x-coords are in axes units
					rd['xmin']=convert_xy(mpobj,rd['xmin'],0)[0]
					rd['xmax']=convert_xy(mpobj,rd['xmax'],0)[0]
					rd.pop('increment')
					mpobj.axhspan(**rd)
			# ADD ARROW
			if len(k.ARROW_LIST) != 0:
				print('adding arrows')
				for ad in k.ARROW_LIST:
					mpobj.arrow(**ad)
			# ADD LEGEND
			# -- needs to go last, otherwise possible 'no label situation'
			if k.SETTINGS['leg_props'] is not None:
				if k.SETTINGS['leg_props']['bool']:
					k.SETTINGS['leg_props'].pop('bool')
					l = mpobj.legend(prop=k.SETTINGS['leg_fprop'],**k.SETTINGS['leg_props'])
					# update the legend title also
					if k.SETTINGS['leg_props']['title'] is not None:
						plt.setp(l.get_title(),**k.SETTINGS['leg_fprop'])

			# make copy of the entire object
			self._LAYER_PLT_OBJECT.append(mpobj)

		return mpobj

	def saveMe(self,fname,**kwargs):
		"""
		saves the figure to file `fname`

		** args **
		fname 	- path/filename to save to

		** kwargs **
		height 	- dimension of figure, in inches
		width 	- dimension of figure, in inches
		dpi 	- the dots per inch of the figure
		"""
		#if self._SAVED is None:
		#	self._SAVED = pickle.dumps(self,pickle.HIGHEST_PROTOCOL)
		sf = update_default_kwargs(self.SAVEFIG_SETTINGS,kwargs)
		fig = plt.gcf()
		if 'width' in sf and 'height' in sf:
			fig.set_size_inches(sf['width'],sf['height'])
			sf.pop('width')
			sf.pop('height')
		if self.PLOT_SETTINGS['tight_layout']:
			plt.tight_layout(pad=0.75)
		plt.savefig(fname,**sf)
		return

	def saveObj(self,fname):
		"""
		saves the plot objects to a file `fname` to edit later

		** args **
		fname 	- path/filename to save to
		"""
		f = open(fname,'wb')
		if self._SAVED is None:
			pickle.dump(self,f,pickle.HIGHEST_PROTOCOL)
		else:
			f.write(self._SAVED)
		f.close()
		return

	def showMe(self, saveBool=False):
		"""
		shows the figure which has been generated
		note : this depends on the backend selected
		"""
		if saveBool:
			self._SAVED = pickle.dumps(self,pickle.HIGHEST_PROTOCOL)
		plt.show()
		return

class kaxes(object):
	"""
	helper class for kaplot, all functions here are internal.
	used to build layer objects for the final figure.
	"""
	# location options
	_LOCATION = ['upper left', 'upper right', 'lower left', 'lower right']

	def __init__(self):
		self.SETTINGS 	= 	{	'plot_type'		:	'line'			, \
								'uniq_cols'		:	False			, \
								'color_map'		:	'gist_rainbow'	, \
								'location'		:	None			, \
								'title'			:	None			, \
								'title_prop'	:	None			, \
								'grid_bool'		:	False			, \
								'grid_prop'		:	None			, \
								'axes_type'		:	'linear'		, \
								'x_base'		:	1.0				, \
								'y_base'		:	1.0				, \
								'xlabel'		:	None			, \
								'xlab_prop'		:	None			, \
								'ylabel'		:	None			, \
								'ylab_prop'		:	None			, \
								'xticks'		:	None			, \
								'xtick_labels'	:	None			, \
								'xtick_prop'	:	None			, \
								'yticks'		:	None			, \
								'ytick_labels'	:	None			, \
								'ytick_prop'	:	None			, \
								'x_limit'		:	None			, \
								'y_limit'		:	None			, \
								'leg_props'		:	None			, \
								'leg_fprop'		:	None}

		self.FRAMES 	= 	{	'top'			:	True 			, \
								'bottom'		:	True 			, \
								'left'			:	True 			, \
								'right'			:	True}
		self.XTICK_PARAM 	=	None
		self.YTICK_PARAM 	=	None
		self.XTICK_FORMAT 	= 	None
		self.YTICK_FORMAT 	= 	None
		self.AXHLINE_LIST	= 	[]
		self.AXVLINE_LIST	= 	[]
		self.TEXT_LIST 		= 	[]
		self.DATA_LIST		= 	[]
		self.RECT_LIST		=	[]
		self.ARROW_LIST 	= 	[]
		return

	def set_location(self,location):
		if type(location) is type([]) and len(location) == 4:
			self.SETTINGS['location'] = location
		elif location is None:
			self.SETTINGS['location'] = None
		elif location.lower() in self._LOCATION:
			self.SETTINGS['location'] = location.lower()
		else:
			print('KAXES: set_location error. location does not exist.')
		return

	def set_plot_type(self,ptype):
		self.SETTINGS['plot_type'] = ptype
		return

	def set_title(self,title,**fdict):
		if title is not None:
			self.SETTINGS['title'] = title
			self.SETTINGS['title_prop'] = fdict
		else:
			print('KAXES: set_title error. title is None.')
		return

	def set_grid(self,gbool,**gdict):
		if gbool:
			self.SETTINGS['grid_bool'] 	= True
			self.SETTINGS['grid_prop']	= gdict
		return

	def set_axes_type(self,ptype):
		self.SETTINGS['axes_type'] = ptype.lower()
		return

	def set_base(self,basex,basey):
		self.SETTINGS['x_base'] = basex
		self.SETTINGS['y_base'] = basey
		return

	def set_xlabel(self,lab,**fdict):
		self.SETTINGS['xlabel'] 	= lab
		self.SETTINGS['xlab_prop']	= fdict
		return

	def set_ylabel(self,lab,**fdict):
		self.SETTINGS['ylabel'] 	= lab
		self.SETTINGS['ylab_prop']	= fdict
		return

	def set_xticks(self,myList,myLabels,**fdict):
		self.SETTINGS['xtick_prop']	= fdict
		if len(myList) != 0:
			self.SETTINGS['xticks']			= myList
			self.SETTINGS['xtick_labels']	= myLabels
		return

	def set_yticks(self,myList,myLabels,**fdict):
		self.SETTINGS['ytick_prop']	= fdict
		if len(myList) != 0:
			self.SETTINGS['yticks']			= myList
			self.SETTINGS['ytick_labels']	= myLabels
		return

	def set_xlim(self,xmin,xmax):
		self.SETTINGS['x_limit']	= [xmin, xmax]
		return

	def set_ylim(self,ymin,ymax):
		self.SETTINGS['y_limit']	= [ymin, ymax]
		return

	def set_frames(self,**frames):
		frame_dict = update_default_kwargs(self.FRAMES,frames)
		self.FRAMES = frame_dict
		return

	def set_x_tick_params(self,**params):
		self.XTICK_PARAM = params
		return

	def set_y_tick_params(self,**params):
		self.YTICK_PARAM = params
		return

	def set_unique_colors(self,ubool,cmap):
		self.SETTINGS['uniq_cols'] 	= ubool
		self.SETTINGS['color_map']	= cmap
		return

	def set_y_tick_format(self,**p):
		self.YTICK_FORMAT = {'style':p['style'], 'scilimits':(p['sci_min'],p['sci_max']), 'useOffset':p['useOffset']}
		return

	def set_x_tick_format(self,**p):
		self.XTICK_FORMAT = {'style':p['style'], 'scilimits':(p['sci_min'],p['sci_max']), 'useOffset':p['useOffset']}
		return

	def add_axhline(self,**ax):
		self.AXHLINE_LIST.append(ax)
		return

	def add_axvline(self,**ax):
		self.AXVLINE_LIST.append(ax)
		return

	def add_text(self,**text):
		self.TEXT_LIST.append(text)
		return

	def add_plotdata(self,**pdict):
		self.DATA_LIST.append(pdict)
		return

	def set_legend(self,fdict,**kwargs):
		self.SETTINGS['leg_fprop'] = fdict
		self.SETTINGS['leg_props'] = kwargs
		return

	def add_rectangle(self,**pdict):
		self.RECT_LIST.append(pdict)
		return

	def add_arrow(self,**kwargs):
		self.ARROW_LIST.append(kwargs)
		return

## HELPER FUNCTIONS
def update_default_kwargs(default_dict,current_dict):
	"""
	dictionary helper function. takes a `default_dict` and combines it
	with `current_dict` while filling in missing values.

	** args **
	default_dict - complete dictionary
	current_dict - user supplied dictionary

	returns a dictionary with all values.
	"""
	return_dict = {}
	for key,kval in default_dict.items():
		if key in current_dict:
			return_dict[key] = current_dict[key]
		else:
			if kval != 'Auto':
				return_dict[key] = kval
	return return_dict

def srange(start,end,incr,log=False):
	"""
	returns a number range, from `start` to `end` with an
	increment value of `incr` , it can also be incremented
	multiplicativly by specifying the `log` boolean.

	** args **
	start 	- start value
	end 	- finish value
	icnr	- increment
	log 	- multiply instead of add boolean

	returns a list
	"""
	if incr == 0:
		return []
	if start == end:
		return []
	## type checking
	# if everything can be shown as an int then make all values int
	if int(start) == float(start):
		start = int(start)
	else:
		start = float(start)
	if int(end) == float(end):
		end = int(end)
	else:
		end = float(end)
	if int(incr) == float(incr):
		incr = int(incr)
	else:
		incr = float(incr)
	## /type checking
	if log == False:
		cval = start
		retList =[]
		while cval <= end:
			retList.append(cval)
			cval = cval+incr
	else:
		cval = start
		retList = []
		while cval <= end:
			retList.append(cval)
			cval = cval*incr
	return retList

def convert_xy(ax,x,y):
	"""
	converts `x` and `y` coordinates on an axes object, `ax` to the
	matplotlib normalized values.

	** args **
	ax 		- matplotlib axes object
	x 		- x value
	y 		- y value

	returns normalized coordinate tuple
	"""
	rx , ry = ax.transAxes.inverted().transform(ax.transData.transform((x,y)))
	return (rx,ry)

def unique_colors(ncols,color_map='gist_rainbow'):
	"""
	color generating function. `ncols` specifies how many unique colors
	to generate from `color_map`. for more color_map options consult :
	<http://matplotlib.org/examples/color/colormaps_reference.html>.

	** args **
	ncols 		- number of colors
	color_map	- matplotlib colormap name

	returns a list of color tuples
	"""
	retList = []
	cm = plt.get_cmap(color_map)
	for i in range(ncols):
		color = cm(1.0*i/ncols)
		retList.append(color)
	return retList
