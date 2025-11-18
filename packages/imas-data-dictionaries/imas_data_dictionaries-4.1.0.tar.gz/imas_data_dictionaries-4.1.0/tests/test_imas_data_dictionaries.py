import imas_data_dictionaries


def test_get_versions():
    dd_versions = imas_data_dictionaries.dd_xml_versions()
    assert len(dd_versions) > 0
    assert "4.0.0" in dd_versions


def test_get_xml():
    data = imas_data_dictionaries.get_dd_xml("4.0.0")
    assert type(data) is bytes
    assert len(data) == 21171649


def test_get_xml_crc():
    assert imas_data_dictionaries.get_dd_xml_crc("4.0.0") == 3271325832


def test_get_identifiers():
    identifiers = imas_data_dictionaries.dd_identifiers()
    assert len(identifiers) > 0
    assert "coordinate_identifier" in identifiers


def test_get_identifier_xml():
    data = imas_data_dictionaries.get_identifier_xml("coordinate_identifier")
    assert type(data) is bytes
    assert len(data) > 0
