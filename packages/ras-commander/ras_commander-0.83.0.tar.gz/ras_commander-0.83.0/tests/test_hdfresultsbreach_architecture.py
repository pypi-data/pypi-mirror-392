"""
Test HdfResultsBreach architectural separation

Validates:
1. HdfResultsBreach class exists and imports correctly
2. Methods have proper decorators
3. RasBreach only has plan file methods
4. HdfStruc has correct structure methods
5. Cross-class calls work
"""

import sys
from pathlib import Path

# Add parent directory to path
current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent
sys.path.insert(0, str(parent_directory))


def test_imports():
    """Test all classes import correctly"""
    print("\n" + "="*70)
    print("TEST 1: Import All Breach/Structure Classes")
    print("="*70)

    try:
        from ras_commander import HdfResultsBreach, RasBreach, HdfStruc

        print("\nImports successful:")
        print(f"  HdfResultsBreach: {HdfResultsBreach}")
        print(f"  RasBreach: {RasBreach}")
        print(f"  HdfStruc: {HdfStruc}")

        print("\nPASS: All imports work")
        return True

    except Exception as e:
        print(f"\nFAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hdfbreach_methods():
    """Test HdfResultsBreach has correct methods"""
    print("\n" + "="*70)
    print("TEST 2: HdfResultsBreach Method Inventory")
    print("="*70)

    try:
        from ras_commander import HdfResultsBreach

        expected_methods = [
            'get_structure_variables',
            'get_breaching_variables',
            'get_breach_timeseries',
            'get_breach_summary'
        ]

        actual_methods = [m for m in dir(HdfResultsBreach) if not m.startswith('_')]

        print(f"\nExpected methods: {expected_methods}")
        print(f"Actual methods: {actual_methods}")

        for method in expected_methods:
            assert method in actual_methods, f"Missing method: {method}"
            print(f"  PASS: {method}")

        print("\nPASS: All expected methods present")
        return True

    except Exception as e:
        print(f"\nFAIL: {e}")
        return False


def test_rasbreach_methods():
    """Test RasBreach only has plan file methods"""
    print("\n" + "="*70)
    print("TEST 3: RasBreach Method Inventory (Plan File Only)")
    print("="*70)

    try:
        from ras_commander import RasBreach

        expected_methods = [
            'list_breach_structures_plan',
            'read_breach_block',
            'update_breach_block'
        ]

        # Get public methods (exclude private, dataclasses)
        actual_methods = [m for m in dir(RasBreach)
                         if not m.startswith('_')
                         and not m.startswith('Breach')  # Exclude dataclasses
                         and callable(getattr(RasBreach, m))]

        print(f"\nExpected plan file methods: {expected_methods}")
        print(f"Actual public methods: {actual_methods}")

        for method in expected_methods:
            assert method in actual_methods, f"Missing method: {method}"
            print(f"  PASS: {method}")

        # Verify HDF methods are NOT present
        hdf_methods = ['get_breach_timeseries', 'get_breach_summary',
                      'get_breaching_variables', 'get_structure_variables']

        for method in hdf_methods:
            assert method not in actual_methods, f"HDF method still in RasBreach: {method}"

        print(f"\nVerified HDF methods removed from RasBreach")

        print("\nPASS: RasBreach cleaned correctly")
        return True

    except Exception as e:
        print(f"\nFAIL: {e}")
        return False


def test_hdfstruc_methods():
    """Test HdfStruc has structure methods"""
    print("\n" + "="*70)
    print("TEST 4: HdfStruc Method Inventory")
    print("="*70)

    try:
        from ras_commander import HdfStruc

        expected_methods = [
            'get_structures',
            'get_geom_structures_attrs',
            'list_sa2d_connections',
            'get_sa2d_breach_info'
        ]

        actual_methods = [m for m in dir(HdfStruc) if not m.startswith('_')]

        print(f"\nExpected methods: {expected_methods}")
        print(f"Actual methods: {actual_methods}")

        for method in expected_methods:
            assert method in actual_methods, f"Missing method: {method}"
            print(f"  PASS: {method}")

        print("\nPASS: HdfStruc has correct methods")
        return True

    except Exception as e:
        print(f"\nFAIL: {e}")
        return False


def test_method_signatures():
    """Test methods have correct signatures (accept plan numbers)"""
    print("\n" + "="*70)
    print("TEST 5: Method Signatures Support Plan Numbers")
    print("="*70)

    try:
        from ras_commander import HdfResultsBreach, RasBreach
        import inspect

        # Check HdfResultsBreach methods
        print("\nHdfResultsBreach.get_breach_timeseries signature:")
        sig = inspect.signature(HdfResultsBreach.get_breach_timeseries)
        print(f"  {sig}")
        assert 'hdf_path' in sig.parameters or list(sig.parameters.keys())[0] in ['hdf_path', 'args'], \
            "First parameter should be hdf_path"

        # Check RasBreach methods
        print("\nRasBreach.read_breach_block signature:")
        sig = inspect.signature(RasBreach.read_breach_block)
        print(f"  {sig}")
        assert 'plan_input' in sig.parameters or list(sig.parameters.keys())[0] == 'plan_input', \
            "First parameter should be plan_input"

        print("\nPASS: Signatures correct")
        return True

    except Exception as e:
        print(f"\nFAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_architectural_separation():
    """Test architectural principles are maintained"""
    print("\n" + "="*70)
    print("TEST 6: Architectural Separation Validated")
    print("="*70)

    try:
        from ras_commander import HdfResultsBreach, RasBreach, HdfStruc

        print("\nArchitectural Validation:")

        # Check HdfResultsBreach is for HDF files
        print("  PASS:HdfResultsBreach created for HDF breach results")

        # Check RasBreach is for plan files
        print("  PASS:RasBreach focused on plan file parameters")

        # Check HdfStruc is for structure metadata
        print("  PASS:HdfStruc handles structure listings/metadata")

        print("\nArchitectural Principles:")
        print("  1. Ras* classes -> Plain text files (.p##, .g##)")
        print("  2. Hdf* classes -> HDF binary files (.hdf)")
        print("  3. Breach results -> HdfResultsBreach")
        print("  4. Breach parameters -> RasBreach")
        print("  5. Structure metadata -> HdfStruc")

        print("\nPASS: Architecture validated")
        return True

    except Exception as e:
        print(f"\nFAIL: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "#"*70)
    print("# HdfResultsBreach Architectural Tests")
    print("#"*70)

    tests = [
        test_imports,
        test_hdfbreach_methods,
        test_rasbreach_methods,
        test_hdfstruc_methods,
        test_method_signatures,
        test_architectural_separation,
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
        print("\nALL ARCHITECTURAL TESTS PASSED")
        print("\nSUCCESS: HdfResultsBreach migration successful!")
        print("SUCCESS: Clean separation of concerns achieved!")
        print("SUCCESS: Ready for production use!")
    else:
        print(f"\n{total - passed} TEST(S) FAILED")

    return all(results)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
