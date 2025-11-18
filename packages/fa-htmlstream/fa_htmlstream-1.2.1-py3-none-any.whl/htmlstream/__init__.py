""" A simple streaming HTML parser """
__version__ = '1.2.1'

from .parse import Parser, Node, DocType, Text, Comment, Tag, CloseTag, OpenTag
from .cursor import Cursor, CursorError
