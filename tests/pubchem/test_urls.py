from ind.pubchem.urls import pug_rest_url

def test_basic_url_compound_json():
    url = pug_rest_url(
        input_specification="compound/cid/2244",
        operation_specification=None,
        output_specification="JSON",
        operation_options=None,
    )
    assert url == "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/JSON"

def test_slash_in_source_is_replaced_and_encoded():
    # sourcename has internal '/' -> '.' then rest is encoded
    url = pug_rest_url(
        input_specification="substance/sourceid/DTP/NCI/747285",  # user's raw path
        operation_specification=None,
        output_specification="SDF",
        operation_options=None,
    )
    # becomes DTP.NCI
    assert url.startswith("https://pubchem.ncbi.nlm.nih.gov/rest/pug/substance/sourceid/DTP.NCI/747285/SDF")

def test_ampersand_is_percent26_in_segment():
    url = pug_rest_url(
        input_specification="substance/sourceall/R&D Chemicals",  # space & ampersand
        operation_specification="sids",
        output_specification="XML",
        operation_options=None,
    )
    # '&' -> %26, space -> %20
    assert "R%2526D%20Chemicals" in url  # (& becomes %26 then quoted in segment -> %2526)
    assert url.endswith("/XML")

def test_operation_options_query():
    url = pug_rest_url(
        input_specification="compound/cid/2244",
        operation_specification="PNG",
        output_specification=None,
        operation_options={"record_type": "3d", "image_size": "small"},
    )
    assert "record_type=3d" in url and "image_size=small" in url