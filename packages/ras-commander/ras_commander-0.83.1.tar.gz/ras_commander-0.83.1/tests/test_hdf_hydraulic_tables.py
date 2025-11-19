"""
Test suite for HdfHydraulicTables

Tests hydraulic property table extraction from geometry HDF files.
"""

import sys
from pathlib import Path

# Add parent directory to path
current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent
sys.path.insert(0, str(parent_directory))

from ras_commander import HdfHydraulicTables

# Test data file - Use preprocessed HDF from example_projects
HDF_FILE = Path(r"C:\GH\ras-commander\example_projects\Balde Eagle Creek\BaldEagle.g01.hdf")


def test_get_xs_htab_single():
    """Test extracting HTAB for a single cross section"""
    print("\n" + "="*70)
    print("TEST 1: get_xs_htab() - Single Cross Section")
    print("="*70)

    if not HDF_FILE.exists():
        print(f"SKIP: Test file not found: {HDF_FILE}")
        return False

    try:
        # First, we need to find what cross sections are available
        # For now, let's try what we know from the HDF exploration
        # We'll need to check the Attributes to see what's available

        import h5py
        with h5py.File(HDF_FILE, 'r') as hdf:
            if '/Geometry/Cross Sections/Attributes' in hdf:
                attrs = hdf['/Geometry/Cross Sections/Attributes'][:]
                if len(attrs) > 0:
                    first_xs = attrs[0]
                    river = first_xs['River'].decode('utf-8').strip()
                    reach = first_xs['Reach'].decode('utf-8').strip()
                    rs = first_xs['RS'].decode('utf-8').strip()

                    print(f"\nTesting with XS: {river} / {reach} / RS {rs}")

                    # Extract HTAB
                    htab = HdfHydraulicTables.get_xs_htab(HDF_FILE, river, reach, rs)

                    print(f"\nProperty Table Extracted:")
                    print(f"  Elevations: {len(htab)}")
                    print(f"  Properties: {len(htab.columns)}")
                    print(f"\nColumns available:")
                    for col in htab.columns:
                        print(f"  - {col}")

                    print(f"\nElevation range: {htab['Elevation'].min():.2f} to {htab['Elevation'].max():.2f}")

                    # Show first few rows
                    print(f"\nFirst 5 rows:")
                    print(htab.head())

                    # Validate structure
                    assert len(htab) > 0, "No data in property table"
                    assert 'Elevation' in htab.columns, "Missing Elevation column"
                    assert 'Area_Total' in htab.columns, "Missing Area_Total column"
                    assert 'Conveyance_Total' in htab.columns, "Missing Conveyance_Total column"

                    print("\nPASS: get_xs_htab() single XS")
                    return True
                else:
                    print("SKIP: No cross sections found in HDF")
                    return False
            else:
                print("SKIP: No Attributes found in HDF")
                return False

    except Exception as e:
        print(f"\nFAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_all_xs_htabs():
    """Test extracting HTABs for all cross sections"""
    print("\n" + "="*70)
    print("TEST 2: get_all_xs_htabs() - All Cross Sections")
    print("="*70)

    if not HDF_FILE.exists():
        print(f"SKIP: Test file not found: {HDF_FILE}")
        return False

    try:
        # Extract all HTABs
        all_htabs = HdfHydraulicTables.get_all_xs_htabs(HDF_FILE)

        print(f"\nExtracted {len(all_htabs)} property tables")

        if len(all_htabs) > 0:
            # Show first few
            print(f"\nFirst 5 cross sections:")
            for i, ((river, reach, rs), htab) in enumerate(all_htabs.items()):
                if i >= 5:
                    break
                print(f"  {i+1}. {river} / {reach} / RS {rs}: {len(htab)} elevations")

            # Test access
            first_key = list(all_htabs.keys())[0]
            first_htab = all_htabs[first_key]

            print(f"\nAccessing first HTAB: {first_key}")
            print(f"  Elevations: {len(first_htab)}")
            print(f"  Elevation range: {first_htab['Elevation'].min():.2f} to {first_htab['Elevation'].max():.2f}")

            # Validate
            assert len(all_htabs) > 0, "No HTABs extracted"
            for key, htab in all_htabs.items():
                assert len(htab) > 0, f"Empty HTAB for {key}"
                assert 'Elevation' in htab.columns, f"Missing Elevation for {key}"

            print("\nPASS: get_all_xs_htabs()")
            return True
        else:
            print("SKIP: No HTABs extracted")
            return False

    except Exception as e:
        print(f"\nFAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_htab_analysis():
    """Test using HTAB for hydraulic analysis"""
    print("\n" + "="*70)
    print("TEST 3: HTAB Analysis - Rating Curves & Calculations")
    print("="*70)

    if not HDF_FILE.exists():
        print(f"SKIP: Test file not found: {HDF_FILE}")
        return False

    try:
        import h5py
        with h5py.File(HDF_FILE, 'r') as hdf:
            if '/Geometry/Cross Sections/Attributes' in hdf:
                attrs = hdf['/Geometry/Cross Sections/Attributes'][:]
                if len(attrs) > 0:
                    first_xs = attrs[0]
                    river = first_xs['River'].decode('utf-8').strip()
                    reach = first_xs['Reach'].decode('utf-8').strip()
                    rs = first_xs['RS'].decode('utf-8').strip()

                    # Extract HTAB
                    htab = HdfHydraulicTables.get_xs_htab(HDF_FILE, river, reach, rs)

                    print(f"\nAnalyzing HTAB for: {river} / {reach} / RS {rs}")

                    # Calculate hydraulic radius
                    htab['Hydraulic_Radius'] = htab['Area_Total'] / htab['Wetted_Perimeter_Total']

                    print(f"\nHydraulic Properties:")
                    print(f"  Max Area: {htab['Area_Total'].max():.1f} sq ft")
                    print(f"  Max Conveyance: {htab['Conveyance_Total'].max():.1f} cfs")
                    print(f"  Max Hydraulic Radius: {htab['Hydraulic_Radius'].max():.2f} ft")
                    print(f"  Max Top Width: {htab['Top_Width'].max():.1f} ft")

                    # Find properties at specific elevation (if available)
                    if len(htab) > 10:
                        mid_idx = len(htab) // 2
                        target_elev = htab.loc[mid_idx, 'Elevation']

                        print(f"\nProperties at elevation {target_elev:.2f} ft:")
                        print(f"  Area: {htab.loc[mid_idx, 'Area_Total']:.1f} sq ft")
                        print(f"  Conveyance: {htab.loc[mid_idx, 'Conveyance_Total']:.1f} cfs")
                        print(f"  Wetted Perimeter: {htab.loc[mid_idx, 'Wetted_Perimeter_Total']:.1f} ft")
                        print(f"  Top Width: {htab.loc[mid_idx, 'Top_Width']:.1f} ft")
                        print(f"  Hydraulic Radius: {htab.loc[mid_idx, 'Hydraulic_Radius']:.2f} ft")

                    # Validate calculations
                    assert htab['Area_Total'].max() > 0, "Invalid area values"
                    assert htab['Conveyance_Total'].max() >= 0, "Invalid conveyance values"
                    assert not htab['Hydraulic_Radius'].isna().all(), "All hydraulic radius values are NaN"

                    print("\nPASS: HTAB analysis")
                    return True
                else:
                    print("SKIP: No cross sections found")
                    return False
            else:
                print("SKIP: No Attributes found")
                return False

    except Exception as e:
        print(f"\nFAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "#"*70)
    print("# HdfHydraulicTables Test Suite")
    print("#"*70)

    tests = [
        test_get_xs_htab_single,
        test_get_all_xs_htabs,
        test_htab_analysis,
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
    skipped = sum(1 for r in results if r is False)
    total = len(results)
    print(f"# Results: {passed}/{total} tests passed, {skipped} skipped")
    print("#"*70)

    if all(r is not False or r is None for r in results):
        if passed > 0:
            print("\nTESTS PASSED")
        else:
            print("\nALL TESTS SKIPPED")
    else:
        print(f"\nSOME TESTS FAILED")

    return all(r is not False for r in results)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
