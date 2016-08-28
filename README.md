# py-d3
D3 and bl.ocks line magics for Jupyter Notebook

The core file in this repository is `py-d3.py`, an IPython extension meant for adding D3.JS support to Jupyter notebooks.

The problem this addresses, in brief: Jupyter notebooks allow executing arbitrary JavaScript code using `IPython.display.JavaScript`, however it makes no effort to restrict the level of DOM objects accessible to executable code. Thus if you ran, for instance, `%javascript d3.selectAll("div").remove();`, you would target and remove *all* `div` elements on the page, including the ones making up the notebook itself!

This plugin attempts to improve on a few existing Jupyter-D3 bindings by restricting `d3` scope to whatever cell you are running the code in. It achieves this by monkey-patching subselection over the core `d3.select` and `d3.selectAll` methods.

The verdict thus far: funky, but operational. More specific notes:

* Since an HTML document can only have one `<body>` tag, and it's already defined in the Jupyter framing, variants of `d3.select("body").append("svg")` won't work. Just define an `<svg>` element yourself and then do `d3.select("svg")` instead!
* Force graphs don't work at all. Unclear why.
* The visualizations won't load on page load because you won't have the proper D3 CDN localized until you actually run the cell.
* D3 cells generated via `Run All` will almost always fail and raise a `Maximum Recursion Error`. I think this is because `%%d3` display cells (implemented via `IPython.display.display`) just initialize the JavaScript code and move on, and don't wait for any necessary D3 libraries to download via CDN. By the time D3 is ready, your notebook might be done running! Running the cells individually, one-by-one, works every time. Usually.
* This has only been implemented for the 3.0 branch of D3.JS so far, a 4.0 version is coming.

See [this comment by Mike Bostock](https://github.com/d3/d3/issues/2947) for ideation.
