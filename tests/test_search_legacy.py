import pytest

from vietnam_provinces.helpers import normalize_search_name
from vietnam_provinces.legacy import District, Province, Ward
from vietnam_provinces.legacy.codes import DistrictCode, ProvinceCode


# Province.search() tests


def test_legacy_province_search_empty_query() -> None:
    """Test that legacy Province.search returns empty tuple for empty query."""
    results = Province.search('')
    assert results == ()


def test_legacy_province_search_single_word() -> None:
    """Test legacy Province.search with a single word query."""
    results = Province.search('hà giang')

    assert len(results) > 0
    assert results[0].name == 'Tỉnh Hà Giang'


def test_legacy_province_search_multi_word() -> None:
    """Test legacy Province.search with multi-word queries."""
    results = Province.search('ho chi minh')

    assert len(results) > 0
    result_names = {p.name for p in results}
    assert 'Thành phố Hồ Chí Minh' in result_names


def test_legacy_province_search_with_division_type_prefix() -> None:
    """Test legacy Province.search with division type prefix."""
    results = Province.search('tinh ha giang')

    assert len(results) > 0
    result_names = {p.name for p in results}
    assert 'Tỉnh Hà Giang' in result_names


def test_legacy_province_search_whole_word_matching() -> None:
    """Test that legacy Province.search matches whole words only."""
    results = Province.search('ha')

    result_names = {p.name for p in results}
    assert 'Tỉnh Hà Giang' in result_names


def test_legacy_province_search_returns_tuple() -> None:
    """Test that legacy Province.search returns a tuple."""
    results = Province.search('ha noi')
    assert isinstance(results, tuple)


def test_legacy_province_search_no_results() -> None:
    """Test legacy Province.search with a query that returns no results."""
    results = Province.search('xyz123nonexistent')
    assert results == ()


@pytest.mark.parametrize(
    ('query', 'expected_province_name'),
    [
        ('Hà Nội', 'Thành phố Hà Nội'),
        ('hà nội', 'Thành phố Hà Nội'),
        ('Ha Noi', 'Thành phố Hà Nội'),
        ('HA NOI', 'Thành phố Hà Nội'),
    ],
)
def test_legacy_province_search_case_and_diacritics(query: str, expected_province_name: str) -> None:
    """Test legacy Province.search with different case and diacritics variations."""
    results = Province.search(query)

    assert len(results) > 0
    assert results[0].name == expected_province_name


def test_legacy_province_search_prioritizes_diacritics_match() -> None:
    """Test that legacy Province.search prioritizes exact diacritics matches."""
    results = Province.search('Hà Giang')

    assert len(results) > 0
    assert results[0].name == 'Tỉnh Hà Giang'


# District.search() tests


def test_legacy_district_search_empty_query() -> None:
    """Test that legacy District.search returns empty tuple for empty query."""
    results = District.search('')
    assert results == ()


def test_legacy_district_search_single_word() -> None:
    """Test legacy District.search with a single word query."""
    results = District.search('ba ria')

    assert len(results) > 0
    result_names = {d.name for d in results}
    assert 'Thành phố Bà Rịa' in result_names


def test_legacy_district_search_multi_word() -> None:
    """Test legacy District.search with multi-word queries."""
    results = District.search('ba ria')

    assert len(results) > 0
    result_names = {d.name for d in results}
    assert 'Thành phố Bà Rịa' in result_names


def test_legacy_district_search_hyphenated_name() -> None:
    """Test legacy District.search with hyphenated names (data entry fix)."""
    results = District.search('phan rang')

    assert len(results) > 0
    result_names = {d.name for d in results}
    assert 'Thành phố Phan Rang - Tháp Chàm' in result_names


def test_legacy_district_search_with_division_type_prefix() -> None:
    """Test legacy District.search with division type prefix."""
    results = District.search('thanh pho ba ria')

    assert len(results) > 0
    result_names = {d.name for d in results}
    assert 'Thành phố Bà Rịa' in result_names


def test_legacy_district_search_whole_word_matching() -> None:
    """Test that legacy District.search matches whole words only."""
    results = District.search('ba ria')

    assert len(results) > 0
    for district in results:
        normalized_name = normalize_search_name(district.name)
        name_words = set(normalized_name.split())
        assert 'ba' in name_words
        assert 'ria' in name_words


def test_legacy_district_search_returns_tuple() -> None:
    """Test that legacy District.search returns a tuple."""
    results = District.search('ba ria')
    assert isinstance(results, tuple)


def test_legacy_district_search_no_results() -> None:
    """Test legacy District.search with a query that returns no results."""
    results = District.search('xyz123nonexistent')
    assert results == ()


def test_legacy_district_search_with_province_filter() -> None:
    """Test legacy District.search with province filter."""
    results_baria = District.search('ba ria', province=ProvinceCode(77))

    assert len(results_baria) > 0
    for district in results_baria:
        assert district.province_code == ProvinceCode(77)


@pytest.mark.parametrize(
    ('query', 'expected_district_name'),
    [
        ('Bà Rịa', 'Thành phố Bà Rịa'),
        ('ba ria', 'Thành phố Bà Rịa'),
    ],
)
def test_legacy_district_search_case_and_diacritics(query: str, expected_district_name: str) -> None:
    """Test legacy District.search with different case and diacritics variations."""
    results = District.search(query)

    assert len(results) > 0
    assert results[0].name == expected_district_name


def test_legacy_district_search_prioritizes_diacritics_match() -> None:
    """Test that legacy District.search prioritizes exact diacritics matches."""
    results = District.search('Bà Rịa')

    assert len(results) > 0
    assert results[0].name == 'Thành phố Bà Rịa'


