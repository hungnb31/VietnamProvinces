import pytest

from vietnam_provinces import Province, Ward
from vietnam_provinces.codes import ProvinceCode, WardCode
from vietnam_provinces.helpers import normalize_search_name
from vietnam_provinces.legacy import Province as LegacyProvince
from vietnam_provinces.legacy import Ward as LegacyWard


@pytest.mark.parametrize(
    ('query', 'expected_first'),
    [
        ('phú mỹ', 'Thị trấn Phú Mỹ'),
        ('Phú Mỹ', 'Thị trấn Phú Mỹ'),
        ('phường phú mỹ', 'Phường Phú Mỹ'),
    ],
)
def test_search_from_legacy_by_name_prioritizes_diacritics_match(query: str, expected_first: str) -> None:
    """Test that search results prioritize exact diacritics matches."""
    results = Ward.search_from_legacy(query)

    # Should return results
    assert len(results) > 0

    # The first result should be one with the expected_first old name
    old_names = [w.name for w in results[0].ward.get_legacy_sources()]
    assert expected_first in old_names, (
        f"First result should have old name '{expected_first}', but got ward with old names {old_names}"
    )


@pytest.mark.parametrize(
    ('legacy_code', 'expected_ward_name'),
    [
        (26707, 'Phường Tân Hải'),  # Phường Tân Hòa (legacy) -> Phường Tân Hải (new)
        (4, 'Phường Ba Đình'),  # Legacy ward -> Phường Ba Đình (new)
        (26731, 'Xã Châu Pha'),  # Xã Tóc Tiên (legacy, Phú Mỹ) -> Xã Châu Pha (new)
        (26725, 'Phường Tân Thành'),  # Phường Hắc Dịch (legacy, Phú Mỹ) -> Phường Tân Thành (new)
    ],
)
def test_search_from_legacy_by_code(legacy_code: int, expected_ward_name: str) -> None:
    """Test that search_from_legacy returns correct ward when searching by legacy code."""
    results = Ward.search_from_legacy(code=legacy_code)

    # Should return results (may be multiple if partly merged)
    assert len(results) > 0

    # The first result should have the expected name
    assert results[0].source_code == legacy_code
    assert results[0].ward.name == expected_ward_name


@pytest.mark.parametrize(
    ('legacy_name', 'expected_ward_name'),
    [
        ('toc tien', 'Xã Châu Pha'),  # Xã Tóc Tiên (legacy) -> Xã Châu Pha (new)
        ('Tóc Tiên', 'Xã Châu Pha'),  # Search with diacritics
        ('hac dich', 'Phường Tân Thành'),  # Phường Hắc Dịch (legacy) -> Phường Tân Thành (new)
        ('Hắc Dịch', 'Phường Tân Thành'),  # Search with diacritics
        ("D'Ran", "Xã D'Ran"),  # D'Ran with straight apostrophe
        ('dran', "Xã D'Ran"),  # dran without apostrophe
    ],
)
def test_search_from_legacy_by_name_specific_wards(legacy_name: str, expected_ward_name: str) -> None:
    """Test that search_from_legacy returns correct ward when searching by specific legacy ward names."""
    results = Ward.search_from_legacy(name=legacy_name)

    # Should return results
    assert len(results) > 0

    # The first result should have the expected name
    assert results[0].ward.name == expected_ward_name


@pytest.mark.parametrize(
    ('ward_code', 'expected_old_ward_name'),
    [
        (4, 'Phường Trúc Bạch'),  # Phường Ba Đình - merged from multiple wards
        (859, 'Xã Ngọc Long'),  # Merged from Xã Ngọc Long (single source)
    ],
)
def test_get_legacy_sources_returns_legacy_wards(ward_code: int, expected_old_ward_name: str) -> None:
    """Test that get_legacy_sources returns legacy wards for a merged ward."""
    ward = Ward.from_code(WardCode(ward_code))
    legacy_sources = ward.get_legacy_sources()

    # Should have legacy sources
    assert len(legacy_sources) > 0

    # Check that all returned items are legacy Ward objects

    for lw in legacy_sources:
        assert isinstance(lw, LegacyWard)

    # Check that expected old ward name is in the legacy sources
    old_names = {lw.name for lw in legacy_sources}
    assert expected_old_ward_name in old_names


