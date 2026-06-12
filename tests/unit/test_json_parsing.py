
import pytest

from workflow.parsing import parse_json_response


def test_parse_json_response_with_extra_data():
    raw_response = """
{
  "key": "value"
}
This is some extra text that would normally cause an 'Extra data' error.
"""
    result = parse_json_response(raw_response)
    assert result == {"key": "value"}

def test_parse_json_response_with_markdown_fence():
    raw_response = """
```json
{
  "key": "value"
}
```
"""
    result = parse_json_response(raw_response)
    assert result == {"key": "value"}

def test_parse_json_response_with_multiple_objects():
    raw_response = """
{ "first": 1 }
{ "second": 2 }
"""
    result = parse_json_response(raw_response)
    assert result == {"first": 1}

def test_parse_json_response_no_json():
    raw_response = "Just some text with no braces"
    with pytest.raises(ValueError, match="Agent response did not contain a JSON object"):
        parse_json_response(raw_response)

def test_parse_json_response_repairs_single_quotes():
    raw_response = "{ 'invalid': 'quotes' }"
    assert parse_json_response(raw_response) == {"invalid": "quotes"}


def test_parse_json_response_repairs_invalid_latex_escape():
    raw_response = r'{"formula": "\alpha + \beta"}'
    assert parse_json_response(raw_response)["formula"] == r"\alpha + \beta"
