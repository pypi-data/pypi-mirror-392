"""
Test to simulate the production error scenario and verify the fix.

This simulates the exact error that occurred in production where
stocking_lord was called with dictionary-based item parameters.
"""
import sys
from pathlib import Path
import warnings

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from EqUMP.linking import stocking_lord

print("=" * 70)
print("Production Error Scenario Test")
print("=" * 70)

# Simulate production data: raw dictionaries (old API)
items_new = {
    1: {"a": 1.2, "b": 0.5, "c": 0.2},
    2: {"a": 1.0, "b": -0.3, "c": 0.15},
    3: {"a": 0.9, "b": 0.1, "c": 0.18},
}

items_old = {
    1: {"a": 1.15, "b": 0.48, "c": 0.18},
    2: {"a": 0.95, "b": -0.28, "c": 0.14},
    3: {"a": 0.88, "b": 0.12, "c": 0.16},
}

print("\nTest 1: Calling stocking_lord with dictionaries (simulating production)")
print("-" * 70)

try:
    # This should now raise a clear TypeError with helpful message
    A, B = stocking_lord(
        items_new=items_new,
        items_old=items_old,
        common_new=[1, 2, 3],
        common_old=[1, 2, 3],
        quadrature="gauss_hermite",
        nq=30,
        symmetry=True
    )
    
    print(f"✗ FAILED: Should have raised TypeError but didn't")
    sys.exit(1)
            
except AttributeError as e:
    print(f"✗ FAILED with AttributeError (old bug - not fixed properly):")
    print(f"  {e}")
    sys.exit(1)
except TypeError as e:
    # This is expected - clear error message telling user to convert to IRF objects
    print(f"✓ SUCCESS! Clear TypeError raised with helpful message:")
    print(f"  {e}")
    print(f"\n✓ This is the correct behavior - user must convert dicts to IRF objects")
except Exception as e:
    print(f"✗ FAILED with unexpected error:")
    print(f"  {type(e).__name__}: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("Test 2: Calling stocking_lord with IRF objects (recommended API)")
print("-" * 70)

from EqUMP.base import IRF

# Convert to IRF objects (recommended approach)
items_new_irf = {
    k: IRF(v, model="3PL", D=1.7) 
    for k, v in items_new.items()
}

items_old_irf = {
    k: IRF(v, model="3PL", D=1.7) 
    for k, v in items_old.items()
}

try:
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        A2, B2 = stocking_lord(
            items_new=items_new_irf,
            items_old=items_old_irf,
            common_new=[1, 2, 3],
            common_old=[1, 2, 3],
            quadrature="gauss_hermite",
            nq=30,
            symmetry=True
        )
        
        print(f"✓ SUCCESS!")
        print(f"  Linking coefficients: A={A2:.4f}, B={B2:.4f}")
        
        # Should have no deprecation warnings
        deprecation_warnings = [warning for warning in w if issubclass(warning.category, DeprecationWarning)]
        if not deprecation_warnings:
            print(f"\n✓ No deprecation warnings (as expected)")
        else:
            print(f"\n⚠ Warning: Unexpected deprecation warnings:")
            for warning in deprecation_warnings:
                print(f"  - {warning.message}")
                
except Exception as e:
    print(f"✗ FAILED:")
    print(f"  {type(e).__name__}: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✓ ALL TESTS PASSED - Production error is fixed!")
print("=" * 70)