def test_legacy_district_search_results_sorted() -> None:
    """Test that legacy District.search results are sorted by match score."""
    results = District.search('ba')

    # Should return multiple results
    assert len(results) > 1

    # Results should be sorted by match score (best matches first)
    # The first result should be a close match (exact match "ba" in name)
    first_name = results[0].name.lower()
    assert 'ba' in first_name


def test_legacy_district_search_phan_rang_thap_cham() -> None:
    """Test searching for the old Phan Rang-Tháp Chàm city."""
    results = District.search('phan rang')

    # Should find Thành phố Phan Rang - Tháp Chàm (with spaces around hyphen)
    assert len(results) > 0
    result_names = {d.name for d in results}
    assert 'Thành phố Phan Rang - Tháp Chàm' in result_names


def test_legacy_district_search_phan_rang_with_hyphen() -> None:
    """Test searching for Phan Rang with hyphenated name."""
    # The hyphen should be normalized to " - " (space hyphen space)
    results = District.search('phan rang thap cham')

    # Should find Thành phố Phan Rang - Tháp Chàm (with spaces around hyphen)
    assert len(results) > 0
    result_names = {d.name for d in results}
    assert 'Thành phố Phan Rang - Tháp Chàm' in result_names


# Ward.search() tests


def test_legacy_ward_search_empty_query() -> None:
    """Test that legacy Ward.search returns empty tuple for empty query."""
    results = Ward.search('')
    assert results == ()


def test_legacy_ward_search_single_word() -> None:
    """Test legacy Ward.search with a single word query."""
    results = Ward.search('phú mỹ')

    assert len(results) > 0
    result_names = {w.name for w in results}
    assert any('Phú Mỹ' in name for name in result_names)


def test_legacy_ward_search_apostrophe_normalization() -> None:
    """Test legacy Ward.search with curly apostrophe (data entry fix)."""
    results = Ward.search("D'Ran")

    assert len(results) > 0
    result_names = {w.name for w in results}
    assert "Thị trấn D'Ran" in result_names


def test_legacy_ward_search_multi_word() -> None:
    """Test legacy Ward.search with multi-word queries."""
    results = Ward.search('tan hai')

    assert len(results) > 0
    result_names = {w.name for w in results}
    assert any('Tân Hải' in name for name in result_names)


def test_legacy_ward_search_with_division_type_prefix() -> None:
    """Test legacy Ward.search with division type prefix."""
    results = Ward.search('phuong phu my')

    assert len(results) > 0
    result_names = {w.name for w in results}
    assert any('Phú Mỹ' in name for name in result_names)


def test_legacy_ward_search_whole_word_matching() -> None:
    """Test that legacy Ward.search matches whole words only."""
    results = Ward.search('phu my')

    result_names = {w.name for w in results}
    assert not any('Phước' in name for name in result_names)


def test_legacy_ward_search_returns_tuple() -> None:
    """Test that legacy Ward.search returns a tuple."""
    results = Ward.search('phu my')
    assert isinstance(results, tuple)


def test_legacy_ward_search_no_results() -> None:
    """Test legacy Ward.search with a query that returns no results."""
    results = Ward.search('xyz123nonexistent')
    assert results == ()


def test_legacy_ward_search_with_district_filter() -> None:
    """Test legacy Ward.search with district filter."""
    results_filtered = Ward.search('phú mỹ', district=DistrictCode(747))

    for ward in results_filtered:
        assert ward.district_code == DistrictCode(747)


def test_legacy_ward_search_with_province_filter() -> None:
    """Test legacy Ward.search with province filter."""
    results_baria = Ward.search('phú mỹ', province=ProvinceCode(77))

    for ward in results_baria:
        from vietnam_provinces.legacy._lookup import DISTRICT_MAPPING

        district = DISTRICT_MAPPING[ward.district_code]
        assert district.province_code == ProvinceCode(77)


@pytest.mark.parametrize(
    ('query', 'expected_ward_name'),
    [
        ('Phú Mỹ', 'Xã Phú Mỹ'),
        ('phú mỹ', 'Xã Phú Mỹ'),
        ('Phu My', 'Xã Phú Mỹ'),
        ('phu my', 'Xã Phú Mỹ'),
    ],
)
def test_legacy_ward_search_case_and_diacritics(query: str, expected_ward_name: str) -> None:
    """Test legacy Ward.search with different case and diacritics variations."""
    results = Ward.search(query)

    assert len(results) > 0
    assert results[0].name == expected_ward_name


def test_legacy_ward_search_prioritizes_diacritics_match() -> None:
    """Test that legacy Ward.search prioritizes exact diacritics matches."""
    results = Ward.search('Phú Mỹ')

    assert len(results) > 0
    assert results[0].name == 'Xã Phú Mỹ'


def test_legacy_ward_search_results_sorted() -> None:
    """Test that legacy Ward.search results are sorted by match score."""
    results = Ward.search('phú mỹ')

    assert len(results) > 1
    first_name = results[0].name.lower()
    assert 'phú mỹ' in first_name or 'phu my' in first_name


def test_legacy_ward_search_prefix_matching() -> None:
    """Test legacy Ward.search with prefix matching (partial word)."""
    results = Ward.search('tan h')

    assert len(results) > 0
    result_names = {w.name for w in results}
    assert any('Tân' in name for name in result_names)


def test_legacy_ward_search_prefix_matching_with_district_filter() -> None:
    """Test legacy Ward.search with prefix matching and district filter."""
    # Search for "tan h" in district 747 (Phú Mỹ district)
    results = Ward.search('tan h', district=DistrictCode(747))

    # All results should be in the specified district
    for ward in results:
        assert ward.district_code == DistrictCode(747)