@pytest.mark.parametrize(
    ('ward_code', 'expected_codes'),
    [
        (4, {4, 13, 16, 19, 22, 28, 40, 55, 73, 112}),  # Phường Ba Đình - merged from multiple wards
        (859, {859}),  # Merged from Xã Ngọc Long (single source)
        (919, {919}),  # Another ward with single source
    ],
)
def test_get_legacy_sources_has_correct_codes(ward_code: int, expected_codes: set[int]) -> None:
    """Test that get_legacy_sources returns wards with correct codes."""
    ward = Ward.from_code(WardCode(ward_code))
    legacy_sources = ward.get_legacy_sources()

    # Verify all legacy sources have the expected codes
    actual_codes = {lw.code.value for lw in legacy_sources}
    assert actual_codes == expected_codes


@pytest.mark.parametrize(
    'ward_code',
    [
        4,  # Phường Ba Đình
        859,  # Xã Ngọc Long (single source)
    ],
)
def test_get_legacy_sources_returns_tuple(ward_code: int) -> None:
    """Test that get_legacy_sources returns a tuple."""
    ward = Ward.from_code(WardCode(ward_code))
    legacy_sources = ward.get_legacy_sources()

    # Should return a tuple (not None, not list)
    assert isinstance(legacy_sources, tuple)


# Province tests


@pytest.mark.parametrize(
    ('legacy_code', 'expected_province_name'),
    [
        (77, 'Thành phố Hồ Chí Minh'),  # Tỉnh Bà Rịa - Vũng Tàu (legacy) -> Thành phố Hồ Chí Minh (new)
        (2, 'Tỉnh Tuyên Quang'),  # Tỉnh Hà Giang (legacy) -> merged into Tỉnh Tuyên Quang (new)
        (54, 'Tỉnh Đắk Lắk'),  # Tỉnh Phú Yên (legacy) -> merged into Tỉnh Đắk Lắk (new)
    ],
)
def test_province_search_from_legacy_by_code(legacy_code: int, expected_province_name: str) -> None:
    """Test that Province.search_from_legacy returns correct province when searching by legacy code."""
    results = Province.search_from_legacy(code=legacy_code)

    # Should return exactly one result for this case
    assert len(results) == 1

    # The result should have the expected name
    assert results[0].source_code == legacy_code
    assert results[0].province.name == expected_province_name


@pytest.mark.parametrize(
    ('legacy_name', 'expected_province_name'),
    [
        ('ha giang', 'Tỉnh Tuyên Quang'),  # Tỉnh Hà Giang (legacy) -> merged into Tỉnh Tuyên Quang
        ('Hà Giang', 'Tỉnh Tuyên Quang'),  # Search with diacritics
        ('phu yen', 'Tỉnh Đắk Lắk'),  # Tỉnh Phú Yên (legacy) -> merged into Tỉnh Đắk Lắk
        ('Phú Yên', 'Tỉnh Đắk Lắk'),  # Search with diacritics
    ],
)
def test_province_search_from_legacy_by_name(legacy_name: str, expected_province_name: str) -> None:
    """Test that Province.search_from_legacy returns correct province when searching by legacy name."""
    results = Province.search_from_legacy(name=legacy_name)

    # Should return results
    assert len(results) > 0

    # The first result should be the expected province
    assert results[0].province.name == expected_province_name


