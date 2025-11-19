"""
Test RasGeometry connection methods

Tests Item 6: SA/2D Connection operations
"""

import sys
from pathlib import Path

# Add parent directory to path
current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent
sys.path.insert(0, str(parent_directory))

from ras_commander import RasGeometry

# Test data file - BaldEagleDamBrk has SA/2D connections
GEOM_FILE = Path(r"C:\GH\ras-commander\research\geometry file parsing\Example Geometries\BaldEagleDamBrk.g01")


def test_get_connections():
    """Test listing all connections"""
    print("\n" + "="*70)
    print("TEST 1: get_connections()")
    print("="*70)

    if not GEOM_FILE.exists():
        print(f"SKIP: Test file not found: {GEOM_FILE}")
        return False

    try:
        # Get all connections
        conn_df = RasGeometry.get_connections(GEOM_FILE)

        print(f"\nConnections found: {len(conn_df)}")

        if len(conn_df) > 0:
            print(f"\nColumns available:")
            for col in conn_df.columns:
                print(f"  - {col}")

            print(f"\nAll connections:")
            print(conn_df[['Connection_Name', 'Upstream_Area', 'Downstream_Area', 'Weir_Width']])

            print(f"\nConnection summary:")
            print(f"  Weir width range: {conn_df['Weir_Width'].min():.1f} to {conn_df['Weir_Width'].max():.1f} ft")
            print(f"  Weir coefficient range: {conn_df['Weir_Coefficient'].min():.2f} to {conn_df['Weir_Coefficient'].max():.2f}")
            print(f"  Connections with gates: {conn_df['Num_Gates'].sum()}")

            # Validate
            assert len(conn_df) > 0, "No connections found"
            assert 'Connection_Name' in conn_df.columns, "Missing Connection_Name"
            assert 'Upstream_Area' in conn_df.columns, "Missing Upstream_Area"
            assert 'Downstream_Area' in conn_df.columns, "Missing Downstream_Area"

            print("\nPASS: get_connections()")
            return True
        else:
            print("SKIP: No connections found")
            return False

    except Exception as e:
        print(f"\nFAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_connection_weir_profile():
    """Test reading connection weir profile"""
    print("\n" + "="*70)
    print("TEST 2: get_connection_weir_profile()")
    print("="*70)

    if not GEOM_FILE.exists():
        print(f"SKIP: Test file not found: {GEOM_FILE}")
        return False

    try:
        # Get connections
        conn_df = RasGeometry.get_connections(GEOM_FILE)

        if len(conn_df) == 0:
            print("SKIP: No connections found")
            return False

        # Get profile for first connection
        conn_name = conn_df.iloc[0]['Connection_Name']

        print(f"\nReading weir profile for connection: {conn_name}")
        print(f"  Upstream: {conn_df.iloc[0]['Upstream_Area']}")
        print(f"  Downstream: {conn_df.iloc[0]['Downstream_Area']}")
        print(f"  Expected SE points: {conn_df.iloc[0]['SE_Count']}")

        profile = RasGeometry.get_connection_weir_profile(GEOM_FILE, conn_name)

        print(f"\nWeir Profile:")
        print(f"  Points: {len(profile)}")
        print(f"  Station range: {profile['Station'].min():.1f} to {profile['Station'].max():.1f}")
        print(f"  Elevation range: {profile['Elevation'].min():.2f} to {profile['Elevation'].max():.2f}")

        print(f"\nFirst 5 points:")
        print(profile.head())

        # Validate
        assert len(profile) > 0, "No profile data"
        assert 'Station' in profile.columns, "Missing Station"
        assert 'Elevation' in profile.columns, "Missing Elevation"

        print("\nPASS: get_connection_weir_profile()")
        return True

    except Exception as e:
        print(f"\nFAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_connection_gates():
    """Test reading connection gate definitions"""
    print("\n" + "="*70)
    print("TEST 3: get_connection_gates()")
    print("="*70)

    if not GEOM_FILE.exists():
        print(f"SKIP: Test file not found: {GEOM_FILE}")
        return False

    try:
        # Get connections
        conn_df = RasGeometry.get_connections(GEOM_FILE)

        if len(conn_df) == 0:
            print("SKIP: No connections found")
            return False

        # Find connection with gates
        conn_with_gates = conn_df[conn_df['Num_Gates'] > 0]

        if len(conn_with_gates) == 0:
            print("SKIP: No connections with gates found")
            return False

        # Get gates for first connection with gates
        conn_name = conn_with_gates.iloc[0]['Connection_Name']

        print(f"\nReading gates for connection: {conn_name}")
        print(f"  Expected gates: {conn_with_gates.iloc[0]['Num_Gates']}")

        gates = RasGeometry.get_connection_gates(GEOM_FILE, conn_name)

        print(f"\nGates found: {len(gates)}")

        if len(gates) > 0:
            print(f"\nGate parameters:")
            print(gates[['Gate_Name', 'Width', 'Height', 'Invert', 'Gate_Coefficient']])

            # Validate
            assert len(gates) > 0, "No gates extracted"
            assert 'Gate_Name' in gates.columns, "Missing Gate_Name"
            assert 'Width' in gates.columns, "Missing Width"
            assert 'Height' in gates.columns, "Missing Height"

            print("\nPASS: get_connection_gates()")
            return True
        else:
            print("No gates extracted")
            return False

    except Exception as e:
        print(f"\nFAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_connections():
    """Test processing all connections"""
    print("\n" + "="*70)
    print("TEST 4: Process All Connections")
    print("="*70)

    if not GEOM_FILE.exists():
        print(f"SKIP: Test file not found: {GEOM_FILE}")
        return False

    try:
        # Get all connections
        conn_df = RasGeometry.get_connections(GEOM_FILE)

        print(f"\nProcessing {len(conn_df)} connections...")

        success_count = 0
        for idx, conn in conn_df.iterrows():
            conn_name = conn['Connection_Name']

            try:
                # Try to get weir profile
                profile = RasGeometry.get_connection_weir_profile(GEOM_FILE, conn_name)
                print(f"  {idx+1}. {conn_name}: {len(profile)} profile points", end="")

                # Try to get gates
                gates = RasGeometry.get_connection_gates(GEOM_FILE, conn_name)
                print(f", {len(gates)} gates")

                success_count += 1

            except Exception as e:
                print(f"  {idx+1}. {conn_name}: ERROR - {e}")

        print(f"\nSuccessfully processed {success_count}/{len(conn_df)} connections")

        assert success_count > 0, "No connections processed successfully"

        print("\nPASS: All connections processed")
        return True

    except Exception as e:
        print(f"\nFAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "#"*70)
    print("# RasGeometry SA/2D Connection Tests")
    print("#"*70)

    tests = [
        test_get_connections,
        test_get_connection_weir_profile,
        test_get_connection_gates,
        test_all_connections,
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
