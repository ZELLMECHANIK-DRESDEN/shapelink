Shape-Link documentation
========================
To install the requirements for building the documentation, run

    pip install -r requirements.txt

To compile the documentation, run

    sphinx-build . _build

Notes
=====
To view the sphinx inventory of Shape-Link, run

   python -m sphinx.ext.intersphinx 'https://shapelink.readthedocs.io/en/latest/objects.inv'
