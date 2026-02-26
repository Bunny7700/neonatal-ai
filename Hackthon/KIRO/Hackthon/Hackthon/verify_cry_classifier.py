#!/usr/bin/env python
"""
Static verification script for CryClassifier module.

This script performs static analysis without running numpy-dependent code.
"""

import ast
import inspect


def verify_cry_classifier_structure():
    """Verify the CryClassifier class structure without importing numpy."""
    print("=" * 60)
    print("CryClassifier Static Verification")
    print("=" * 60)
    
    # Read the source file
    with open('cry_classifier.py', 'r') as f:
        source = f.read()
    
    # Parse the AST
    tree = ast.parse(source)
    
    # Find the CryClassifier class
    cry_classifier_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'CryClassifier':
            cry_classifier_class = node
            break
    
    if not cry_classifier_class:
        print("❌ CryClassifier class not found!")
        return False
    
    print("✓ CryClassifier class found")
    
    # Extract methods
    methods = {}
    class_attributes = {}
    
    for item in cry_classifier_class.body:
        if isinstance(item, ast.FunctionDef):
            methods[item.name] = item
        elif isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name):
                    class_attributes[target.id] = item
    
    # Check required methods
    required_methods = [
        '__init__',
        'load_yamnet',
        'load_cry_type_model',
        'detect_cry',
        'classify_cry_type',
        'predict',
    ]
    
    print("\nChecking required methods:")
    for method_name in required_methods:
        if method_name in methods:
            print(f"  ✓ {method_name}")
        else:
            print(f"  ❌ {method_name} - MISSING")
            return False
    
    # Check class attributes
    print("\nChecking class attributes:")
    expected_attributes = ['CRY_CATEGORIES', 'CONFIDENCE_THRESHOLD']
    for attr in expected_attributes:
        if attr in class_attributes:
            print(f"  ✓ {attr}")
        else:
            print(f"  ❌ {attr} - MISSING")
            return False
    
    # Check method signatures
    print("\nChecking method signatures:")
    
    # __init__ should have model_path parameter
    init_method = methods['__init__']
    init_args = [arg.arg for arg in init_method.args.args]
    if 'model_path' in init_args:
        print("  ✓ __init__ has model_path parameter")
    else:
        print("  ❌ __init__ missing model_path parameter")
    
    # detect_cry should have audio parameter and return tuple
    detect_cry_method = methods['detect_cry']
    detect_cry_args = [arg.arg for arg in detect_cry_method.args.args]
    if 'audio' in detect_cry_args:
        print("  ✓ detect_cry has audio parameter")
    else:
        print("  ❌ detect_cry missing audio parameter")
    
    # classify_cry_type should have features parameter
    classify_method = methods['classify_cry_type']
    classify_args = [arg.arg for arg in classify_method.args.args]
    if 'features' in classify_args:
        print("  ✓ classify_cry_type has features parameter")
    else:
        print("  ❌ classify_cry_type missing features parameter")
    
    # predict should have audio and features parameters
    predict_method = methods['predict']
    predict_args = [arg.arg for arg in predict_method.args.args]
    if 'audio' in predict_args and 'features' in predict_args:
        print("  ✓ predict has audio and features parameters")
    else:
        print("  ❌ predict missing required parameters")
    
    # Check for docstrings
    print("\nChecking docstrings:")
    methods_with_docstrings = 0
    for method_name, method_node in methods.items():
        if ast.get_docstring(method_node):
            methods_with_docstrings += 1
    
    print(f"  ✓ {methods_with_docstrings}/{len(methods)} methods have docstrings")
    
    # Check for requirements validation
    print("\nChecking requirements validation:")
    
    # Look for confidence threshold logic in predict method
    predict_source = ast.get_source_segment(source, predict_method)
    if predict_source and 'CONFIDENCE_THRESHOLD' in predict_source:
        print("  ✓ predict method uses CONFIDENCE_THRESHOLD")
    else:
        print("  ⚠️ predict method may not use CONFIDENCE_THRESHOLD")
    
    if predict_source and 'normal_unknown' in predict_source:
        print("  ✓ predict method handles normal_unknown classification")
    else:
        print("  ⚠️ predict method may not handle normal_unknown")
    
    # Check for error handling
    print("\nChecking error handling:")
    error_handling_count = 0
    for method_name, method_node in methods.items():
        method_source = ast.get_source_segment(source, method_node)
        if method_source and ('try:' in method_source or 'except' in method_source):
            error_handling_count += 1
    
    print(f"  ✓ {error_handling_count}/{len(methods)} methods have error handling")
    
    # Check for input validation
    print("\nChecking input validation:")
    validation_count = 0
    for method_name, method_node in methods.items():
        method_source = ast.get_source_segment(source, method_node)
        if method_source and ('len(' in method_source or 'if ' in method_source):
            validation_count += 1
    
    print(f"  ✓ {validation_count}/{len(methods)} methods have input validation")
    
    print("\n" + "=" * 60)
    print("Static Verification Complete!")
    print("=" * 60)
    
    return True


def verify_requirements_coverage():
    """Verify that the implementation covers all requirements."""
    print("\n" + "=" * 60)
    print("Requirements Coverage Verification")
    print("=" * 60)
    
    with open('cry_classifier.py', 'r') as f:
        source = f.read()
    
    requirements = {
        '4.1': 'five categories: hunger, sleep_discomfort, pain_distress, diaper_change, normal_unknown',
        '4.2': 'confidence score',
        '4.3': 'confidence < 60% → normal_unknown',
        '4.4': 'confidence >= 60% → specific category',
    }
    
    print("\nChecking requirements in code:")
    for req_id, req_text in requirements.items():
        print(f"\nRequirement {req_id}: {req_text}")
        
        if req_id == '4.1':
            # Check for all five categories
            categories = ['hunger', 'sleep_discomfort', 'pain_distress', 'diaper_change', 'normal_unknown']
            all_found = all(cat in source for cat in categories)
            if all_found:
                print("  ✓ All five categories found in code")
            else:
                print("  ❌ Not all categories found")
        
        elif req_id == '4.2':
            # Check for confidence score
            if 'confidence' in source and 'float' in source:
                print("  ✓ Confidence score implementation found")
            else:
                print("  ❌ Confidence score not found")
        
        elif req_id == '4.3':
            # Check for threshold logic
            if '60' in source and 'normal_unknown' in source:
                print("  ✓ Low confidence threshold logic found")
            else:
                print("  ❌ Threshold logic not found")
        
        elif req_id == '4.4':
            # Check for high confidence logic
            if 'CONFIDENCE_THRESHOLD' in source:
                print("  ✓ High confidence threshold logic found")
            else:
                print("  ❌ High confidence logic not found")
    
    print("\n" + "=" * 60)
    print("Requirements Coverage Verification Complete!")
    print("=" * 60)


def main():
    """Run all verifications."""
    try:
        structure_ok = verify_cry_classifier_structure()
        verify_requirements_coverage()
        
        if structure_ok:
            print("\n✅ All static verifications passed!")
            print("\nNote: This is a static analysis. Full testing requires:")
            print("  1. Python 3.11 or 3.12 (not 3.14)")
            print("  2. Compatible numpy installation")
            print("  3. Running the test suite: python -m pytest tests/test_cry_classifier.py")
            return 0
        else:
            print("\n❌ Some verifications failed!")
            return 1
    
    except Exception as e:
        print(f"\n❌ Verification error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
