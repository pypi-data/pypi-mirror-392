"""
Test RasGeometry cross section methods

Tests the three Item 1 methods:
1. get_cross_sections()
2. get_station_elevation()
3. set_station_elevation()
"""

import sys
from pathlib import Path

# Add parent directory to path
current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent
sys.path.insert(0, str(parent_directory))

from ras_commander.RasGeometry import RasGeometry

# Test data file
GEOM_FILE = Path(r"C:\GH\ras-commander\research\geometry file parsing\Example Geometries\BaldEagle.g01")


def test_get_cross_sections():
    """Test extracting all cross sections"""
    print("\n" + "="*70)
    print("TEST 1: get_cross_sections()")
    print("="*70)

    if not GEOM_FILE.exists():
        print(f"SKIP: Test file not found: {GEOM_FILE}")
        return False

    try:
        # Get all cross sections
        xs_df = RasGeometry.get_cross_sections(GEOM_FILE)

        print(f"\nTotal cross sections: {len(xs_df)}")
        print(f"\nFirst 5 cross sections:")
        print(xs_df.head())

        print(f"\nRivers found: {xs_df['River'].unique().tolist()}")
        print(f"Reaches found: {xs_df['Reach'].unique().tolist()}")

        # Validate
        assert len(xs_df) > 0, "No cross sections found"
        assert 'River' in xs_df.columns, "Missing River column"
        assert 'Reach' in xs_df.columns, "Missing Reach column"
        assert 'RS' in xs_df.columns, "Missing RS column"

        print("\nPASS: get_cross_sections()")
        return True

    except Exception as e:
        print(f"\nFAIL: {e}")
        return False


def test_get_station_elevation():
    """Test reading station/elevation for a cross section"""
    print("\n" + "="*70)
    print("TEST 2: get_station_elevation()")
    print("="*70)

    if not GEOM_FILE.exists():
        print(f"SKIP: Test file not found: {GEOM_FILE}")
        return False

    try:
        # First get list of cross sections
        xs_df = RasGeometry.get_cross_sections(GEOM_FILE)

        if len(xs_df) == 0:
            print("SKIP: No cross sections found")
            return False

        # Get first cross section
        first_xs = xs_df.iloc[0]
        river = first_xs['River']
        reach = first_xs['Reach']
        rs = first_xs['RS']

        print(f"\nReading XS: {river} / {reach} / RS {rs}")

        # Get station/elevation
        sta_elev = RasGeometry.get_station_elevation(GEOM_FILE, river, reach, rs)

        print(f"\nStation/Elevation points: {len(sta_elev)}")
        print(f"\nFirst 5 points:")
        print(sta_elev.head())

        print(f"\nStation range: {sta_elev['Station'].min():.2f} to {sta_elev['Station'].max():.2f}")
        print(f"Elevation range: {sta_elev['Elevation'].min():.2f} to {sta_elev['Elevation'].max():.2f}")

        # Validate
        assert len(sta_elev) > 0, "No station/elevation data found"
        assert 'Station' in sta_elev.columns, "Missing Station column"
        assert 'Elevation' in sta_elev.columns, "Missing Elevation column"

        print("\nPASS: get_station_elevation()")
        return True

    except Exception as e:
        print(f"\nFAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_set_station_elevation():
    """Test writing station/elevation (round-trip)"""
    print("\n" + "="*70)
    print("TEST 3: set_station_elevation() - Round Trip")
    print("="*70)

    if not GEOM_FILE.exists():
        print(f"SKIP: Test file not found: {GEOM_FILE}")
        return False

    try:
        # Use a test copy
        test_file = GEOM_FILE.parent / "BaldEagle_test.g01"

        # Copy original to test file
        import shutil
        shutil.copy2(GEOM_FILE, test_file)
        print(f"\nCreated test copy: {test_file.name}")

        # Get first cross section
        xs_df = RasGeometry.get_cross_sections(test_file)
        first_xs = xs_df.iloc[0]
        river = first_xs['River']
        reach = first_xs['Reach']
        rs = first_xs['RS']

        print(f"\nTesting with XS: {river} / {reach} / RS {rs}")

        # Read original data
        original_sta_elev = RasGeometry.get_station_elevation(test_file, river, reach, rs)
        print(f"\nOriginal data: {len(original_sta_elev)} points")

        # Modify data (add 1.0 to all elevations)
        modified_sta_elev = original_sta_elev.copy()
        modified_sta_elev['Elevation'] += 1.0
        print(f"Modified elevations: +1.0 ft")

        # Write modified data
        RasGeometry.set_station_elevation(test_file, river, reach, rs, modified_sta_elev)
        print("Wrote modified data to file")

        # Read back
        readback_sta_elev = RasGeometry.get_station_elevation(test_file, river, reach, rs)
        print(f"Read back: {len(readback_sta_elev)} points")

        # Validate
        assert len(readback_sta_elev) == len(modified_sta_elev), "Point count changed"

        # Check elevations match (within float precision)
        import numpy as np
        assert np.allclose(readback_sta_elev['Elevation'].values,
                          modified_sta_elev['Elevation'].values,
                          rtol=1e-5), "Elevations don't match after round-trip"

        assert np.allclose(readback_sta_elev['Station'].values,
                          modified_sta_elev['Station'].values,
                          rtol=1e-5), "Stations don't match after round-trip"

        print("\nElevation check:")
        print(f"  Original mean:  {original_sta_elev['Elevation'].mean():.3f}")
        print(f"  Modified mean:  {modified_sta_elev['Elevation'].mean():.3f}")
        print(f"  Readback mean:  {readback_sta_elev['Elevation'].mean():.3f}")
        print(f"  Difference:     {abs(modified_sta_elev['Elevation'].mean() - readback_sta_elev['Elevation'].mean()):.6f}")

        # Clean up test file
        test_file.unlink()
        # Also remove backup
        backup_file = test_file.with_suffix(test_file.suffix + '.bak')
        if backup_file.exists():
            backup_file.unlink()

        print("\nPASS: set_station_elevation() round-trip successful")
        return True

    except Exception as e:
        print(f"\nFAIL: {e}")
        import traceback
        traceback.print_exc()
        # Clean up test file if it exists
        if test_file.exists():
            test_file.unlink()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "#"*70)
    print("# RasGeometry Cross Section Tests")
    print("#"*70)

    tests = [
        test_get_cross_sections,
        test_get_station_elevation,
        test_set_station_elevation,
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
    passed = sum(results)
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
