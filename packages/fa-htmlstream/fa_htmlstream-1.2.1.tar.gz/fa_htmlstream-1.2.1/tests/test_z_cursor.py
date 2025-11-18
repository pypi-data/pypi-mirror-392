from io import StringIO
import logging

from htmlstream import Cursor, Parser, OpenTag, CloseTag, Text


def test_track_depth():
    with open('tests/data/small.html', encoding='utf-8') as file:
        parser = Cursor(Parser(file))
        tags = [('html', 1), ('head', 2), ('title', 3), ('body', 2), ('p', 3)]

        tags.reverse()

        for node in parser:
            if isinstance(node, OpenTag):
                tag = tags.pop()
                assert parser.stack[-1].tag == tag[0]
                assert len(parser.stack) == tag[1]

        assert not tags


def test_inner_text():
    with open('tests/data/deep_text.html', encoding='utf-8') as file:
        parser = Cursor(Parser(file))

        for node in parser:
            if isinstance(node, OpenTag) and node.tag == 'p':
                assert parser.getInnerText().strip() == "Whether we buy green things or orange, all is right in bottom of a barrel."
                return


def test_inner_html():
    with open('tests/data/deep_text.html', encoding='utf-8') as file:
        parser = Cursor(Parser(file))
        expected_html = '\n\tWhether we buy green things or orange,'\
            +' <b class="first">all</b> is right in <b>bottom</b> of a barrel.\n\t'
        inner_html = ''

        for node in parser:
            if isinstance(node, OpenTag) and node.tag == 'p':
                inner_html = parser.getInnerHtml()
                break

        assert inner_html == expected_html


def test_findOpenTag_with_no_attributes():
    with open('tests/data/deep_text.html', encoding='utf-8') as file:
        parser = Cursor(Parser(file))

        found_tag = parser.findOpenTag('b')
        assert isinstance(found_tag, OpenTag)
        assert found_tag.tag == 'b'
        assert found_tag['class'] == 'first'


def test_findOpenTag_with_attributes():
    with open('tests/data/deep_text.html', encoding='utf-8') as file:
        parser = Cursor(Parser(file))

        found_tag = parser.findOpenTag('p', {'class':'second'})
        assert isinstance(found_tag, OpenTag)
        assert found_tag.tag == 'p'
        assert found_tag['class'] == 'second'


def test_findOpenTag_empty_tag():
    with open('tests/data/deep_text.html', encoding='utf-8') as file:
        parser = Cursor(Parser(file))

        found_tag = parser.findOpenTag('', {'class':'main'})
        assert isinstance(found_tag, OpenTag)
        assert found_tag.tag == 'p'
        assert found_tag['class'] == 'main'
