""""""""""
HTMLStream
""""""""""

HTMLStream is a simple stream parser for HTML. Rather than load an entire DOM into memory all at once, HTMLStream reads
a io stream incrementally, resulting in a stream of HTML tags and text. The aim is to be fairly permissible, generating
usable results from even malformed HTML.

==========
Installing
==========

With pip:

.. code-block:: shell

    $ pip install fa-htmlstream


========
Examples
========

Find the doc type of a document:

.. code-block:: python

    from htmlstream import Parser, DocType, Text

    def getDocType(filename:str) -> str:
        with open(filename, encoding='utf-8') as file:
            for node in Parser(file):
                if isinstance(node, Text): continue

                if isinstance(node, DocType):
                    return node.doctype
                else:
                    raise Exception('No doctype!')


Extract all the text:

.. code-block:: python

    from htmlstream import Parser, Text

    def getAllText(filename:str) -> str:
        text = ''

        with open(filename, encoding='utf-8') as file:
            for node in Parser(file):
                if isinstance(node, Text):
                    text += node.text

        return text

Get the text of a specific element:

.. code-block:: python

    from htmlstream import Parser, OpenTag, Text

    def getElementText(filename:str, eid:str) -> str:
        inElement = False
        with open(filename, encoding='utf-8') as file:
            for node in Parser(file):
                if inElement and isinstance(node, Text):
                    return node.text
                if isinstance(node, OpenTag) and node.attributes.get('id') == eid):
                    inElement = True

        return 'MISSING'


----------
The Cursor
----------

We can simplify some of the above using the ``Cursor`` wrapper class. The Cursor has additional state to keep track of
where it is in the element hierarchy and provide utility operations.

For example, get the text of a specific element becomes:

.. code-block:: python

    from htmlstream import Parser, Cursor

    def getElementText(filename:str, eid:str) -> str:
        with open(filename, encoding='utf-8') as file:
            html = Cursor(Parser(file))
            if not html.findOpenTag('', {'id': eid}):
                return 'MISSING'
            return html.getInnerText()

===
API
===


--------------------------------
``class Parser(Iterator[Node])``
--------------------------------

    The parser itself. The parser is an iterator, so it can be used if for loops, passed to ``list()`` and ``next()``,
    and used in list comprehensions.

    ``__init__(stream: TextIOBase, maxTextLength: int|None = None)``
        :stream: The text stream to parse (e.g. a file object).
        :maxTextLength: The maximum length of a text node; unlimited if None

    ``__next__() -> Node``
        Get the next node in the stream.

    ``__iter__() -> Iterator[Node]``
        The Parser itself.

--------------
``class Node``
--------------

    Base node class.

--------------------
``class Text(Node)``
--------------------

    A text node. This includes any and all text between tags, comments, and doctypes.

    :text str: The content of the section of text.

-----------------------
``class Comment(Node)``
-----------------------

    A comment node. All the text between the opening <!-- and closing -->.

    :comment str: The content of the comment.

-----------------------
``class DocType(Node)``
-----------------------

    A doctype node.

    :doctype str: The specific doctype declared (i.e. "html").

-------------------
``class Tag(Node)``
-------------------

    Base tag class.

    :tag str: The name of the tag (e.g. "p", "table", "body", etc.).

----------------------
``class OpenTag(Tag)``
----------------------

    An opening tag, including unclosed and self-closing tags.

    :selfClosing bool: True if the tag is self-closing (for example ``<br />``).
    :attributes dict[str,str|None]: The attributes included in tag. Toggle attributes have the value ``None``.

    ``__getitem__(attr:str) -> str|None``
        Get the value of an attribute. Returns ``None`` for toggle attributes.
        :attr: The name of the attribute

    ``__contains__(attr:str) -> str|None``
        Returns ``true`` if the specified attribute is set on the tag.
        :attr: The name of the attribute


-----------------------
``class CloseTag(Tag)``
-----------------------

    A closing tag.


--------------------------------
``class Cursor(Iterator[Node])``
--------------------------------

    A utility class that wraps a ``Parser``, providing additional tree-streaming functionality. The Cursor moves through
    the Parser's node stream linearly, effectively processing the HTML tree in a depth-first manner.

    :stack list[OpenTag]: The current heirarchy of tags, where ``stack[0]`` is the root element of of the document (e.g.
        `<html`), and ``stack[-1]`` is the opening tag of the element the cursor is currently inside of.
    :depth int: The number of elements deep into the tree the curser is.

    ``__init__(parser: Parser)``
        :parser: The Parser to wrap.

    ``__next__() -> Node``
        Get the next node in the stream.

    ``__iter__() -> Iterator[Node]``
        The Cursor itself.

    ``findOpenTag(tag: str, attrs: dict[str, str]|None = None) -> Node|None``
        Move the cursor the next matching open tag. Returns the tag (or None, if the exact tag couldn't be found).
        :tag: The tag name to search for (e.g. "body" or "img"). If empty, matches any tag.
        :attr: Optional specific attributes the tag must have
    
    ``getInnerText() -> str``
        Get the text of all of the text nodes within the current element.

    ``getInnerHtml() -> str``
        Get the html within the current element.

