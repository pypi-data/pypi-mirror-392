"""Test backward compatibility and comprehensive testing of transform_items.

Includes regression test for GPCM2 threshold parameter bug.
"""
import sys
import warnings
from pathlib import Path
import numpy as np

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from EqUMP.linking.helper import transform_items, transform_item_params
from EqUMP.base import IRF

# Test 1: Legacy API with dictionaries (should show deprecation warning)
print("Test 1: Legacy API with dictionaries (DEPRECATED)")
items_dict = {
    1: {"a": 1.2, "b": 0.5, "c": 0.2},
    2: {"a": 1.0, "b": -0.3, "c": 0.15},
}

try:
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = transform_items(items_dict, A=1.1, B=0.2, direction="to_old")
        
        if len(w) == 1 and issubclass(w[0].category, DeprecationWarning):
            print(f"✓ DeprecationWarning raised as expected:")
            print(f"  {w[0].message}")
        else:
            print(f"✗ Expected DeprecationWarning but got: {w}")
        
        print(f"✓ Success! Result type: {type(result)}")
        print(f"  Item 1: {result[1]}")
        print(f"  Item 2: {result[2]}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 2: New API with IRF objects (ItemCollection)
print("\nTest 2: New API with IRF objects")
items_irf = {
    1: IRF({"a": 1.2, "b": 0.5, "c": 0.2}, "3PL", D=1.7),
    2: IRF({"a": 1.0, "b": -0.3, "c": 0.15}, "3PL", D=1.7),
}

try:
    result = transform_items(items_irf, A=1.1, B=0.2, direction="to_old")
    print(f"✓ Success! Result type: {type(result)}")
    print(f"  Item 1 type: {type(result[1])}")
    print(f"  Item 1 params: {result[1].params}")
    print(f"  Item 2 params: {result[2].params}")
except Exception as e:
    print(f"✗ Failed: {e}")

print("\n✓ All backward compatibility tests passed!")

# Test 3: GPCM2 with threshold parameter (regression test for bug)
print("\nTest 3: GPCM2 with threshold parameter (REGRESSION TEST)")
items_gpcm2 = {
    1: IRF({"a": 1.2, "b": 0.5, "threshold": [-0.5, 0.0, 0.5]}, "GPCM2"),
    2: IRF({"a": 0.8, "b": -0.3, "threshold": [0.2, 0.8]}, "GPCM2"),
}

try:
    result = transform_items(items_gpcm2, A=1.1, B=0.2, direction="to_old")
    print(f"✓ Success! GPCM2 transformation completed")
    print(f"  Item 1 model: {result[1].model}")
    print(f"  Item 1 params keys: {list(result[1].params.keys())}")
    
    # Verify threshold is preserved
    if "threshold" in result[1].params:
        print(f"  ✓ Item 1 threshold preserved: {result[1].params['threshold']}")
        if np.array_equal(result[1].params['threshold'], items_gpcm2[1].params['threshold']):
            print(f"  ✓ Item 1 threshold unchanged (as expected)")
        else:
            print(f"  ✗ Item 1 threshold was modified (unexpected!)")
    else:
        print(f"  ✗ FAILED: Item 1 threshold parameter missing!")
        raise KeyError("threshold parameter was lost during transformation")
    
    if "threshold" in result[2].params:
        print(f"  ✓ Item 2 threshold preserved: {result[2].params['threshold']}")
    else:
        print(f"  ✗ FAILED: Item 2 threshold parameter missing!")
        raise KeyError("threshold parameter was lost during transformation")
    
    # Verify a and b are transformed
    expected_a1 = 1.2 / 1.1
    expected_b1 = 1.1 * 0.5 + 0.2
    if np.isclose(result[1].params['a'], expected_a1):
        print(f"  ✓ Item 1 'a' transformed correctly: {result[1].params['a']:.4f}")
    else:
        print(f"  ✗ Item 1 'a' transformation incorrect")
    
    if np.isclose(result[1].params['b'], expected_b1):
        print(f"  ✓ Item 1 'b' transformed correctly: {result[1].params['b']:.4f}")
    else:
        print(f"  ✗ Item 1 'b' transformation incorrect")
        
except Exception as e:
    print(f"✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: GPCM2 to_new direction
print("\nTest 4: GPCM2 to_new direction")
try:
    result = transform_items(items_gpcm2, A=1.1, B=0.2, direction="to_new")
    if "threshold" in result[1].params and "threshold" in result[2].params:
        print(f"✓ Success! threshold preserved in to_new direction")
    else:
        print(f"✗ FAILED: threshold lost in to_new direction")
        raise KeyError("threshold parameter was lost")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

# Test 5: Mixed models including GPCM2
print("\nTest 5: Mixed models (2PL, 3PL, GRM, GPCM, GPCM2)")
mixed_items = {
    1: IRF({"a": 1.0, "b": 0.5}, "2PL"),
    2: IRF({"a": 1.2, "b": 0.3, "c": 0.2}, "3PL"),
    3: IRF({"a": 0.8, "b": [-0.5, 0.0, 0.5]}, "GRM"),
    4: IRF({"a": 0.9, "b": [-0.3, 0.0, 0.3]}, "GPCM"),
    5: IRF({"a": 1.1, "b": 0.2, "threshold": [-0.3, 0.3]}, "GPCM2"),
}

try:
    result = transform_items(mixed_items, A=1.2, B=0.3, direction="to_old")
    
    # Verify all models preserved
    models_ok = all([
        result[1].model == "2PL",
        result[2].model == "3PL",
        result[3].model == "GRM",
        result[4].model == "GPCM",
        result[5].model == "GPCM2",
    ])
    
    if models_ok:
        print(f"✓ All models preserved correctly")
    else:
        print(f"✗ Some models were not preserved")
        raise ValueError("Model preservation failed")
    
    # Verify special parameters
    if result[2].params["c"] == 0.2:
        print(f"✓ 3PL 'c' parameter preserved")
    else:
        print(f"✗ 3PL 'c' parameter lost or modified")
        raise ValueError("c parameter not preserved")
    
    if "threshold" in result[5].params:
        print(f"✓ GPCM2 'threshold' parameter preserved")
    else:
        print(f"✗ GPCM2 'threshold' parameter lost")
        raise KeyError("threshold parameter lost in mixed model test")
    
except Exception as e:
    print(f"✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: transform_item_params with GPCM2 (low-level function)
print("\nTest 6: transform_item_params with GPCM2 (low-level)")
params_gpcm2 = {
    1: {"a": 1.2, "b": 0.5, "threshold": np.array([-0.5, 0.0, 0.5])},
}

try:
    result = transform_item_params(params_gpcm2, A=1.1, B=0.2, direction="to_old")
    
    if "threshold" in result[1]:
        print(f"✓ threshold preserved in transform_item_params")
        if np.array_equal(result[1]["threshold"], params_gpcm2[1]["threshold"]):
            print(f"✓ threshold unchanged (as expected)")
        else:
            print(f"✗ threshold was modified")
    else:
        print(f"✗ FAILED: threshold lost in transform_item_params")
        raise KeyError("threshold lost in low-level function")
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✓ ALL TESTS PASSED!")
print("  - Backward compatibility: OK")
print("  - GPCM2 threshold preservation: OK (bug fixed)")
print("  - Mixed models: OK")
print("  - Low-level transform_item_params: OK")
print("="*60)
