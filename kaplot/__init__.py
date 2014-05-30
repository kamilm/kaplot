"""
kaplot is a plotting tool built around matplotlib. It combines the flexibilty and fantastic plot
generation potention of matplotlib with an easier to use, object oriented, interface. The interface
is simple enough to quickly prototype plots, or fine tune for publication quality results.

TODO 
====
	- 	need to add loadObj()
	- 	fix latex output to use the same font
"""

from copy import deepcopy
# required to make pydocs work
from decorator import decorator
import matplotlib
# backends @ http://matplotlib.org/faq/usage_faq.html
from kaplot_backend import get_backend
if get_backend():
	# If kaplot_backend wasn't imported, or no backend was set, then skip explicitly setting a backend
	matplotlib.use(get_backend())
from kaplot.defaults import default
import kaplot.defaults as kd
import matplotlib.pyplot as plt 
import pickle
from scipy.interpolate import UnivariateSpline
from numpy import linspace

__author__		= 'Kamil'
__version__		= '1.0.0~beta2'
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
			for key,val in kwargs.iteritems():
				new_kwargs[key.lower()] = val
			return fn(self,*args,**new_kwargs)
		raise AttributeError('No layer/axes named %s' % kwargs['name'])

class kaplot(object):
	"""
	multi layer plotting class

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

	def __init__(self,settings=None):
		'''Make `kaplot` object: list of layers and associated properties. Also allows for dictionary,
		or list of dictionaries, to be passed as `settings` to adjust plot settings.'''
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
			for key,value in default.iteritems():
				setattr(self,key,value)
			return
		# otherwise there are at least 1 additional settings provided in `settings`
		# since not all groups of settings might be updated, we loop through the default settings,
		# update that group's dictionary with override settings, if present, and add to `self`.
		# Note that some entries in the settings/default dictionary are actually lists. For those
		# we simply overwrite.
		if type(settings) != type([]):
			settings = [settings,]			
		for key,value in default.iteritems():
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
			print 'KAPLOT: add_layer error. layer exists.'
		return

	@check_name
	def set_plot_type(self,ptype,**kwargs):
		"""
		sets the plot type of the layer

		** args **
		ptype 	- plot type , either line , bar 

		** kwargs **
		name 	- layer name if not main
		"""
		k = self._LAYER_OBJECTS[kwargs['ind']]
		if ptype.lower() in ['line', 'bar']:
			k.set_plot_type(ptype)
		else:
			print "KAPLOT Error. Not a valid plot"
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
		fontsize 		- font size 
		borderpad		- padding inside the legend 
		labelspacing	- spacing between labels
		handletextpad	- spacing between legend handle and text 
		columnspacing	- spacing between columns

		** font prop kwargs **
		family			- font family , 'sans-serif' 'serif' 'monospace' 'fantasy'
		style 			- 'normal' or 'oblique'
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
		style 		- 'normal' or 'oblique'
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
			print 'KAPLOT: set_axes_type error. ptype must be either linear,log-log,semilog-x,semilog-y.'
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
			print 'KAPLOT: set_base error. basex or basey must be a valid float.'

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
		style 		- 'normal' or 'oblique'
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
		style 		- 'normal' or 'oblique'
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
	def set_xticks(self,start,stop,incr,log=False,**kwargs):
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

		family		- font family , 'sans-serif' 'serif' 'monospace' 'fantasy'
		style 		- 'normal' or 'oblique'
		size 		- font size , #points 'xx-small' 'medium' 'xx-large'
		weight		- 'normal' 'regular' 'semibold' 'bold' 'black'
		color 		- font color
		alpha 		- alpha level
		va 			- vertical alignment , 'center' 'top' 'bottom' 'baseline'
		ha 			- horizontal alignment , 'center' , 'right' , 'left'
		rotation	- rotate text by some degree
		"""
		fdict 	= update_default_kwargs(self._FONT_XTICK,kwargs)
		k 		= self._LAYER_OBJECTS[kwargs['ind']]
		if 'mylist' in kwargs:
			tick_list = kwargs['mylist']
		else:
			tick_list = srange(start,stop,incr,log)
		k.set_xticks(tick_list,**fdict)
		return

	@check_name
	def set_yticks(self,start,stop,incr,log=False,**kwargs):
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

		family		- font family , 'sans-serif' 'serif' 'monospace' 'fantasy'
		style 		- 'normal' or 'oblique'
		size 		- font size , #points 'xx-small' 'medium' 'xx-large'
		weight		- 'normal' 'regular' 'semibold' 'bold' 'black'
		color 		- font color
		alpha 		- alpha level
		va 			- vertical alignment , 'center' 'top' 'bottom' 'baseline'
		ha 			- horizontal alignment , 'center' , 'right' , 'left'
		rotation	- rotate text by some degree
		"""
		fdict 	= update_default_kwargs(self._FONT_YTICK,kwargs)
		k 		= self._LAYER_OBJECTS[kwargs['ind']]
		if 'mylist' in kwargs:
			tick_list = kwargs['mylist']
		else:
			tick_list = srange(start,stop,incr,log)
		k.set_yticks(tick_list,**fdict)
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

		* valid in both / x-axis *
		labeltop	- True/False 
		labelbottom	- True/False
		top 		- True/False , draw ticks
		bottom		- True/False , draw ticks

		* valid in both / y-axis *
		labelleft	- True/False
		labelright	- True/False
		left 		- True/False , draw ticks
		right		- True/False , draw ticks
		"""
		k 	= self._LAYER_OBJECTS[kwargs['ind']]
		# gets both lists, regardless
		x_params= update_default_kwargs(self._XTICK_PARAMS,kwargs)
		y_params= update_default_kwargs(self._YTICK_PARAMS,kwargs)
		if axis is 'both':
			k.set_x_tick_params(**y_params)
			k.set_y_tick_params(**y_params)
		elif axis is 'x':
			k.set_x_tick_params(**x_params)
		elif axis is 'y':
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
		"""
		k 	= self._LAYER_OBJECTS[kwargs['ind']]
		x_format = update_default_kwargs(self._XTICK_FORMAT,kwargs)
		y_format = update_default_kwargs(self._YTICK_FORMAT,kwargs)
		if axis is 'both':
			k.set_x_tick_format(**x_format)
			k.set_y_tick_format(**y_format)
		elif axis is 'x':
			k.set_x_tick_format(**x_format)
		elif axis is 'y':
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
		ax['y']			= location
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
		ax['x']			= location
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
		style 		- 'normal' or 'oblique'
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
		m 			- marker 
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
		"""
		k 	= self._LAYER_OBJECTS[kwargs['ind']]
		if k.SETTINGS['plot_type'] is 'line':
			sdict 			= update_default_kwargs(self._LINE_DEFAULTS,kwargs)
			sdict['x']		= x
			sdict['y']		= y
		elif k.SETTINGS['plot_type'] is 'bar':
			sdict 			= update_default_kwargs(self._BAR_DEFAULTS,kwargs)
			sdict['left']	= x 
			sdict['height']	= y
		k.add_plotdata(**sdict)
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
		if self.PLOT_SETTINGS['xkcd']:
			plt.xkcd()
		for i,name in enumerate(self._LAYER_NAMES):
			name 	= self._LAYER_NAMES[i]
			k 		= self._LAYER_OBJECTS[i]
			setting = self._LAYER_SETTINGS[i]
			print 'working on layer : %s' % name
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
				mpobj 	= plt.axes()
			else:
				loc_txt = k.SETTINGS['location']
				if type(loc_txt) is type([]):
					loc_cor = loc_txt
				elif self.PLOT_SETTINGS['tight_layout']:
					loc_cor = self._LOCATION_TIGHT[loc_txt]
				else:
					loc_cor = self._LOCATION[loc_txt]
				mpobj = plt.axes(loc_cor)
			# TITLE
			if k.SETTINGS['title'] is not None:
				mpobj.set_title(k.SETTINGS['title'],**k.SETTINGS['title_prop'])
			# GRID
			if k.SETTINGS['grid_bool']:
				mpobj.grid(**k.SETTINGS['grid_prop'])
			# AXES TYPE AND BASE SETTING
			if k.SETTINGS['axes_type'] in ['log-log','semilog-x','semilog-y']:
				if k.SETTINGS['axes_type'] is 'log-log':
					mpobj.set_xscale('log',basex=k.SETTINGS['x_base'])
					mpobj.set_yscale('log',basey=k.SETTINGS['y_base'])
				elif k.SETTINGS['axes_type'] is 'semilog-y':
					mpobj.set_yscale('log',basey=k.SETTINGS['y_base'])
				else:
					mpobj.set_xscale('log',basex=k.SETTINGS['x_base'])
			else:
				mpobj.set_xscale('linear')
				mpobj.set_yscale('linear')
			# AXES LABELS, TICKS, FORMATTING, and PARAMETERS 
			if k.SETTINGS['xlabel'] is not None:
				mpobj.set_xlabel(k.SETTINGS['xlabel'],**k.SETTINGS['xlab_prop'])
			if k.SETTINGS['ylabel'] is not None:
				mpobj.set_ylabel(k.SETTINGS['ylabel'],**k.SETTINGS['ylab_prop'])
			if k.SETTINGS['xticks'] is not None:
				mpobj.set_xticks(k.SETTINGS['xticks'])
				mpobj.set_xticklabels(k.SETTINGS['xticks'],**k.SETTINGS['xtick_prop'])
			if k.SETTINGS['yticks'] is not None:
				mpobj.set_yticks(k.SETTINGS['yticks'])
				mpobj.set_yticklabels(k.SETTINGS['yticks'],**k.SETTINGS['ytick_prop'])
			if k.XTICK_FORMAT is not None:
				mpobj.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
				mpobj.ticklabel_format(axis='x',**k.XTICK_FORMAT)
			if k.YTICK_FORMAT is not None:
				mpobj.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
				mpobj.ticklabel_format(axis='y',**k.YTICK_FORMAT)				
			if k.XTICK_PARAM is not None:
				mpobj.tick_params(axis='x',**k.XTICK_PARAM)
			if k.YTICK_PARAM is not None:
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
			if len(k.AXHLINE_LIST) is not 0:
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
			if len(k.AXVLINE_LIST) is not 0:
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
			if len(k.TEXT_LIST) is not 0:
				for txt in k.TEXT_LIST:
					txt['s'] = txt.pop('txt')
					mpobj.text(**txt)
			# ADD PLOTDATA
			if len(k.DATA_LIST) is not 0:
				# generate color,marker,fill list for the plot
				inc_cnt = 0
				for pd in k.DATA_LIST:
					if pd['increment']:
						inc_cnt += 1
				cnt = 0
				for pd in k.DATA_LIST:
					# line plots
					if k.SETTINGS['plot_type'] is 'line':
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
					elif k.SETTINGS['plot_type'] is 'bar':
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
			# ADD RECTANGLE
			if len(k.RECT_LIST) is not 0:
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
			if len(k.ARROW_LIST) is not 0:
				print 'adding arrows'
				for ad in k.ARROW_LIST:
					mpobj.arrow(**ad)
			# ADD LEGEND
			# -- needs to go last, otherwise possible 'no label situation'
			if k.SETTINGS['leg_props'] is not None:
				if k.SETTINGS['leg_props']['bool']:
					k.SETTINGS['leg_props'].pop('bool')
					mpobj.legend(prop=k.SETTINGS['leg_fprop'],**k.SETTINGS['leg_props'])
			# make copy of the entire object
			self._LAYER_PLT_OBJECT.append(mpobj)
		return

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
		if self._SAVED is None:
			self._SAVED = pickle.dumps(self,pickle.HIGHEST_PROTOCOL)
		sf = update_default_kwargs(self.SAVEFIG_SETTINGS,kwargs)
		fig = plt.gcf()
		if 'width' in sf and 'height' in sf:
			fig.set_size_inches(sf['width'],sf['height'])
			sf.pop('width')
			sf.pop('height')
		if self.PLOT_SETTINGS['tight_layout']:
			plt.tight_layout(pad=1.0)
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

	def showMe(self):
		"""
		shows the figure which has been generated
		note : this depends on the backend selected
		"""
		if self._SAVED is None:
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
		self.SETTINGS 	= 	{	'plot_type'	:	'line'			, \
								'uniq_cols'	:	False			, \
								'color_map'	:	'gist_rainbow'	, \
								'location'	:	None			, \
								'title'		:	None			, \
								'title_prop':	None			, \
								'grid_bool'	:	False			, \
								'grid_prop'	:	None			, \
								'axes_type'	:	'linear'		, \
								'x_base'	:	1.0				, \
								'y_base'	:	1.0				, \
								'xlabel'	:	None			, \
								'xlab_prop'	:	None			, \
								'ylabel'	:	None			, \
								'ylab_prop'	:	None			, \
								'xticks'	:	None			, \
								'xtick_prop':	None			, \
								'yticks'	:	None			, \
								'ytick_prop':	None			, \
								'x_limit'	:	None			, \
								'y_limit'	:	None			, \
								'leg_props'	:	None			, \
								'leg_fprop'	:	None}

		self.FRAMES 	= 	{	'top'		:	True 			, \
								'bottom'	:	True 			, \
								'left'		:	True 			, \
								'right'		:	True}
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
			print 'KAXES: set_location error. location does not exist.'
		return

	def set_plot_type(self,ptype):
		self.SETTINGS['plot_type'] = ptype
		return

	def set_title(self,title,**fdict):
		if title is not None:
			self.SETTINGS['title'] = title
			self.SETTINGS['title_prop'] = fdict
		else:
			print 'KAXES: set_title error. title is None.'
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

	def set_xticks(self,myList,**fdict):
		self.SETTINGS['xticks']		= myList
		self.SETTINGS['xtick_prop']	= fdict
		return

	def set_yticks(self,myList,**fdict):
		self.SETTINGS['yticks']		= myList
		self.SETTINGS['ytick_prop']	= fdict
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
		self.YTICK_FORMAT = {'style':p['style'], 'scilimits':(p['sci_min'],p['sci_max'])}
		return

	def set_x_tick_format(self,**p):
		self.XTICK_FORMAT = {'style':p['style'], 'scilimits':(p['sci_min'],p['sci_max'])}
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
	for key,kval in default_dict.iteritems():
		if key in current_dict:
			return_dict[key] = current_dict[key]
		else:
			if kval is not 'Auto':
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
	if log == False:
		cval = float(start)
		retList =[]
		while cval <= end:
			retList.append(cval)
			cval = float(cval)+float(incr)
	else:
		cval = start
		retList = []
		while cval <= end:
			retList.append(cval)
			cval = float(cval)*float(incr)
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
