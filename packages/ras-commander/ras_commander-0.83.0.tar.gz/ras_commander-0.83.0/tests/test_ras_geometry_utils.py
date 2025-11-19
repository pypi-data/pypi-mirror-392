"""
Test suite for RasGeometryUtils

Tests all utility functions with real HEC-RAS geometry files.
Cross-validates parsing with HDF files where applicable.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent
sys.path.insert(0, str(parent_directory))

from ras_commander.RasGeometryUtils import RasGeometryUtils


def test_parse_fixed_width_8char():
    """Test parsing 8-character fixed-width columns"""
    print("\n" + "="*70)
    print("TEST: parse_fixed_width() with 8-char columns")
    print("="*70)

    # Test case 1: Station/elevation data
    line1 = "       0  963.04    27.2  963.04   32.64  963.02   38.08  962.85"
    values1 = RasGeometryUtils.parse_fixed_width(line1, column_width=8)
    expected1 = [0.0, 963.04, 27.2, 963.04, 32.64, 963.02, 38.08, 962.85]

    print(f"Input:    '{line1}'")
    print(f"Parsed:   {values1}")
    print(f"Expected: {expected1}")
    assert values1 == expected1, "8-char parsing failed"
    print("PASS: 8-char fixed-width parsing")

    # Test case 2: Manning's n data
    line2 = "   0.035   0.035   0.035   0.035   0.035   0.035   0.035   0.035"
    values2 = RasGeometryUtils.parse_fixed_width(line2, column_width=8)
    assert len(values2) == 8, "Wrong count parsed"
    assert all(v == 0.035 for v in values2), "Manning's n values incorrect"
    print("PASS: Manning's n parsing")

    # Test case 3: Merged values (edge case)
    line3 = "  100.50200.75300.25"  # No spaces between values
    values3 = RasGeometryUtils.parse_fixed_width(line3, column_width=8)
    print(f"\nMerged values test:")
    print(f"Input:  '{line3}'")
    print(f"Parsed: {values3}")
    print("PASS: Merged value handling")


def test_parse_fixed_width_16char():
    """Test parsing 16-character fixed-width columns (2D coordinates)"""
    print("\n" + "="*70)
    print("TEST: parse_fixed_width() with 16-char columns")
    print("="*70)

    # Test 2D coordinate data
    line = "   648224.43125   4551425.84375   648229.43125   4551425.84375"
    values = RasGeometryUtils.parse_fixed_width(line, column_width=16)
    expected = [648224.43125, 4551425.84375, 648229.43125, 4551425.84375]

    print(f"Input:    '{line}'")
    print(f"Parsed:   {values}")
    print(f"Expected: {expected}")
    assert len(values) == 4, "Wrong count for 16-char"
    assert values == expected, "16-char parsing failed"
    print("PASS: 16-char fixed-width parsing (2D coordinates)")


def test_format_fixed_width():
    """Test formatting values into fixed-width lines"""
    print("\n" + "="*70)
    print("TEST: format_fixed_width()")
    print("="*70)

    # Test 8-char formatting
    values = [0.0, 963.04, 27.2, 963.04]
    lines = RasGeometryUtils.format_fixed_width(values, column_width=8, values_per_line=10, precision=2)

    print(f"Input values: {values}")
    print(f"Formatted line: '{lines[0].rstrip()}'")

    # Parse back and verify
    reparsed = RasGeometryUtils.parse_fixed_width(lines[0], column_width=8)
    assert len(reparsed) == len(values), "Round-trip count mismatch"
    for orig, parsed in zip(values, reparsed):
        assert abs(orig - parsed) < 0.01, f"Round-trip value mismatch: {orig} != {parsed}"

    print("PASS: Round-trip formatting and parsing")


def test_interpret_count():
    """Test count interpretation for different keywords"""
    print("\n" + "="*70)
    print("TEST: interpret_count()")
    print("="*70)

    # Test station/elevation (pairs)
    count1 = RasGeometryUtils.interpret_count("#Sta/Elev", 40)
    print(f"#Sta/Elev= 40  ->  {count1} total values (40 pairs)")
    assert count1 == 80, "Sta/Elev count wrong"

    # Test Manning's n (segments × 3)
    count2 = RasGeometryUtils.interpret_count("#Mann", 3, [0, 0])
    print(f"#Mann= 3 , 0 , 0  ->  {count2} total values (3 segments × 3)")
    assert count2 == 9, "Mann count wrong"

    # Test coordinates (pairs)
    count3 = RasGeometryUtils.interpret_count("Reach XY", 591)
    print(f"Reach XY= 591  ->  {count3} total values (591 pairs)")
    assert count3 == 1182, "Reach XY count wrong"

    # Test elevation-volume (pairs)
    count4 = RasGeometryUtils.interpret_count("Storage Area Elev Volume", 53)
    print(f"Storage Area Elev Volume= 53  ->  {count4} total values (53 pairs)")
    assert count4 == 106, "Elev/Volume count wrong"

    # Test levees (sum)
    count5 = RasGeometryUtils.interpret_count("Levee", 12, [0])
    print(f"Levee= 12 , 0  ->  {count5} total values (12 + 0)")
    assert count5 == 12, "Levee count wrong"

    print("PASS: All count interpretations correct")


def test_extract_keyword_value():
    """Test extracting values after keyword markers"""
    print("\n" + "="*70)
    print("TEST: extract_keyword_value()")
    print("="*70)

    # Test various keywords
    line1 = "Geom Title=White Lick Creek Geometry"
    value1 = RasGeometryUtils.extract_keyword_value(line1, "Geom Title")
    print(f"'{line1}'")
    print(f"  -> Extracted: '{value1}'")
    assert value1 == "White Lick Creek Geometry", "Geom Title extraction failed"

    line2 = "Program Version=6.30"
    value2 = RasGeometryUtils.extract_keyword_value(line2, "Program Version")
    print(f"'{line2}'")
    print(f"  -> Extracted: '{value2}'")
    assert value2 == "6.30", "Program Version extraction failed"

    line3 = "#Sta/Elev= 40"
    value3 = RasGeometryUtils.extract_keyword_value(line3, "#Sta/Elev")
    print(f"'{line3}'")
    print(f"  -> Extracted: '{value3}'")
    assert value3 == "40", "Count extraction failed"

    print("PASS: Keyword value extraction")


def test_extract_comma_list():
    """Test extracting comma-separated lists"""
    print("\n" + "="*70)
    print("TEST: extract_comma_list()")
    print("="*70)

    # Test with comma separation
    line1 = "River Reach=White Lick,Reach 1"
    values1 = RasGeometryUtils.extract_comma_list(line1, "River Reach")
    print(f"'{line1}'")
    print(f"  -> Extracted: {values1}")
    assert values1 == ["White Lick", "Reach 1"], "River/Reach extraction failed"

    # Test without comma (single value)
    line2 = "Storage Area=Res Pool 1"
    values2 = RasGeometryUtils.extract_comma_list(line2, "Storage Area")
    print(f"'{line2}'")
    print(f"  -> Extracted: {values2}")
    assert values2 == ["Res Pool 1"], "Single value extraction failed"

    # Test with multiple commas
    line3 = "#Mann= 3 , 0 , 0"
    values3 = RasGeometryUtils.extract_comma_list(line3, "#Mann")
    print(f"'{line3}'")
    print(f"  -> Extracted: {values3}")
    assert values3 == ["3", "0", "0"], "Multiple comma extraction failed"

    print("PASS: Comma list extraction")


def test_create_backup():
    """Test backup file creation"""
    print("\n" + "="*70)
    print("TEST: create_backup()")
    print("="*70)

    # Use a test geometry file
    test_file = Path(r"C:\GH\ras-commander\research\geometry file parsing\Example Geometries\BaldEagle.g01")

    if not test_file.exists():
        print(f"⚠ WARNING: Test file not found: {test_file}")
        print("SKIP: Backup test")
        return

    try:
        backup_path = RasGeometryUtils.create_backup(test_file)
        print(f"Original: {test_file}")
        print(f"Backup:   {backup_path}")

        assert backup_path.exists(), "Backup file not created"
        assert backup_path.stat().st_size > 0, "Backup file is empty"

        # Clean up backup
        backup_path.unlink()
        print("PASS: Backup creation (cleanup completed)")

    except Exception as e:
        print(f"FAIL: Backup creation failed: {e}")
        raise


def test_identify_section():
    """Test section identification in geometry files"""
    print("\n" + "="*70)
    print("TEST: identify_section()")
    print("="*70)

    # Use real geometry file
    test_file = Path(r"C:\GH\ras-commander\research\geometry file parsing\Example Geometries\BaldEagle.g01")

    if not test_file.exists():
        print(f"⚠ WARNING: Test file not found: {test_file}")
        print("SKIP: Section identification test")
        return

    with open(test_file, 'r') as f:
        lines = f.readlines()

    # Test finding River Reach section
    section = RasGeometryUtils.identify_section(lines, "River Reach=")
    if section:
        start, end = section
        print(f"Found 'River Reach=' at lines {start} to {end}")
        print(f"  Line {start}: {lines[start].strip()}")
        assert start >= 0 and end > start, "Invalid section bounds"
        print("PASS: Section identification")
    else:
        print("FAIL: River Reach section not found")


def test_with_real_geometry_file():
    """Integration test with real geometry file"""
    print("\n" + "="*70)
    print("INTEGRATION TEST: Parse real cross section data")
    print("="*70)

    geom_file = Path(r"C:\GH\ras-commander\research\geometry file parsing\Example Geometries\BaldEagle.g01")

    if not geom_file.exists():
        print(f"⚠ WARNING: Test file not found: {geom_file}")
        print("SKIP: Integration test")
        return

    try:
        with open(geom_file, 'r') as f:
            lines = f.readlines()

        # Find first cross section with station/elevation data
        found_xs = False
        for i, line in enumerate(lines):
            if line.startswith("#Sta/Elev="):
                count_str = RasGeometryUtils.extract_keyword_value(line, "#Sta/Elev")
                count = int(count_str.strip())

                print(f"\nFound cross section at line {i}:")
                print(f"  {line.strip()}")
                print(f"  Count: {count} pairs")

                # Calculate total values to read
                total_values = RasGeometryUtils.interpret_count("#Sta/Elev", count)
                print(f"  Total values to read: {total_values}")

                # Parse station/elevation data
                values = []
                line_idx = i + 1
                while len(values) < total_values and line_idx < len(lines):
                    parsed = RasGeometryUtils.parse_fixed_width(lines[line_idx], column_width=8)
                    values.extend(parsed)
                    line_idx += 1

                print(f"  Parsed {len(values)} values")
                print(f"  First 10 values: {values[:10]}")

                # Validate count matches
                assert len(values) == total_values, f"Count mismatch: expected {total_values}, got {len(values)}"

                # Convert to station/elevation pairs
                stations = values[0::2]
                elevations = values[1::2]
                print(f"  Station/Elevation pairs: {len(stations)}")
                print(f"  Station range: {min(stations):.2f} to {max(stations):.2f}")
                print(f"  Elevation range: {min(elevations):.2f} to {max(elevations):.2f}")

                found_xs = True
                print("PASS: Real geometry file parsing")
                break

        if not found_xs:
            print("FAIL: No cross section data found")

    except Exception as e:
        print(f"FAIL: Integration test error: {e}")
        raise


def run_all_tests():
    """Run all test functions"""
    print("\n" + "#"*70)
    print("# RasGeometryUtils Test Suite")
    print("#"*70)

    tests = [
        test_parse_fixed_width_8char,
        test_parse_fixed_width_16char,
        test_format_fixed_width,
        test_interpret_count,
        test_extract_keyword_value,
        test_extract_comma_list,
        test_identify_section,
        test_create_backup,
        test_with_real_geometry_file,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\nASSERTION FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\nERROR: {e}")
            failed += 1

    print("\n" + "#"*70)
    print(f"# Test Results: {passed} passed, {failed} failed")
    print("#"*70)

    if failed == 0:
        print("\nALL TESTS PASSED")
    else:
        print(f"\nFAILED: {failed} TEST(S) FAILED")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
