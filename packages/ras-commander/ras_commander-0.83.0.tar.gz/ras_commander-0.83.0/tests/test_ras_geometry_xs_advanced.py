"""
Test advanced cross section methods: banks, exp/cntr, Manning's n

Tests Phase 2-3 methods
"""

import sys
from pathlib import Path

# Add parent directory to path
current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent
sys.path.insert(0, str(parent_directory))

from ras_commander import RasGeometry

# Test data file
GEOM_FILE = Path(r"C:\GH\ras-commander\research\geometry file parsing\Example Geometries\BaldEagle.g01")


def test_get_bank_stations():
    """Test bank station extraction"""
    print("\n" + "="*70)
    print("TEST 1: get_bank_stations()")
    print("="*70)

    if not GEOM_FILE.exists():
        print(f"SKIP: Test file not found")
        return False

    try:
        # Get first XS
        xs_df = RasGeometry.get_cross_sections(GEOM_FILE)
        first_xs = xs_df.iloc[0]
        river, reach, rs = first_xs['River'], first_xs['Reach'], first_xs['RS']

        print(f"\nExtracting banks for: {river} / {reach} / RS {rs}")

        # Get bank stations
        banks = RasGeometry.get_bank_stations(GEOM_FILE, river, reach, rs)

        if banks:
            left, right = banks
            print(f"\nBank Stations:")
            print(f"  Left: {left}")
            print(f"  Right: {right}")
            print(f"  Main channel width: {right - left:.2f} ft")

            assert left < right, "Left bank should be < right bank"
            assert left >= 0, "Banks should be positive"

            print("\nPASS: get_bank_stations()")
            return True
        else:
            print("\nNo banks found for this XS")
            return True  # Not an error, some XS don't have banks

    except Exception as e:
        print(f"\nFAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_expansion_contraction():
    """Test expansion/contraction extraction"""
    print("\n" + "="*70)
    print("TEST 2: get_expansion_contraction()")
    print("="*70)

    if not GEOM_FILE.exists():
        print(f"SKIP: Test file not found")
        return False

    try:
        # Get first XS
        xs_df = RasGeometry.get_cross_sections(GEOM_FILE)
        first_xs = xs_df.iloc[0]
        river, reach, rs = first_xs['River'], first_xs['Reach'], first_xs['RS']

        print(f"\nExtracting exp/cntr for: {river} / {reach} / RS {rs}")

        # Get expansion/contraction
        exp, cntr = RasGeometry.get_expansion_contraction(GEOM_FILE, river, reach, rs)

        print(f"\nExpansion/Contraction Coefficients:")
        print(f"  Expansion: {exp}")
        print(f"  Contraction: {cntr}")

        assert 0 <= exp <= 1.0, "Expansion should be between 0 and 1"
        assert 0 <= cntr <= 1.0, "Contraction should be between 0 and 1"

        print("\nPASS: get_expansion_contraction()")
        return True

    except Exception as e:
        print(f"\nFAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_mannings_n():
    """Test Manning's n extraction"""
    print("\n" + "="*70)
    print("TEST 3: get_mannings_n()")
    print("="*70)

    if not GEOM_FILE.exists():
        print(f"SKIP: Test file not found")
        return False

    try:
        # Get first XS
        xs_df = RasGeometry.get_cross_sections(GEOM_FILE)
        first_xs = xs_df.iloc[0]
        river, reach, rs = first_xs['River'], first_xs['Reach'], first_xs['RS']

        print(f"\nExtracting Manning's n for: {river} / {reach} / RS {rs}")

        # Get Manning's n
        mann = RasGeometry.get_mannings_n(GEOM_FILE, river, reach, rs)

        print(f"\nManning's n Segments:")
        print(mann)

        print(f"\nSummary:")
        print(f"  Total segments: {len(mann)}")
        print(f"  Subsections: {mann['Subsection'].unique().tolist()}")

        if 'LOB' in mann['Subsection'].values:
            lob_n = mann[mann['Subsection'] == 'LOB']['n_value'].iloc[0]
            print(f"  LOB Manning's n: {lob_n}")

        if 'Channel' in mann['Subsection'].values:
            chan_n = mann[mann['Subsection'] == 'Channel']['n_value'].iloc[0]
            print(f"  Channel Manning's n: {chan_n}")

        if 'ROB' in mann['Subsection'].values:
            rob_n = mann[mann['Subsection'] == 'ROB']['n_value'].iloc[0]
            print(f"  ROB Manning's n: {rob_n}")

        assert len(mann) > 0, "No Manning's n data extracted"
        assert 'Station' in mann.columns, "Missing Station column"
        assert 'n_value' in mann.columns, "Missing n_value column"
        assert 'Subsection' in mann.columns, "Missing Subsection column"

        print("\nPASS: get_mannings_n()")
        return True

    except Exception as e:
        print(f"\nFAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "#"*70)
    print("# Advanced Cross Section Tests")
    print("#"*70)

    tests = [
        test_get_bank_stations,
        test_get_expansion_contraction,
        test_get_mannings_n,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\nERROR in {test_func.__name__}: {e}")
            results.append(False)

    print("\n" + "#"*70)
    passed = sum(1 for r in results if r is True)
    total = len(results)
    print(f"# Results: {passed}/{total} tests passed")
    print("#"*70)

    if all(results):
        print("\nALL TESTS PASSED")
    else:
        print(f"\n{total - passed} TEST(S) FAILED")

    return all(results)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
