================
Writing Plug-ins
================

A Shape-Link plug-in is a Python script with a class derived from
:class:`shapelink.ShapeLinkPlugin <shapelink.shapelink_plugin.ShapeLinkPlugin>`
and some additional meta data. Let's have a look at
:download:`this example plugin <../plugins/slp_rolling_mean.py>` which
prints the rolling mean of a few
:ref:`scalar features <dclab:sec_features_scalar>` to stdout:


.. literalinclude:: ../plugins/slp_rolling_mean.py
   :language: python
   :linenos:


The main action happens in the
:func:`handle_event <shapelink.shapelink_plugin.ShapeLinkPlugin.handle_event>`
function - your plugin **must** implement at least this function. The two functions
:func:`after_register <shapelink.shapelink_plugin.ShapeLinkPlugin.after_register>`
and
:func:`after_transmission <shapelink.shapelink_plugin.ShapeLinkPlugin.after_transmission>`
can be used to set things up
(e.g. creation of an additional output file) or to tear things down (e.g.
closing that file). Use the
:func:`__init__ <shapelink.shapelink_plugin.ShapeLinkPlugin.__init__>`
function for defining additional class properties.
The ``info`` dictionary is required so that the plugin
can be run via the :ref:`sec_cli`.