@pytest.mark.parametrize(
    ('province_code', 'expected_old_province_name'),
    [
        (
            79,
            'Tỉnh Bà Rịa - Vũng Tàu',
        ),  # Thành phố Hồ Chí Minh - merged from multiple provinces including Bà Rịa - Vũng Tàu
        (8, 'Tỉnh Hà Giang'),  # Tỉnh Tuyên Quang - merged from Tỉnh Hà Giang and Tỉnh Tuyên Quang
        (66, 'Tỉnh Phú Yên'),  # Tỉnh Đắk Lắk - merged from Tỉnh Phú Yên and Tỉnh Đắk Lắk
    ],
)
def test_province_get_legacy_sources_returns_legacy_provinces(
    province_code: int, expected_old_province_name: str
) -> None:
    """Test that Province.get_legacy_sources returns legacy provinces for a merged province."""
    province = Province.from_code(ProvinceCode(province_code))
    legacy_sources = province.get_legacy_sources()

    # Should have legacy sources
    assert len(legacy_sources) > 0

    # Check that all returned items are legacy Province objects

    for lp in legacy_sources:
        assert isinstance(lp, LegacyProvince)

    # Check that expected old province name is in the legacy sources
    old_names = {lp.name for lp in legacy_sources}
    assert expected_old_province_name in old_names


@pytest.mark.parametrize(
    ('province_code', 'expected_codes'),
    [
        (79, {74, 77, 79}),  # Thành phố Hồ Chí Minh - merged from multiple provinces
        (8, {2, 8}),  # Tỉnh Tuyên Quang - merged from Tỉnh Hà Giang and Tỉnh Tuyên Quang
        (66, {54, 66}),  # Tỉnh Đắk Lắk - merged from Tỉnh Phú Yên and Tỉnh Đắk Lắk
    ],
)
def test_province_get_legacy_sources_has_correct_codes(province_code: int, expected_codes: set[int]) -> None:
    """Test that Province.get_legacy_sources returns provinces with correct codes."""
    province = Province.from_code(ProvinceCode(province_code))
    legacy_sources = province.get_legacy_sources()

    # Verify all legacy sources have the expected codes
    actual_codes = {lp.code.value for lp in legacy_sources}
    assert actual_codes == expected_codes


@pytest.mark.parametrize(
    'province_code',
    [
        79,  # Thành phố Hồ Chí Minh
        8,  # Tỉnh Tuyên Quang
        66,  # Tỉnh Đắk Lắk
    ],
)
def test_province_get_legacy_sources_returns_tuple(province_code: int) -> None:
    """Test that Province.get_legacy_sources returns a tuple."""
    province = Province.from_code(ProvinceCode(province_code))
    legacy_sources = province.get_legacy_sources()

    # Should return a tuple (not None, not list)
    assert isinstance(legacy_sources, tuple)


# District tests


@pytest.mark.parametrize(
    ('legacy_district_code', 'expected_ward_names'),
    [
        (748, ['Phường Bà Rịa', 'Phường Long Hương', 'Phường Tam Long']),  # Thành phố Bà Rịa
    ],
)
def test_search_from_legacy_district_by_code(legacy_district_code: int, expected_ward_names: list[str]) -> None:
    """Test that search_from_legacy_district returns correct wards when searching by legacy district code."""
    results = Ward.search_from_legacy_district(code=legacy_district_code)

    # Should return results
    assert len(results) > 0

    # Check that expected ward names are in the results
    result_names = {w.ward.name for w in results}
    for expected_name in expected_ward_names:
        assert expected_name in result_names


@pytest.mark.parametrize(
    ('legacy_district_name', 'expected_ward_name'),
    [
        ('ba ria', 'Phường Bà Rịa'),  # Thành phố Bà Rịa (without diacritics)
        ('Bà Rịa', 'Phường Bà Rịa'),  # Search with diacritics
    ],
)
def test_search_from_legacy_district_by_name(legacy_district_name: str, expected_ward_name: str) -> None:
    """Test that search_from_legacy_district returns correct wards when searching by legacy district name."""
    results = Ward.search_from_legacy_district(name=legacy_district_name)

    # Should return results
    assert len(results) > 0

    # Check that expected ward name is in the results
    result_names = {w.ward.name for w in results}
    assert expected_ward_name in result_names


def test_search_from_legacy_district_empty_query() -> None:
    """Test that search_from_legacy_district returns empty tuple for empty query."""
    results = Ward.search_from_legacy_district()
    assert results == ()


