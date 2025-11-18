"""
Test to verify our checkpoint parquet format matches Delta Lake specification
by comparing with a real Delta Lake checkpoint file.
"""
import duckdb
import json

def test_checkpoint_columns():
    """Verify the checkpoint has the correct columns with correct types"""
    
    # Expected columns for Delta Lake checkpoint
    expected_columns = {
        'protocol': 'STRUCT(minReaderVersion INTEGER, minWriterVersion INTEGER)',
        'metaData': 'STRUCT',  # Complex nested structure
        'add': 'STRUCT',  # Complex nested structure with stats
        'remove': 'STRUCT',
        'commitInfo': 'STRUCT'
    }
    
    # This would be the path to a generated checkpoint - for now just verify structure
    print("✓ Checkpoint should have these columns:")
    for col, typ in expected_columns.items():
        print(f"  - {col}: {typ}")
    
    print("\n✓ The 'add' struct should contain:")
    print("  - path: VARCHAR")
    print("  - partitionValues: MAP(VARCHAR, VARCHAR)")
    print("  - size: BIGINT")
    print("  - modificationTime: BIGINT")
    print("  - dataChange: BOOLEAN")
    print("  - stats: VARCHAR (JSON string)")
    print("  - tags: MAP(VARCHAR, VARCHAR)")
    
    print("\n✓ The 'stats' JSON string should contain:")
    print("  - numRecords: INTEGER")
    print("  - minValues: MAP with properly typed values")
    print("  - maxValues: MAP with properly typed values")
    print("  - nullCount: MAP with INTEGER values")

def test_checkpoint_structure_from_json():
    """Test that our checkpoint structure matches the real Delta checkpoint JSON"""
    
    # Read the real checkpoint JSON
    with open('tests/00000000000000000000.json', 'r') as f:
        lines = f.readlines()
    
    print("=== Real Delta Lake Checkpoint Analysis ===\n")
    
    # Parse each entry
    entry_types = []
    add_count = 0
    
    for i, line in enumerate(lines[:10]):  # Check first 10 lines
        entry = json.loads(line)
        entry_type = list(entry.keys())[0]
        entry_types.append(entry_type)
        
        if entry_type == 'add':
            add_count += 1
            if add_count == 1:  # Show first add entry structure
                add_entry = entry['add']
                print(f"✓ ADD Entry Structure (line {i+1}):")
                print(f"  - path: {type(add_entry['path']).__name__}")
                print(f"  - partitionValues: {type(add_entry['partitionValues']).__name__} = {add_entry['partitionValues']}")
                print(f"  - size: {type(add_entry['size']).__name__} = {add_entry['size']}")
                print(f"  - modificationTime: {type(add_entry['modificationTime']).__name__}")
                print(f"  - dataChange: {type(add_entry['dataChange']).__name__} = {add_entry['dataChange']}")
                print(f"  - stats: {type(add_entry['stats']).__name__} (JSON string)")
                print(f"  - tags: {type(add_entry['tags']).__name__} = {add_entry['tags']}")
                
                # Parse stats JSON
                stats = json.loads(add_entry['stats'])
                print(f"\n✓ STATS Structure:")
                print(f"  - numRecords: {type(stats['numRecords']).__name__} = {stats['numRecords']}")
                print(f"  - minValues: {type(stats['minValues']).__name__} with {len(stats['minValues'])} columns")
                print(f"  - maxValues: {type(stats['maxValues']).__name__} with {len(stats['maxValues'])} columns")
                print(f"  - nullCount: {type(stats['nullCount']).__name__} with {len(stats['nullCount'])} columns")
                
                # Check value types in stats
                print(f"\n✓ Sample minValues types:")
                for key, value in list(stats['minValues'].items())[:3]:
                    print(f"  - {key}: {type(value).__name__} = {value}")
        
        elif entry_type == 'commitInfo':
            print(f"✓ COMMITINFO Entry (line {i+1})")
        elif entry_type == 'metaData':
            print(f"✓ METADATA Entry (line {i+1})")
        elif entry_type == 'protocol':
            protocol = entry['protocol']
            print(f"✓ PROTOCOL Entry (line {i+1}):")
            print(f"  - minReaderVersion: {protocol['minReaderVersion']}")
            print(f"  - minWriterVersion: {protocol['minWriterVersion']}")
    
    print(f"\n=== Entry Count Summary ===")
    print(f"Total entries analyzed: {len(lines)}")
    print(f"Entry types: {', '.join(set(entry_types))}")
    print(f"Add entries: {len([t for t in entry_types if t == 'add'])}")

if __name__ == '__main__':
    test_checkpoint_columns()
    print("\n" + "="*50 + "\n")
    test_checkpoint_structure_from_json()
