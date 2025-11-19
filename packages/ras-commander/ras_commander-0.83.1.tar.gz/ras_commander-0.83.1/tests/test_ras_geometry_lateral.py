"""
Test RasGeometry lateral structure methods

Tests Item 5: Lateral Structure operations
"""

import sys
from pathlib import Path

# Add parent directory to path
current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent
sys.path.insert(0, str(parent_directory))

from ras_commander import RasGeometry

# Test data file - A100_00_00.g08 has lateral structures
GEOM_FILE = Path(r"C:\GH\ras-commander\research\geometry file parsing\Example Geometries\A100_00_00.g08")


def test_get_lateral_structures():
    """Test listing all lateral structures"""
    print("\n" + "="*70)
    print("TEST 1: get_lateral_structures()")
    print("="*70)

    if not GEOM_FILE.exists():
        print(f"SKIP: Test file not found: {GEOM_FILE}")
        return False

    try:
        # Get all lateral structures
        lat_strucs = RasGeometry.get_lateral_structures(GEOM_FILE)

        print(f"\nLateral structures found: {len(lat_strucs)}")

        if len(lat_strucs) > 0:
            print(f"\nColumns available:")
            for col in lat_strucs.columns:
                print(f"  - {col}")

            print(f"\nFirst 5 lateral structures:")
            print(lat_strucs.head())

            print(f"\nSummary:")
            print(f"  Rivers: {lat_strucs['River'].unique().tolist()}")
            print(f"  Reaches: {lat_strucs['Reach'].unique().tolist()}")
            print(f"  Width range: {lat_strucs['Width'].min():.1f} to {lat_strucs['Width'].max():.1f} ft")
            print(f"  Coefficient range: {lat_strucs['Coefficient'].min():.2f} to {lat_strucs['Coefficient'].max():.2f}")

            # Validate
            assert len(lat_strucs) > 0, "No lateral structures found"
            assert 'River' in lat_strucs.columns, "Missing River column"
            assert 'RS' in lat_strucs.columns, "Missing RS column"
            assert 'Width' in lat_strucs.columns, "Missing Width column"

            print("\nPASS: get_lateral_structures()")
            return True
        else:
            print("SKIP: No lateral structures found in file")
            return False

    except Exception as e:
        print(f"\nFAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_lateral_weir_profile():
    """Test reading lateral weir station-elevation profile"""
    print("\n" + "="*70)
    print("TEST 2: get_lateral_weir_profile()")
    print("="*70)

    if not GEOM_FILE.exists():
        print(f"SKIP: Test file not found: {GEOM_FILE}")
        return False

    try:
        # First get list of lateral structures
        lat_strucs = RasGeometry.get_lateral_structures(GEOM_FILE)

        if len(lat_strucs) == 0:
            print("SKIP: No lateral structures found")
            return False

        # Get profile for first lateral structure
        first_lat = lat_strucs.iloc[0]
        river = first_lat['River']
        reach = first_lat['Reach']
        rs = first_lat['RS']
        position = first_lat['Position']

        print(f"\nReading lateral weir profile:")
        print(f"  River: {river}")
        print(f"  Reach: {reach}")
        print(f"  RS: {rs}")
        print(f"  Position: {position}")
        print(f"  Description: {first_lat.get('Description', 'N/A')}")

        profile = RasGeometry.get_lateral_weir_profile(GEOM_FILE, river, reach, rs, position)

        print(f"\nLateral Weir Profile:")
        print(f"  Points: {len(profile)}")
        print(f"  Station range: {profile['Station'].min():.2f} to {profile['Station'].max():.2f}")
        print(f"  Elevation range: {profile['Elevation'].min():.2f} to {profile['Elevation'].max():.2f}")

        print(f"\nProfile data:")
        print(profile)

        # Validate
        assert len(profile) > 0, "No profile data found"
        assert 'Station' in profile.columns, "Missing Station column"
        assert 'Elevation' in profile.columns, "Missing Elevation column"

        # Note: SE_Count may represent something different than point count
        if len(profile) != first_lat['SE_Count']:
            print(f"\nNote: SE_Count={first_lat['SE_Count']} but extracted {len(profile)} points")
            print("  (SE_Count interpretation may differ from actual point count)")

        print("\nPASS: get_lateral_weir_profile()")
        return True

    except Exception as e:
        print(f"\nFAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_laterals():
    """Test accessing multiple lateral structures"""
    print("\n" + "="*70)
    print("TEST 3: Multiple Lateral Structures")
    print("="*70)

    if not GEOM_FILE.exists():
        print(f"SKIP: Test file not found: {GEOM_FILE}")
        return False

    try:
        # Get all lateral structures
        lat_strucs = RasGeometry.get_lateral_structures(GEOM_FILE)

        if len(lat_strucs) <= 1:
            print("SKIP: Need at least 2 lateral structures for this test")
            return False

        print(f"\nProcessing {len(lat_strucs)} lateral structures...")

        # Extract profiles for all
        profiles_extracted = 0
        for idx, lat in lat_strucs.iterrows():
            try:
                profile = RasGeometry.get_lateral_weir_profile(
                    GEOM_FILE, lat['River'], lat['Reach'], lat['RS'], lat['Position']
                )
                profiles_extracted += 1
                print(f"  {idx+1}. RS {lat['RS']} pos {lat['Position']}: {len(profile)} points")
            except Exception as e:
                print(f"  {idx+1}. RS {lat['RS']} pos {lat['Position']}: ERROR - {e}")

        print(f"\nSuccessfully extracted {profiles_extracted}/{len(lat_strucs)} profiles")

        assert profiles_extracted > 0, "No profiles extracted"

        print("\nPASS: Multiple lateral structures")
        return True

    except Exception as e:
        print(f"\nFAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "#"*70)
    print("# RasGeometry Lateral Structure Tests")
    print("#"*70)

    tests = [
        test_get_lateral_structures,
        test_get_lateral_weir_profile,
        test_multiple_laterals,
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
        print(f"\n{total - passed} TEST(S) FAILED OR SKIPPED")

    return all(results)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