def test_search_from_legacy_district_invalid_code() -> None:
    """Test that search_from_legacy_district returns empty tuple for invalid district code."""
    results = Ward.search_from_legacy_district(code=99999)
    assert results == ()


class TestPhanRangThapCham:
    """Test cases for Phan Rang - Tháp Chàm (old city dissolved to wards in 2025)."""

    def test_search_from_legacy_district_by_code_phan_rang(self) -> None:
        """Test finding new wards from old Phan Rang-Tháp Chàm by district code."""
        # District code 582 was Thành phố Phan Rang-Tháp Chàm
        results = Ward.search_from_legacy_district(code=582)

        # Should return 6 new wards
        assert len(results) == 6

        # Check expected ward names
        result_names = {w.ward.name for w in results}
        expected_names = {
            'Phường Đô Vinh',
            'Phường Bảo An',
            'Phường Phan Rang',
            'Phường Đông Hải',
            'Phường Ninh Chử',
            'Xã Phước Dinh',
        }
        assert result_names == expected_names

    def test_search_from_legacy_district_by_name_phan_rang(self) -> None:
        """Test finding new wards from old Phan Rang-Tháp Chàm by district name."""
        results = Ward.search_from_legacy_district(name='phan rang')

        # Should return 6 new wards
        assert len(results) == 6

        # Check expected ward names
        result_names = {w.ward.name for w in results}
        expected_names = {
            'Phường Đô Vinh',
            'Phường Bảo An',
            'Phường Phan Rang',
            'Phường Đông Hải',
            'Phường Ninh Chử',
            'Xã Phước Dinh',
        }
        assert result_names == expected_names

    def test_search_from_legacy_district_phan_rang_with_diacritics(self) -> None:
        """Test finding new wards from old Phan Rang-Tháp Chàm with diacritics."""
        # Search with diacritics but without hyphen
        results = Ward.search_from_legacy_district(name='Phan Rang')

        # Should return 6 new wards
        assert len(results) == 6

        # Check that Phường Phan Rang is in results
        result_names = {w.ward.name for w in results}
        assert 'Phường Phan Rang' in result_names


# Ward.search() tests


def test_ward_search_empty_query() -> None:
    """Test that Ward.search returns empty tuple for empty query."""
    results = Ward.search('')
    assert results == ()


def test_ward_search_single_word() -> None:
    """Test Ward.search with a single word query."""
    results = Ward.search('phú mỹ')

    # Should return results
    assert len(results) > 0

    # All results should contain the query words (normalized comparison)
    # Normalized form of 'phú mỹ' is 'phu my'

    for ward in results:
        normalized_name = normalize_search_name(ward.name)
        assert 'phu' in normalized_name
        assert 'my' in normalized_name


@pytest.mark.parametrize(
    ('query', 'expected_ward_name'),
    [
        ('phú mỹ', 'Xã Phú Mỹ'),  # Exact match with diacritics
        ('Phú Mỹ', 'Xã Phú Mỹ'),  # Case insensitive with diacritics
        ('phu my', 'Xã Phú Mỹ'),  # Without diacritics
        ('Phu My', 'Xã Phú Mỹ'),  # Case insensitive without diacritics
    ],
)
def test_ward_search_prioritizes_diacritics_match(query: str, expected_ward_name: str) -> None:
    """Test that Ward.search prioritizes exact diacritics matches."""
    results = Ward.search(query)

    # Should return results
    assert len(results) > 0

    # The first result should be the expected ward
    assert results[0].name == expected_ward_name


