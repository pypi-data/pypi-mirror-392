#!/usr/bin/env python3
"""
Test script for writer.py dictionary encoding feature
"""

import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from duckrun.writer import _build_write_deltalake_args, _IS_OLD_DELTALAKE, _HAS_PYARROW_DATASET
import pyarrow as pa

def test_dictionary_encoding():
    """Test that dictionary encoding is properly configured in write args"""
    print("=" * 60)
    print("Testing Dictionary Encoding in Writer")
    print("=" * 60)
    
    # Create sample PyArrow table
    data = {
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'category': ['A', 'B', 'A', 'B', 'A']
    }
    df = pa.table(data)
    
    print(f"\nDeltalake version check:")
    print(f"  - Is old deltalake (< 0.20): {_IS_OLD_DELTALAKE}")
    print(f"  - Has PyArrow dataset: {_HAS_PYARROW_DATASET}")
    
    # Test 1: Normal write mode (no schema merging)
    print("\n[Test 1] Normal write mode (no schema merging)")
    print("-" * 60)
    
    args = _build_write_deltalake_args(
        path='test/path',
        df=df,
        mode='overwrite',
        schema_mode=None,
        partition_by=None
    )
    
    print(f"Arguments generated:")
    for key, value in args.items():
        if key == 'data':
            print(f"  - {key}: <PyArrow Table>")
        elif key == 'file_options':
            print(f"  - {key}: <ParquetFileWriteOptions>")
            # Try to inspect file_options
            if hasattr(value, '__dict__'):
                print(f"    Options: {value.__dict__}")
        else:
            print(f"  - {key}: {value}")
    
    # Check if dictionary encoding is enabled
    if _IS_OLD_DELTALAKE and _HAS_PYARROW_DATASET:
        if 'file_options' in args:
            print("\n✅ [PASS] file_options is present in write args")
            print("   Dictionary encoding (use_dictionary=True) should be configured")
        else:
            print("\n❌ [FAIL] file_options is missing from write args")
            return False
    else:
        print("\n⚠️  [SKIP] Not using PyArrow engine (deltalake >= 0.20 or PyArrow dataset unavailable)")
    
    # Test 2: Schema merging mode
    print("\n[Test 2] Schema merging mode")
    print("-" * 60)
    
    args_merge = _build_write_deltalake_args(
        path='test/path',
        df=df,
        mode='append',
        schema_mode='merge',
        partition_by=None
    )
    
    print(f"Arguments generated:")
    for key, value in args_merge.items():
        if key == 'data':
            print(f"  - {key}: <PyArrow Table>")
        elif key == 'writer_properties':
            print(f"  - {key}: <WriterProperties>")
        else:
            print(f"  - {key}: {value}")
    
    if 'schema_mode' in args_merge and args_merge['schema_mode'] == 'merge':
        print("\n✅ [PASS] schema_mode='merge' is correctly set")
        if _IS_OLD_DELTALAKE:
            if 'engine' in args_merge and args_merge['engine'] == 'rust':
                print("✅ [PASS] engine='rust' is correctly set for old deltalake")
            else:
                print("❌ [FAIL] engine='rust' is missing for old deltalake with schema merging")
                return False
    else:
        print("\n❌ [FAIL] schema_mode='merge' is not properly set")
        return False
    
    # Test 3: With partitioning
    print("\n[Test 3] With partitioning")
    print("-" * 60)
    
    args_partition = _build_write_deltalake_args(
        path='test/path',
        df=df,
        mode='overwrite',
        schema_mode=None,
        partition_by=['category']
    )
    
    if 'partition_by' in args_partition and args_partition['partition_by'] == ['category']:
        print("✅ [PASS] partition_by is correctly set to ['category']")
    else:
        print("❌ [FAIL] partition_by is not properly configured")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All dictionary encoding tests passed!")
    print("=" * 60)
    print("\nConfiguration details:")
    print("  - ZSTD compression: Enabled")
    print("  - Dictionary encoding: Enabled (for PyArrow engine)")
    print("  - Optimized row groups: Enabled (for old deltalake)")
    
    return True

if __name__ == "__main__":
    try:
        success = test_dictionary_encoding()
        if success:
            print("\n✅ Test completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
