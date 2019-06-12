"""
Defines a couple of default settings dictionaries for importing into a kaplot object.
They are user overwritable, by passing a custom dictionary (or list of of dicts) to the kaplot `__init__` function.
Any parameters not specified by the user will come from the `default` settings dictionary.

If it exists, import any user-defined settings from ~/.kaplotdefaults.rc
"""

from imp import load_source
import os.path as osp

default = {
	'PLOT_SETTINGS' 	:	{	'tight_layout'	:	False 		, \
								'xkcd'			:	False		, \
								'style'			:	None		, \
								'x_label_sep_l'	:	' , '		, \
								'x_label_sep_r'	:	''			, \
								'y_label_sep_l'	:	' , '		, \
								'y_label_sep_r'	:	''			, \
								'color_map'		:	'gist_rainbow'},

	'SAVEFIG_SETTINGS' 	:	{	'dpi'			:	100		, \
							  	'transparent'	:	False	, \
							  	'width'			:	8		, \
							  	'height'		:	6},

	'_LOCATION_TIGHT'	:	{	'upper left'	:	[0.18,0.595,0.25,0.25] , \
								'upper right'	:	[0.70,0.595,0.25,0.25] , \
								'lower right'	:	[0.70,0.195,0.25,0.25] , \
								'lower left'	:	[0.18,0.195,0.25,0.25]},

	'_LOCATION'			:	{	'upper left'	:	[0.22,0.595,0.25,0.25] , \
								'upper right'	:	[0.63,0.595,0.25,0.25] , \
								'lower right'	:	[0.63,0.180,0.25,0.25] , \
								'lower left'	:	[0.22,0.180,0.25,0.25]},

	'_FONT_TITLE'		:	{	'family'	: 	'Auto' 		, \
								'weight'	:	'Auto'		, \
								'size'		:	'Auto'		, \
								'color'		:	'Auto'		, \
								'alpha'		:	'Auto'		, \
								'va'		:	'Auto'		, \
								'ha'		:	'Auto'		, \
								'rotation'	:	'Auto'},

	'_FONT_XLABEL'		:	{	'family'	: 	'Auto' 		, \
								'weight'	:	'Auto'		, \
								'size'		:	'Auto'		, \
								'color'		:	'Auto'		, \
								'alpha'		:	'Auto'		, \
								'va'		:	'Auto'		, \
								'ha'		:	'Auto'		, \
								'rotation'	:	'Auto'},

	'_FONT_YLABEL'		:	{	'family'	: 	'Auto' 		, \
								'weight'	:	'Auto'		, \
								'size'		:	'Auto'		, \
								'color'		:	'Auto'		, \
								'alpha'		:	'Auto'		, \
								'va'		:	'Auto'		, \
								'ha'		:	'Auto'		, \
								'rotation'	:	'Auto'},

	'_GRID_SETTINGS'	:	{	'alpha'		:	'Auto'		, \
								'color'		:	'Auto'		, \
								'ls'		:	'Auto'		, \
								'lw'		:	'Auto'},

	'_FONT_XTICK' 		:	{	'family'	: 	'Auto' 		, \
								'weight'	:	'Auto'		, \
								'size'		:	'Auto'		, \
								'color'		:	'Auto'		, \
								'alpha'		:	'Auto'		, \
								'va'		:	'Auto'		, \
								'ha'		:	'Auto'		, \
								'rotation'	:	'Auto'},

	'_FONT_YTICK' 		:	{	'family'	: 	'Auto' 		, \
								'weight'	:	'Auto'		, \
								'size'		:	'Auto'		, \
								'color'		:	'Auto'		, \
								'alpha'		:	'Auto'		, \
								'va'		:	'Auto'		, \
								'ha'		:	'Auto'		, \
								'rotation'	:	'Auto'},

	'_FRAME_LIST'		:	{	'top'		:	'Auto' 		, \
								'bottom'	:	'Auto'		, \
								'right'		:	'Auto'		, \
								'left'		:	'Auto'},

	'_XTICK_PARAMS'		:	{	'direction'		:	'Auto'	, \
								'length'		:	'Auto'	, \
								'width'			:	'Auto'	, \
								'color'			:	'Auto'	, \
								'pad'			:	'Auto'	, \
								'labelsize'		:	'Auto'	, \
								'labelcolor'	:	'Auto'	, \
								'labeltop'		:	'Auto' 	, \
								'labelbottom'	:	'Auto' 	, \
								'top'			:	'Auto'	, \
								'bottom' 		:	'Auto'	, \
								'maxticks'		:	'Auto'},

	'_YTICK_PARAMS'		:	{	'direction'		:	'Auto'	, \
								'length'		:	'Auto'	, \
								'width'			:	'Auto'	, \
								'color'			:	'Auto'	, \
								'pad'			:	'Auto'	, \
								'labelsize'		:	'Auto'	, \
								'labelcolor'	:	'Auto'	, \
								'labelleft'		:	'Auto' 	, \
								'labelright'	:	'Auto' 	, \
								'left'			:	'Auto' 	, \
								'right'			:	'Auto'	, \
								'maxticks'		:	'Auto'},

	'_XTICK_FORMAT'		:	{	'style'		:	'plain'		, \
								'sci_min'	:	0			, \
								'sci_max'	:	0			, \
								'useOffset' :	False},

	'_YTICK_FORMAT'		:	{	'style'		:	'plain'		, \
								'sci_min'	:	0			, \
								'sci_max'	:	0			, \
								'useOffset' :	False},

	'_AX_LINE' 			:	{	'min'		:	'Auto'		, \
								'max'		:	'Auto'		, \
								'alpha'		:	'Auto'		, \
								'ls' 		: 	'Auto'		, \
								'lw'		:	'Auto'		, \
								'color'		:	'Auto'},

	'_TEXT_FONT' 		:	{ 	'family'	: 	'Auto' 		, \
								'weight'	:	'Auto'		, \
								'size'		:	'Auto'		, \
								'color'		:	'Auto'		, \
								'alpha'		:	'Auto'		, \
								'va'		:	'Auto'		, \
								'ha'		:	'Auto'		, \
								'rotation'	:	'Auto'},

	'_LINE_DEFAULTS'	:	{	'x'			:	None			, \
								'y'			:	None			, \
								'xerr'		:	None			, \
								'yerr'		:	None			, \
								'label'		: 	'_nolegend_'	, \
								'increment'	:	True 			, \
								'color'		:	'Auto'			, \
								'lw'		:	'Auto'			, \
								'ls'		:	'Auto'			, \
								'marker'	:	'Auto'			, \
								'mec' 		: 	'Auto'			, \
								'ms'		:	'Auto'			, \
								'markevery'	:	'Auto'			, \
								'mfc' 		: 	'Auto'			, \
								'ecolor'	:	'Auto'			, \
								'elinewidth':	'Auto'			, \
								'capsize'	:	'Auto'			, \
								'alpha'		:	'Auto'			, \
								'spline'	:	False			, \
								'sp_order'	:	3				, \
								'sp_smooth'	:	0 				, \
								'sp_points'	:	1000},

	'_BAR_DEFAULTS' 	:	{	'x'			:	None			, \
								'height'	:	None			, \
								'xerr'		:	None			, \
								'yerr'		:	None			, \
								'label'		:	'_nolegend_'	, \
								'increment'	:	True			, \
								'color'		:	'Auto'			, \
								'lw'		:	'Auto'			, \
								'ls'		:	'Auto'			, \
								'ecolor'	:	'Auto'			, \
								'elinewidth':	'Auto'			, \
								'capsize'	:	'Auto'			, \
								'edgecolor'	:	'Auto'			, \
								'align'		:	'center'		, \
								'width'		:	'Auto'			, \
								'fill'		:	'Auto'			, \
								'hatch'		:	'Auto'			, \
								'facecolor'	:	'Auto'			, \
								'bottom'	:	'Auto'			, \
								'log'		:	'Auto'			, \
								'alpha'		:	'Auto'},

	'_HIST_DEFAULTS'	:	{	'increment'		: True			, \
								'bins'			: 'Auto'		, \
								'min' 			: 'Auto'		, \
								'max' 			: 'Auto'		, \
								'normed' 		: 'Auto'		, \
								'cumulative'	: 'Auto'		, \
								'histtype' 		: 'Auto'		, \
								'align'			: 'Auto'		, \
								'orientation' 	: 'Auto'		, \
								'log' 			: 'Auto'		, \
								'color' 		: 'Auto'		, \
								'label' 		: 'Auto'		, \
								'stacked' 		: 'Auto'		, \
								'alpha' 		: 'Auto'		, \
								'edgecolor'		: 'Auto'		, \
								'facecolor' 	: 'Auto'		, \
								'fill' 			: 'Auto'		, \
								'hatch' 		: 'Auto'		, \
								'ls' 			: 'Auto'		, \
								'lw' 			: 'Auto'},

	'_BOXPLOT_DEFAULTS'	:	{	'increment'		: True			, \
								'label'			: 'Auto'		, \
								'loc'			: 'Auto'		, \
								'whis'			: 'Auto'		, \
								'vert'			: 'Auto'		, \
								'width'			: 'Auto'		, \
								'sym'			: 'Auto'		, \
								'box_fill_color': 'Auto'		, \
								'meanline'		: 'Auto'		, \
								'showmean'		: 'Auto'		, \
								'showcap'		: 'Auto'		, \
								'showbox'		: 'Auto'		, \
								'showfliers'	: 'Auto'		, \
								'boxprops'		: 'Auto'		, \
								'flierprops'	: 'Auto'		, \
								'medianprops'	: 'Auto'		, \
								'meanprops'		: 'Auto'		, \
								'capprops'		: 'Auto'		, \
								'whiskerprops'	: 'Auto'		, \
								'manage_xticks'	: 'Auto'		, \
								'patch_artist'	: True},

	'_BOXSCATTER_DEFAULTS'	:	{'label'		: 	'_nolegend_'	, \
								'color'			:	'Auto'			, \
								'marker'		:	'Auto'			, \
								'mec' 			: 	'Auto'			, \
								'ms'			:	'Auto'			, \
								'markevery'		:	'Auto'			, \
								'mfc' 			: 	'Auto'			, \
								'alpha'			:	'Auto'},


	'_LEGEND_FONTPROPS'	:	{	'family'	:	'sans-serif'	, \
								'weight'	:	'normal'		, \
								'size'		:	'medium'},

	'_LEGEND_DEFAULTS'	:	{	'bool'			:	False			, \
								'loc'			:	'upper right'	, \
								'numpoints'		:	1 				, \
								'markerscale'	:	1 		 		, \
								'edgecolor'		:	'Auto' 			, \
								'frameon'		:	True 			, \
								'fancybox'		:	False 			, \
								'shadow'		:	False 			, \
								'framealpha'	:	1.0 			, \
								'ncol'			:	1 				, \
								'title'			:	None			, \
								'borderpad'		:	0.1 			, \
								'labelspacing'	: 	0.1 			, \
								'handletextpad'	: 	0.25			, \
								'columnspacing'	: 	0.1},

	'_RECTANGLE_DEFAULTS' :	{	'ymin'			: 	'Auto'			, \
								'ymax'			:	'Auto'			, \
								'xmin'			:	'Auto'			, \
								'xmax'			:	'Auto'			, \
								'increment'		:	True			, \
								'color'			:	'Auto'			, \
								'ec'			:	'Auto'			, \
								'fc'			:	'Auto'			, \
								'fill'			:	'Auto'			, \
								'hatch'			:	'Auto'			, \
								'ls'			:	'Auto'			, \
								'lw'			:	'Auto'			, \
								'alpha'			:	'Auto'},

	'_ARROW_DEFAULTS' 	:	{	'x'				:	'Auto'			, \
								'y'				:	'Auto'			, \
								'dx'			:	'Auto'			, \
								'dy'			:	'Auto'			, \
								'width'			:	'Auto'			, \
						'length_includes_head'	:	'Auto'			, \
								'head_width'	:	'Auto'			, \
								'head_length'	:	'Auto'			, \
								'shape'			:	'Auto'			, \
								'overhang'		:	'Auto'			, \
								'alpha'			:	'Auto'			, \
								'ec'			:	'Auto'			, \
								'fc'			:	'Auto'			, \
								'fill'			:	'Auto'			, \
								'hatch'			:	'Auto'			, \
								'ls'			:	'Auto'			, \
								'lw'			:	'Auto'},

	'_COLOR_LIST'		:	['black' , 'red' , 'blue' , 'fuchsia' , 'orange' , 'lime' , 'aqua' , 'maroon' , '0.40' , '0.85'],
	'_MARKER_LIST' 		:	[None , 's' , 'o' , '^' , 'D'],
	'_MARKER_FILL_LIST'	:	[None , 'white'],

	'_HATCH_LIST'		:	[None,'/','\\','|','-','+','x','o','O','.','*'],
	'_HATCH_FILL_LIST'	:	[False, True],
}

greyscale = {
	'_COLOR_LIST' : ['black','0.40'],
}

grayscale = greyscale

blackandwhite = {
	'_COLOR_LIST' : ['black']
}

bw = blackandwhite

markers = {
	'_MARKER_LIST' 		:	['s' , 'o' , '^' , 'D'],
}

try:
	kud = load_source('kaplotUserDefaults',osp.join('.','kaplot','kaplotdefaults.rc'))
	for key,value in kud.__dict__.items():
		if key.startswith('__'):
			continue
		globals()[key] = value
except IOError:
	pass
