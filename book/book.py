# -*- coding: utf-8 -*-

import os
from re import search, sub
from json import loads

from IPython.display import Markdown, display

class Book():
    def __init__(self, notebooks=[]):
        self.notebooks = notebooks

    def index():
        return self.pages_tree

    @property
    def pages_tree():
        for notebook_name in notebooks:
            with open(notebook_name, "r") as f:
                content = loads(f.read())
            for i, (cell) in enumerate(content["cells"]):
                subtitle = search(r'#+', cell[source[0]])
                if subtitle:
                    cell[source][0] = "nkasd"

    def chapter_title(notebook):
        with open(notebook, "r") as f:
            content = loads(f.read())
        return search(
            r'-\s(.+)</center>',
            content["cells"][0]["source"][0]
        ).group(1)

    def footer(self, page_number):
        """Build a convenient markdown notebooks paginator and index.

        Args:
             page_number (int): Number of the page of the notebook
                 from you call the method. """
        current_page_number = "%03d" % page_number
        previous_page_number = "%03d" % (page_number - 1)
        next_page_number = "%03d" % (page_number + 1)

        output = "\n_________________________\n"
        pagination = "### <center>"
        index = "### **Índice**:\n"

        IS_FIRST_PAGE = True
        for i, notebook_name in enumerate(sorted(self.notebooks)):
            if os.path.splitext(notebook_name)[1] != ".ipynb":
                continue
            notebook_page = int(search(r'[^d](\d+)', notebook_name).group(1))
            index += '%s. <a href="%s" style="text-decoration:none">**%s**</a>\n' \
                         % (
                    search(r'^\d+', chapter_title(notebook_name)).group(0),
                    notebook_name,
                    sub(r'[\d\.]+', '', chapter_title(notebook_name)).strip(" ")
                )
            if previous_page_number in notebook_name:
                IS_FIRST_PAGE = False
                pagination += "[⬅ %s](%s)" % ( chapter_title(notebook_name), notebook_name )
            if current_page_number in notebook_name:
                if not IS_FIRST_PAGE:
                    pagination += " | "
                pagination += "%s" % chapter_title(notebook_name)
                if IS_FIRST_PAGE:
                    pagination += " | "
            if next_page_number in notebook_name:
                if not IS_FIRST_PAGE:
                    pagination += " | "
                pagination += "[%s ➡](%s)" % ( chapter_title(notebook_name), notebook_name )

        pagination += "</center>"
        output += "%s\n\n%s" % (pagination, index)

        display(Markdown(output))
