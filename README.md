# py-d3
D3 and bl.ocks line magics for Jupyter Notebook

The core file in this repository is `py-d3.py`, an IPython extension meant for adding D3.JS support to Jupyter notebooks.

The problem this addresses, in brief: Jupyter notebooks allow executing arbitrary JavaScript code using `IPython.display.JavaScript`, however it makes no effort to restrict the level of DOM objects accessible to executable code. Thus if you ran, for instance, `%javascript d3.selectAll("div").remove();`, you would target and remove *all* `div` elements on the page, including the ones making up the notebook itself!

This plugin attempts to improve on a few existing Jupyter-D3 bindings by restricting `d3` scope to whatever cell you are running the code in. It achieves this by monkey-patching subselection over the core `d3.select` and `d3.selectAll` methods. Declare `%%d3` at the beginning of a cell and you're ready to roll!

The verdict thus far: funky, but operational. With a few outstanding quirks, most D3 visualizations, even very complex ones, can be made to run inside of a Jupyter Notebook `%%d3` cell, with a couple of modifications:

* Remove any D3 imports in the cell (e.g. `<script src="https://d3js.org/d3.v3.js"></script>`). D3 is initialized at cell runtime by the `%%d3` cell magic (`3.5.11` by default, you can specify a specific version via line parameter, e.g. `%%d3 3.4.3`).
* Since an HTML document can only have one `<body>` tag, and it's already defined in the Jupyter framing, variants of `d3.select("body").append("g")` won't work. Workaround: define an `<g>` element yourself and then do `d3.select("g")` instead.

Known issues:

* Force graphs don't work at all. This appears to stem from assumptions the module makes about its runtime environment within D3 code.
* The visualizations won't load on page load because you won't have the proper D3 CDN localized until you actually run the cell. 
* D3 cells generated via `Run All` will almost always fail and raise a `Maximum Recursion Error`. I think this is because `%%d3` display cells (implemented via `IPython.display.display`) just initialize the JavaScript code and move on, and don't wait for any necessary D3 libraries to download via CDN. By the time D3 is ready, your notebook might be done running! Running the cells individually, one-by-one, works every time. Usually.
* For similar reasons, you may sometimes have to run the first `%%d3` cell on the page twice before cells start working properly.
* Only the 3.x branch version of D3 works. The 4.x version fails for [reasons unknown](http://stackoverflow.com/questions/39335992/d3-4-0-does-not-create-a-global-d3-variable-when-imported-into-jupyter-notebook).

I also want to implement a `%block` line magic as a [bl.ocks](http://bl.ocks.org/) interface because that'd allow more elegant one-liner chart embedding. I haven't finshed it yet because there's lots of little string substitutions that have to be written and tests that have to be run to make sure it works, and I don't feel justified in doing so unless all of the root `%%d3` quirks are worked out.

See [this comment by Mike Bostock](https://github.com/d3/d3/issues/2947) for ideation.
