"""
Test bank station interpolation and 450 point limit in set_station_elevation()

Tests critical HEC-RAS compatibility requirements:
1. Bank stations MUST appear as exact points in station/elevation data
2. Maximum 450 points per cross section
3. Bank modification propagates correctly
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add parent directory to path
current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent
sys.path.insert(0, str(parent_directory))

from ras_commander import RasGeometry

# Test data file
GEOM_FILE = Path(r"C:\GH\ras-commander\research\geometry file parsing\Example Geometries\BaldEagle.g01")


def test_bank_interpolation_auto():
    """Test automatic bank interpolation from existing banks"""
    print("\n" + "="*70)
    print("TEST 1: Automatic Bank Interpolation (Read Existing Banks)")
    print("="*70)

    if not GEOM_FILE.exists():
        print(f"SKIP: Test file not found: {GEOM_FILE}")
        return False

    try:
        # Create test copy
        test_file = GEOM_FILE.parent / "BaldEagle_bank_test.g01"
        import shutil
        shutil.copy2(GEOM_FILE, test_file)

        # Get first XS
        xs_df = RasGeometry.get_cross_sections(test_file)
        first_xs = xs_df.iloc[0]
        river, reach, rs = first_xs['River'], first_xs['Reach'], first_xs['RS']

        print(f"\nTesting with: {river} / {reach} / RS {rs}")

        # Read original geometry and banks
        original_sta_elev = RasGeometry.get_station_elevation(test_file, river, reach, rs)

        # Read bank stations from file
        with open(test_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("Bank Sta="):
                    bank_str = line.split('=')[1].strip()
                    banks = [float(v.strip()) for v in bank_str.split(',')]
                    bank_left_orig, bank_right_orig = banks[0], banks[1]
                    break

        print(f"Original banks: {bank_left_orig}, {bank_right_orig}")
        print(f"Original points: {len(original_sta_elev)}")

        # Check if banks are in original data
        left_in_data = bank_left_orig in original_sta_elev['Station'].values
        right_in_data = bank_right_orig in original_sta_elev['Station'].values

        print(f"Left bank in data: {left_in_data}")
        print(f"Right bank in data: {right_in_data}")

        # Remove a point to test interpolation (simulate missing bank point)
        test_sta_elev = original_sta_elev[original_sta_elev['Station'] != bank_left_orig].copy()
        print(f"\nRemoved left bank point, now {len(test_sta_elev)} points")

        # Write without bank parameters (should auto-read and interpolate)
        RasGeometry.set_station_elevation(test_file, river, reach, rs, test_sta_elev)
        print("Wrote geometry with auto bank interpolation")

        # Read back
        readback = RasGeometry.get_station_elevation(test_file, river, reach, rs)
        print(f"Read back: {len(readback)} points")

        # Verify banks are in readback data
        left_in_readback = bank_left_orig in readback['Station'].values
        right_in_readback = bank_right_orig in readback['Station'].values

        print(f"\nAfter auto-interpolation:")
        print(f"  Left bank ({bank_left_orig}) in data: {left_in_readback}")
        print(f"  Right bank ({bank_right_orig}) in data: {right_in_readback}")

        # Cleanup
        test_file.unlink()
        if (test_file.parent / (test_file.name + '.bak')).exists():
            (test_file.parent / (test_file.name + '.bak')).unlink()

        assert left_in_readback, "Left bank not interpolated!"
        assert right_in_readback, "Right bank not interpolated!"

        print("\nPASS: Banks automatically interpolated")
        return True

    except Exception as e:
        print(f"\nFAIL: {e}")
        import traceback
        traceback.print_exc()
        if test_file.exists():
            test_file.unlink()
        return False


def test_bank_modification():
    """Test changing bank stations"""
    print("\n" + "="*70)
    print("TEST 2: Bank Station Modification")
    print("="*70)

    if not GEOM_FILE.exists():
        print(f"SKIP: Test file not found: {GEOM_FILE}")
        return False

    try:
        # Create test copy
        test_file = GEOM_FILE.parent / "BaldEagle_bank_modify_test.g01"
        import shutil
        shutil.copy2(GEOM_FILE, test_file)

        # Get first XS
        xs_df = RasGeometry.get_cross_sections(test_file)
        first_xs = xs_df.iloc[0]
        river, reach, rs = first_xs['River'], first_xs['Reach'], first_xs['RS']

        # Read geometry
        sta_elev = RasGeometry.get_station_elevation(test_file, river, reach, rs)

        # Define new bank stations
        new_bank_left = 100.0
        new_bank_right = 400.0

        print(f"\nSetting new banks: {new_bank_left}, {new_bank_right}")
        print(f"Original points: {len(sta_elev)}")

        # Write with new banks
        RasGeometry.set_station_elevation(test_file, river, reach, rs, sta_elev,
                                         bank_left=new_bank_left, bank_right=new_bank_right)

        # Read back
        readback = RasGeometry.get_station_elevation(test_file, river, reach, rs)
        print(f"Points after write: {len(readback)}")

        # Verify new banks in data
        left_in_data = new_bank_left in readback['Station'].values
        right_in_data = new_bank_right in readback['Station'].values

        print(f"\nNew banks in geometry:")
        print(f"  Left bank ({new_bank_left}) in data: {left_in_data}")
        print(f"  Right bank ({new_bank_right}) in data: {right_in_data}")

        # Verify Bank Sta= line updated
        with open(test_file, 'r') as f:
            file_content = f.read()
            bank_line_found = f"Bank Sta={new_bank_left:g},{new_bank_right:g}" in file_content

        print(f"  Bank Sta= line updated in file: {bank_line_found}")

        # Cleanup
        test_file.unlink()
        if (test_file.parent / (test_file.name + '.bak')).exists():
            (test_file.parent / (test_file.name + '.bak')).unlink()

        assert left_in_data, "New left bank not in geometry!"
        assert right_in_data, "New right bank not in geometry!"
        assert bank_line_found, "Bank Sta= line not updated!"

        print("\nPASS: Bank modification successful")
        return True

    except Exception as e:
        print(f"\nFAIL: {e}")
        import traceback
        traceback.print_exc()
        if test_file.exists():
            test_file.unlink()
        return False


def test_450_point_limit():
    """Test 450 point limit enforcement"""
    print("\n" + "="*70)
    print("TEST 3: 450 Point Limit Enforcement")
    print("="*70)

    if not GEOM_FILE.exists():
        print(f"SKIP: Test file not found: {GEOM_FILE}")
        return False

    try:
        # Get first XS
        xs_df = RasGeometry.get_cross_sections(GEOM_FILE)
        first_xs = xs_df.iloc[0]
        river, reach, rs = first_xs['River'], first_xs['Reach'], first_xs['RS']

        # Create oversized geometry (451 points)
        oversized_sta_elev = pd.DataFrame({
            'Station': np.linspace(0, 1000, 451),
            'Elevation': np.linspace(650, 700, 451)
        })

        print(f"Created test geometry with {len(oversized_sta_elev)} points (exceeds 450)")

        # Attempt to write (should raise ValueError)
        try:
            test_file = GEOM_FILE.parent / "BaldEagle_limit_test.g01"
            import shutil
            shutil.copy2(GEOM_FILE, test_file)

            RasGeometry.set_station_elevation(test_file, river, reach, rs, oversized_sta_elev)

            # If we get here, test failed (should have raised ValueError)
            print("\nFAIL: Expected ValueError for >450 points, but write succeeded")
            test_file.unlink()
            return False

        except ValueError as e:
            error_msg = str(e)
            print(f"\nCorrectly raised ValueError:")
            print(f"  {error_msg}")

            # Verify error message is helpful
            assert "450" in error_msg, "Error should mention 450 point limit"
            assert "451" in error_msg or str(len(oversized_sta_elev)) in error_msg, "Error should mention actual count"

            # Cleanup
            if test_file.exists():
                test_file.unlink()
            if (test_file.parent / (test_file.name + '.bak')).exists():
                (test_file.parent / (test_file.name + '.bak')).unlink()

            print("\nPASS: 450 point limit enforced")
            return True

    except Exception as e:
        print(f"\nFAIL: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bank_interpolation_with_limit():
    """Test that interpolation is counted toward 450 limit"""
    print("\n" + "="*70)
    print("TEST 4: Bank Interpolation Counted Toward 450 Limit")
    print("="*70)

    if not GEOM_FILE.exists():
        print(f"SKIP: Test file not found: {GEOM_FILE}")
        return False

    try:
        # Get first XS
        xs_df = RasGeometry.get_cross_sections(GEOM_FILE)
        first_xs = xs_df.iloc[0]
        river, reach, rs = first_xs['River'], first_xs['Reach'], first_xs['RS']

        # Create geometry with exactly 449 points
        test_sta_elev = pd.DataFrame({
            'Station': np.linspace(0, 1000, 449),
            'Elevation': np.linspace(650, 700, 449)
        })

        # Set banks that are NOT in the station list (will add 2 points via interpolation)
        new_bank_left = 250.5  # Between existing stations
        new_bank_right = 750.5  # Between existing stations

        print(f"Geometry: {len(test_sta_elev)} points")
        print(f"Banks: {new_bank_left}, {new_bank_right} (not in station list)")
        print(f"Expected after interpolation: {len(test_sta_elev) + 2} = 451 points")
        print(f"This should EXCEED 450 limit and raise error")

        try:
            test_file = GEOM_FILE.parent / "BaldEagle_interp_limit_test.g01"
            import shutil
            shutil.copy2(GEOM_FILE, test_file)

            RasGeometry.set_station_elevation(test_file, river, reach, rs, test_sta_elev,
                                             bank_left=new_bank_left, bank_right=new_bank_right)

            # Should not reach here
            print("\nFAIL: Should have raised ValueError for 451 points after interpolation")
            test_file.unlink()
            return False

        except ValueError as e:
            error_msg = str(e)
            print(f"\nCorrectly raised ValueError:")
            print(f"  {error_msg[:200]}...")

            assert "450" in error_msg, "Error should mention limit"
            assert "451" in error_msg or "interpolation" in error_msg.lower(), "Error should mention interpolation count"

            # Cleanup
            if test_file.exists():
                test_file.unlink()
            if (test_file.parent / (test_file.name + '.bak')).exists():
                (test_file.parent / (test_file.name + '.bak')).unlink()

            print("\nPASS: Interpolation counted toward limit")
            return True

    except Exception as e:
        print(f"\nFAIL: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "#"*70)
    print("# Bank Interpolation and 450 Point Limit Tests")
    print("#"*70)

    tests = [
        test_bank_interpolation_auto,
        test_bank_modification,
        test_450_point_limit,
        test_bank_interpolation_with_limit,
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
