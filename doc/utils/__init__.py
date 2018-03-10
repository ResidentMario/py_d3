# -*- coding: utf-8 -*-

from .book import Book


def index(notebooks=[]):
    book = Book(notebooks=notebooks)
    return book.index()

def footer(page_number, notebooks=[]):
    book = Book(notebooks=notebooks)
    return book.footer(page_number)