@pytest.mark.parametrize(
    ('query', 'expected_in_results'),
    [
        ('tan hai', ['Xã Tân Hải', 'Phường Tân Hải']),  # Multi-word without diacritics
        ('Tân Hải', ['Xã Tân Hải', 'Phường Tân Hải']),  # Multi-word with diacritics
        ('phuong tan hai', ['Phường Tân Hải']),  # With division type prefix
        ('xa tan hai', ['Xã Tân Hải']),  # With division type prefix
        ('tan h', ['Xã Tân Hải', 'Phường Tân Hải']),  # Prefix matching for second word
    ],
)
def test_ward_search_multi_word(query: str, expected_in_results: list[str]) -> None:
    """Test Ward.search with multi-word queries."""
    results = Ward.search(query)

    # Should return results
    assert len(results) > 0

    # Check that expected wards are in results
    result_names = {w.name for w in results}
    for expected_name in expected_in_results:
        assert expected_name in result_names, f"Expected '{expected_name}' in results, got {result_names}"


def test_ward_search_multi_word_requires_all_words() -> None:
    """Test that Ward.search requires all words to match for multi-word queries."""
    # Search for "phu my" - both words must be present
    results = Ward.search('phu my')

    # Should return results
    assert len(results) > 0

    # All results should contain both "phu" and "my" as whole words in normalized form

    for ward in results:
        normalized_name = normalize_search_name(ward.name)
        name_words = set(normalized_name.split())
        assert 'phu' in name_words, f"Expected 'phu' as whole word in '{name_words}' for ward '{ward.name}'"
        assert 'my' in name_words, f"Expected 'my' as whole word in '{name_words}' for ward '{ward.name}'"


def test_ward_search_whole_word_matching() -> None:
    """Test that Ward.search matches whole words only, not substrings."""
    # Search for "phu my" - should NOT match "phuoc" (which contains "phu" as substring)
    results = Ward.search('phu my')

    result_names = {w.name for w in results}

    # These should NOT be in results because "phuoc" != "phu"
    assert 'Xã Phước Mỹ Trung' not in result_names, "'phuoc' should not match 'phu'"
    assert 'Phường Mỹ Phước Tây' not in result_names, "'phuoc' should not match 'phu'"


def test_ward_search_with_apostrophe() -> None:
    """Test Ward.search with apostrophe in query."""
    results = Ward.search("D'Ran")

    # Should return results
    assert len(results) > 0

    # Should find Xã D'Ran (with straight apostrophe)
    result_names = {w.name for w in results}
    assert "Xã D'Ran" in result_names  # Straight apostrophe (U+0027)


def test_ward_search_returns_tuple() -> None:
    """Test that Ward.search returns a tuple."""
    results = Ward.search('phu my')

    # Should return a tuple (not None, not list)
    assert isinstance(results, tuple)


def test_ward_search_with_province_filter() -> None:
    """Test that Ward.search can filter by province."""
    # Test filtering by province
    results_all = Ward.search('phu my')
    results_hcmc = Ward.search('phu my', province=ProvinceCode(79))  # Hồ Chí Minh City

    # Filtered results should be a subset of all results
    assert len(results_hcmc) <= len(results_all)

    # All filtered results should be from the specified province
    if results_hcmc:
        assert all(ward.province_code == ProvinceCode(79) for ward in results_hcmc)

    # Test with a province that has matching wards
    results_gialai = Ward.search('phu my', province=ProvinceCode(52))  # Gia Lai
    assert len(results_gialai) > 0
    assert all(ward.province_code == ProvinceCode(52) for ward in results_gialai)

    # Test with empty results
    results_empty = Ward.search('nonexistent', province=ProvinceCode(79))
    assert results_empty == ()


def test_ward_search_no_results() -> None:
    """Test Ward.search with a query that returns no results."""
    results = Ward.search('xyz123nonexistent')

    # Should return empty tuple
    assert results == ()


def test_ward_search_results_sorted_by_match_score() -> None:
    """Test that Ward.search results are sorted by match score (best matches first)."""
    results = Ward.search('phu my')

    # Should return multiple results
    assert len(results) > 1

    # Exact matches should come before partial matches
    # The first result should be an exact or close match
    first_result = results[0]
    normalized_first = first_result.name.lower().replace('xã ', '').replace('phường ', '')

    # First result should start with "phú mỹ" or be very close
    assert normalized_first.startswith('phú mỹ') or normalized_first.startswith('phu my')
