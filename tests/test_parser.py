import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from foamparser import parse
from foamparser import exceptions

logging.basicConfig(level=logging.DEBUG)


def test_simple():
    """The very basic example."""
    input = "a 1;"
    expected = {"a": "1"}
    actual = parse(input)
    assert actual == expected


def test_list():
    """Checks if loading lists works."""
    input = "a (1 2 3);"
    expected = {"a": ["1", "2", "3"]}
    actual = parse(input)
    assert actual == expected


def test_multilpe_values():
    """Checks if we accept an entry with multiple values."""
    input = "a uniform 2;"
    expected = {"a": ["uniform", "2"]}
    actual = parse(input)
    assert actual == expected


def test_nested_lists():
    """Checks if we can process lists inside lists."""
    input = "a (1 2 (3 4));"
    expected = {"a": ["1", "2", ["3", "4"]]}
    actual = parse(input)
    assert actual == expected


def test_multiple_simple_elements():
    """Checks if multiple entries work fine."""
    input = "a 2; b 3;"
    expected = {"a": "2", "b": "3"}
    actual = parse(input)
    assert actual == expected


def test_quoted():
    input = 'a "value is quoted";'
    expected = {"a": "value is quoted"}
    actual = parse(input)
    assert actual == expected


def test_invalid_token():
    input = "a: invalid;"
    try:
        parse(input)
    except exceptions.UnexpectedCharacterError as exc:
        assert exc.position == 1
        assert exc.text == ": invalid;"
        return
    raise Exception


def test_complex_1():
    """Checks a semi-complex input."""
    input = """name "short case name";
description "long string\\nwith line breaks";
location "URL";
lastRun "dateInISO8601Format";
lastVersion "version";
tags {
	heatTransfer yes;
	temporalScheme steady;
	physics solid radiationSolid;
}"""
    expected = {
        "name": "short case name",
        "description": "long string\\nwith line breaks",
        "location": "URL",
        "lastRun": "dateInISO8601Format",
        "lastVersion": "version",
        "tags": {
            "heatTransfer": "yes",
            "temporalScheme": "steady",
            "physics": ["solid", "radiationSolid"],
        },
    }
    actual = parse(input)
    assert actual == expected


def test_quoted_entries():
    input = """errors
{
    tags
    {
        "physics:time"
        {
            error invalid;
            validValues ( steady fixed );
            currentValue bananas;
        }
    }
}"""

    expected = {
        "errors": {
            "tags": {
                "physics:time": {
                    "error": "invalid",
                    "validValues": ["steady", "fixed"],
                    "currentValue": "bananas",
                }
            }
        }
    }
    actual = parse(input)
    assert actual == expected


def test_nested_dicts():
    input = """cases
{
    1
    {
        name "case 1";
        tags
        {
            physics
            {
                time steady;
            }
        }
    }
    2
    {
        name "case 2";
        tags
        {
            additional
            {
                company customer;
            }
        }
    }
}"""
    expected = {
        "cases": {
            "1": {
                "name": "case 1",
                "tags": {
                    "physics": {
                        "time": "steady",
                    }
                },
            },
            "2": {
                "name": "case 2",
                "tags": {
                    "additional": {
                        "company": "customer",
                    }
                },
            },
        }
    }
    actual = parse(input)
    assert actual == expected


def test_actual():
    input = """name "GUI-Tutorial-1-Diffuser";
location "git@bitbucket.org:engys/examples.git";
lastRun "2024-11-18 11:23:10Z";
lastVersion "4.3.0";
tags
{
    physics
    {
        time                steady;
        dimensionality      3D;
        solverType          segregated;
        density             incompressible;
        turbulence          on;
        turbulenceCoeffs
        {
            simulationType  RAS;
            turbulenceModel kOmegaSST;
        }
        multiphase          no;
        multiregion         no;
        speciesTransport    no;
        energy              off;
        referenceFrame      no;
    }
 
    additional
    {
        application ( GUITutorial );
        CI_systems ( GUIMacro midSizedCoreCI );
    }
   
}
    """
    expected = {
        "name": "GUI-Tutorial-1-Diffuser",
        "location": "git@bitbucket.org:engys/examples.git",
        "lastRun": "2024-11-18 11:23:10Z",
        "lastVersion": "4.3.0",
        "tags": {
            "physics": {
                "time": "steady",
                "dimensionality": "3D",
                "solverType": "segregated",
                "density": "incompressible",
                "turbulence": "on",
                "turbulenceCoeffs": {
                    "simulationType": "RAS",
                    "turbulenceModel": "kOmegaSST",
                },
                "multiphase": "no",
                "multiregion": "no",
                "speciesTransport": "no",
                "energy": "off",
                "referenceFrame": "no",
            },
            "additional": {
                "application": ["GUITutorial"],
                "CI_systems": ["GUIMacro", "midSizedCoreCI"],
            },
        },
    }
    actual = parse(input)
    assert actual == expected


def test_tilde():
    """Tests if the parser accepts identifiers with a tilde in them."""
    input = "~tilde 2;"
    expected = {"~tilde": "2"}
    actual = parse(input)
    assert actual == expected
