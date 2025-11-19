"""
Test RasGeometry storage area methods

Tests Item 4: Storage Area operations
"""

import sys
from pathlib import Path

# Add parent directory to path
current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent
sys.path.insert(0, str(parent_directory))

from ras_commander import RasGeometry

# Test data file - BaldEagleDamBrk has storage areas
GEOM_FILE = Path(r"C:\GH\ras-commander\research\geometry file parsing\Example Geometries\BaldEagleDamBrk.g01")


def test_get_storage_areas():
    """Test listing all storage areas"""
    print("\n" + "="*70)
    print("TEST 1: get_storage_areas()")
    print("="*70)

    if not GEOM_FILE.exists():
        print(f"SKIP: Test file not found: {GEOM_FILE}")
        return False

    try:
        # Get storage areas (excluding 2D)
        storage_areas = RasGeometry.get_storage_areas(GEOM_FILE, exclude_2d=True)

        print(f"\nStorage areas found (excluding 2D): {len(storage_areas)}")
        for i, name in enumerate(storage_areas, 1):
            print(f"  {i}. {name}")

        # Get all storage areas (including 2D)
        all_storage = RasGeometry.get_storage_areas(GEOM_FILE, exclude_2d=False)

        print(f"\nAll storage areas (including 2D): {len(all_storage)}")
        for i, name in enumerate(all_storage, 1):
            print(f"  {i}. {name}")

        # Validate
        assert len(storage_areas) >= 0, "Should return at least empty list"
        assert len(all_storage) >= len(storage_areas), "All storage should be >= non-2D storage"

        print("\nPASS: get_storage_areas()")
        return True

    except Exception as e:
        print(f"\nFAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_storage_elevation_volume():
    """Test reading elevation-volume curve"""
    print("\n" + "="*70)
    print("TEST 2: get_storage_elevation_volume()")
    print("="*70)

    if not GEOM_FILE.exists():
        print(f"SKIP: Test file not found: {GEOM_FILE}")
        return False

    try:
        # First get list of storage areas
        storage_areas = RasGeometry.get_storage_areas(GEOM_FILE, exclude_2d=True)

        if len(storage_areas) == 0:
            print("SKIP: No storage areas found in geometry file")
            return False

        # Get elevation-volume for first storage area
        area_name = storage_areas[0]
        print(f"\nReading elevation-volume for: {area_name}")

        elev_vol = RasGeometry.get_storage_elevation_volume(GEOM_FILE, area_name)

        print(f"\nElevation-Volume Data:")
        print(f"  Points: {len(elev_vol)}")
        print(f"  Elevation range: {elev_vol['Elevation'].min():.2f} to {elev_vol['Elevation'].max():.2f}")
        print(f"  Volume range: {elev_vol['Volume'].min():.0f} to {elev_vol['Volume'].max():.0f}")

        print(f"\nFirst 5 points:")
        print(elev_vol.head())

        # Validate
        assert len(elev_vol) > 0, "No elevation-volume data found"
        assert 'Elevation' in elev_vol.columns, "Missing Elevation column"
        assert 'Volume' in elev_vol.columns, "Missing Volume column"
        assert elev_vol['Volume'].is_monotonic_increasing, "Volume should increase with elevation"

        print("\nPASS: get_storage_elevation_volume()")
        return True

    except Exception as e:
        print(f"\nFAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "#"*70)
    print("# RasGeometry Storage Area Tests")
    print("#"*70)

    tests = [
        test_get_storage_areas,
        test_get_storage_elevation_volume,
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
