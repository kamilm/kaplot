kaplot
======

kaplot is a plotting tool built around matplotlib. It combines the flexibilty and fantastic plot
generation potention of matplotlib with an easier to use, object oriented, interface. The interface
is simple enough to quickly prototype plots, or fine tune for publication quality results.

Detailed documentation is hosted on [GitHub](kamilm.github.io/kaplot). The package contains 2 modules:

- kaplot is the main module, which contains the kaplot class for plotting.
    - kaplot.defaults is a submodule which contains a couple of pre-made plot settings, which
      are passed as an argument to the kaplot object. More information (including making your
      own settings file) is available in the documentation
- kaplot_backend is a module which allows for selecting a custom `matplotlib` [backend](http://matplotlib.org/faq/usage_faq.html#what-is-a-backend). 