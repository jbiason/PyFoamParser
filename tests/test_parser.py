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
    """Checks if the parser can properly find strings with quotes, and produce a single result."""
    input = 'a "value is quoted";'
    expected = {"a": "value is quoted"}
    actual = parse(input)
    assert actual == expected


def test_invalid_token():
    """Checks if the parser produces an error in case the content can't be parsed."""
    # In this case, we are considering ":" an invalid token for a variable.
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
    """Checks if the parser properly finds entries that are properly quoted to cover invalid identified characters."""
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
    """Checks if the library handles dictionaries inside dictionaries."""
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
    """Tests for a fairly complex dictionary."""
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


def test_line_comment():
    """Tests if we can parse line comments correctly."""
    input = """a 2;
// and this is ignored
b 3;"""
    expected = {"a": "2", "b": "3"}
    actual = parse(input)
    assert actual == expected


def test_block_comment():
    """Tests if we can parse block comments correctly."""
    input = """/* this multiline comments
must be ignored */
    a 2;"""
    expected = {"a": "2"}
    actual = parse(input)
    assert actual == expected


def test_block_comment2():
    """Tests if we parse a block comment when it doesn't have any "separators."""
    input = """/*---------------
block comment
-----------*/
a 1;"""
    expected = {"a": "1"}
    actual = parse(input)
    assert actual == expected


def test_dot_values():
    """Tests if we can parse values with dots in them."""
    input = "a 0.0000001;"
    expected = {"a": "0.0000001"}
    actual = parse(input)
    assert actual == expected


def test_multiple_quoted_values():
    """Tests if the parser picks multiple values when they are all quoted."""
    input = 'a "val1" "val2" "val3";'
    expected = {"a": ["val1", "val2", "val3"]}
    actual = parse(input)
    assert actual == expected


def test_control_dict():
    """Tests if the parser properly parses a more complex structure, like a full controlDict."""
    input = """/*--------------------------------*- C++ -*----------------------------------*\
|       o          |                                                          |
|    o     o       | HELYX(R): Open-source CFD for Enterprise                 |
|   o   O   o      | Version: vd.e.v--Apr22-A10                               |
|    o     o       | Engys Ltd. http://www.engys.com                          |
|       o          |                                                          |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version 2.0;
    format ascii;
    class dictionary;
    location system;
    object controlDict;
}
    application pimpleDyMFoam;
    startFrom latestTime;
    startTime 0;
    stopAt endTime;
    endTime 10.0;
    deltaT 0.01;
    writeControl adjustableRunTime;
    writeInterval 0.2;
    purgeWrite 0;
    writeFormat binary;
    writePrecision 10;
    writeCompression uncompressed;
    writeEndTime true;
    timeFormat general;
    timePrecision 6;
    graphFormat raw;
    runTimeModifiable yes;
    adjustTimeStep true;
    maxCo 1.0;
    maxDeltaT 1.0;
    maxAlphaCo 0.0;
    minDeltaT 1.0E-6;
    functions
    {
        FP
        {
            type fieldProcess;
            regions ( region0 );
            executeControl writeTime;
            executeInterval 1;
            writeControl outputTimeAndEnd;
            writeInterval 1;
            operations
            (
                {
                    operation Cp;
                    fieldName Cp;
                    write true;
                    nearCellValue true;
                    p p;
                    Uref 1.0;
                }
            );
            functionObjectLibs ( "libfieldFunctionObjects.so" );
        }
        IM
        {
            type runTimeVisualisation;
            regions ( region0 );
            functionObjectLibs ( "librunTimeVisualisation.so" );
            activeScenes ( transform-symmetry );
            width 1024;
            height 768;
            exportFormats ( png );
            debug true;
            parallel true;
            writeControl writeTime;
            writeInterval 1;
            executeControl writeTime;
            executeInterval 1;
            #include "postDict";
        }
    }
"""
    expected = {
        "FoamFile": {
            "version": "2.0",
            "format": "ascii",
            "class": "dictionary",
            "location": "system",
            "object": "controlDict",
        },
        "application": "pimpleDyMFoam",
        "startFrom": "latestTime",
        "startTime": "0",
        "stopAt": "endTime",
        "endTime": "10.0",
        "deltaT": "0.01",
        "writeControl": "adjustableRunTime",
        "writeInterval": "0.2",
        "purgeWrite": "0",
        "writeFormat": "binary",
        "writePrecision": "10",
        "writeCompression": "uncompressed",
        "writeEndTime": "true",
        "timeFormat": "general",
        "timePrecision": "6",
        "graphFormat": "raw",
        "runTimeModifiable": "yes",
        "adjustTimeStep": "true",
        "maxCo": "1.0",
        "maxDeltaT": "1.0",
        "maxAlphaCo": "0.0",
        "minDeltaT": "1.0E-6",
        "functions": {
            "FP": {
                "type": "fieldProcess",
                "regions": ["region0"],
                "executeControl": "writeTime",
                "executeInterval": "1",
                "writeControl": "outputTimeAndEnd",
                "writeInterval": "1",
                "operations": [
                    {
                        "operation": "Cp",
                        "fieldName": "Cp",
                        "write": "true",
                        "nearCellValue": "true",
                        "p": "p",
                        "Uref": "1.0",
                    }
                ],
                "functionObjectLibs": ["libfieldFunctionObjects.so"],
            },
            "IM": {
                "type": "runTimeVisualisation",
                "regions": ["region0"],
                "functionObjectLibs": ["librunTimeVisualisation.so"],
                "activeScenes": ["transform-symmetry"],
                "width": "1024",
                "height": "768",
                "exportFormats": ["png"],
                "debug": "true",
                "parallel": "true",
                "writeControl": "writeTime",
                "writeInterval": "1",
                "executeControl": "writeTime",
                "executeInterval": "1",
                "#includes": ['"postDict"'],
            },
        },
    }
    actual = parse(input)
    assert actual == expected
