from src.parser.markdown_ast import (
    BlankLineNode,
    CodeBlockNode,
    HeadingNode,
    ListBlockNode,
    ParagraphNode,
    parse_markdown,
)


def test_parse_markdown_emits_nodes_in_order():
    text = (
        "# Title\n"
        "\n"
        "Intro line\n"
        "Second line\n"
        "\n"
        "- Item one\n"
        "  continuation\n"
        "- Item two\n"
        "\n"
        "```python\n"
        "# not a heading\n"
        "```\n"
    )

    nodes = parse_markdown(text)

    assert isinstance(nodes[0], HeadingNode)
    assert nodes[0].level == 1
    assert nodes[0].text == "Title"

    assert isinstance(nodes[1], BlankLineNode)

    assert isinstance(nodes[2], ParagraphNode)
    assert nodes[2].lines == ["Intro line\n", "Second line\n"]

    assert isinstance(nodes[3], BlankLineNode)

    assert isinstance(nodes[4], ListBlockNode)
    assert nodes[4].ordered is False
    assert len(nodes[4].items) == 2
    assert nodes[4].items[0].lines == ["- Item one\n", "  continuation\n"]

    assert isinstance(nodes[5], BlankLineNode)

    assert isinstance(nodes[6], CodeBlockNode)
    assert nodes[6].info == "python"
    assert nodes[6].lines == ["# not a heading\n"]


def test_parse_markdown_supports_ordered_lists_from_iterable():
    lines = ["1. First\n", "2. Second\n", "\n", "Next\n"]

    nodes = parse_markdown(lines)

    assert isinstance(nodes[0], ListBlockNode)
    assert nodes[0].ordered is True
    assert len(nodes[0].items) == 2
    assert nodes[0].line_start == 1
    assert nodes[0].line_end == 3
    assert isinstance(nodes[1], BlankLineNode)
    assert isinstance(nodes[2], ParagraphNode)
