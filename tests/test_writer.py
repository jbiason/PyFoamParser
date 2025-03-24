import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from foamparser import write

logging.basicConfig(level=logging.DEBUG)


def test_simple():
    input = {"a": "1"}
    expected = "a 1;"
    actual = write(input)
    assert actual == expected


def test_multiple_values():
    input = {"a": "1", "b": "2"}
    expected = "a 1;\nb 2;"
    actual = write(input)
    assert actual == expected


def test_list():
    input = {"a": ["1", "2"]}
    expected = "a ( 1 2 );"
    actual = write(input)
    assert actual == expected


def test_dict():
    input = {"a": {"b": "2"}}
    expected = "a\n{\n    b 2;\n}"
    actual = write(input)
    assert actual == expected


def test_complex():
    input = {
        "failures": {"notFound": ["caseId"]},
        "cases": {
            "case1": {
                "name": "short case name",
                "description": "long string\nwith line breaks",
                "location": "URL",
                "lastRun": "dateInISO8601Format",
                "lastVersion": "version",
                "tags": {
                    "heatTransfer": "yes",
                    "temporalScheme": "steady",
                    "physics": ["solid", "radiationSolid"],
                },
            },
            "case2": {
                "name": "short case name",
                "description": "long string\nwith line breaks",
                "location": "URL",
                "lastRun": "dateInISO8601Format",
                "lastVersion": "version",
                "tags": {
                    "heatTransfer": "yes",
                    "temporalScheme": "steady",
                    "physics": ["solid", "radiationSolid"],
                },
            },
        },
    }
    expected = """failures
{
    notFound ( caseId );
}
cases
{
    case1
    {
        name "short case name";
        description "long string\\nwith line breaks";
        location URL;
        lastRun dateInISO8601Format;
        lastVersion version;
        tags
        {
            heatTransfer yes;
            temporalScheme steady;
            physics ( solid radiationSolid );
        }
    }
    case2
    {
        name "short case name";
        description "long string\\nwith line breaks";
        location URL;
        lastRun dateInISO8601Format;
        lastVersion version;
        tags
        {
            heatTransfer yes;
            temporalScheme steady;
            physics ( solid radiationSolid );
        }
    }
}"""
    actual = write(input)
    assert actual == expected


def test_require_quotes():
    """Checks if values that require quotes are being quoted."""
    input = {"a": "1.2.3"}
    expected = 'a "1.2.3";'
    actual = write(input)
    assert actual == expected

    input = {"value": "this-has-dashes"}
    expected = 'value "this-has-dashes";'
    actual = write(input)
    assert actual == expected

    input = {"val.dot": "both-require-quotes"}
    expected = '"val.dot" "both-require-quotes";'
    actual = write(input)
    assert actual == expected


def test_numbers():
    """Checks if we don't try to turn numbers into safe values (which only
    work for strings).
    """
    input = {"a": 1}
    expected = "a 1;"
    actual = write(input)
    assert actual == expected


def test_empty_value():
    """Checks if we quote empty values (thus not producing an invalid foam)."""
    input = {"a": ""}
    expected = 'a "";'
    actual = write(input)
    assert actual == expected


def test_not_quite_empty_value():
    """Checks if we not not quiting "falsy" values when not needed."""
    input = {"a": 0}
    expected = "a 0;"
    actual = write(input)
    assert actual == expected


def test_none():
    """Checks if we output an empty string when the value is None."""
    input = {"a": None}
    expected = 'a "";'
    actual = write(input)
    assert actual == expected


def test_empty_dict():
    """Checks if we output an empty dictionary in a single line."""
    input = {"a": {}}
    expected = "a {}"
    actual = write(input)
    assert actual == expected
