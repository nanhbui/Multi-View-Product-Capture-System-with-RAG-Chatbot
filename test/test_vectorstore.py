#!/usr/bin/env python3
"""
Test Vector Store Initialization
"""

import sys
sys.path.insert(0, 'phase_2')

from data_processor import DataProcessor
from pathlib import Path

print("="*80)
print("VECTOR STORE INITIALIZATION TEST")
print("="*80)

# Initialize data processor
print("\n[STEP 1] Initializing DataProcessor...")
try:
    processor = DataProcessor()
    print("✅ DataProcessor initialized")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check MongoDB data
print("\n[STEP 2] Checking MongoDB for session data...")
try:
    records = processor.get_all_product_records()
    print(f"✅ Found {len(records)} product records in MongoDB")

    if records:
        for record in records:
            print(f"\n   Session: {record.session_id}")
            print(f"   - Angles: {record.total_angles}")
            print(f"   - Created: {record.created_at}")
    else:
        print("\n⚠️  No records found in MongoDB yet")
        print("   This is expected if you haven't processed any metadata files")

except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Try to process latest metadata file
print("\n[STEP 3] Looking for latest metadata file to process...")
captured_images = Path("captured_images")
metadata_files = list(captured_images.glob("*/metadata.json"))

if metadata_files:
    latest_file = str(max(metadata_files, key=lambda p: p.stat().st_mtime))
    print(f"✅ Found: {latest_file}")

    # Check if already processed
    with open(latest_file, 'r') as f:
        import json
        metadata = json.load(f)
        session_id = metadata['session_id']

    existing = processor.get_product_record(session_id)
    if existing:
        print(f"   ℹ️  Session {session_id} already in MongoDB (skipping re-processing)")
    else:
        print(f"\n   Processing {session_id}...")
        print("   Note: This will call OpenAI Vision API and may take time...")

        response = input("   Process this session? [y/N]: ").strip().lower()
        if response == 'y':
            try:
                record = processor.process_session_metadata(
                    metadata_file_path=latest_file,
                    product_id=None,
                    notes="Processed by test_vectorstore.py"
                )
                if record:
                    print(f"   ✅ Session processed successfully")
                else:
                    print(f"   ❌ Processing failed")
            except Exception as e:
                print(f"   ❌ Error: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("   Skipped processing")
else:
    print("⚠️  No metadata files found")

# Initialize vector store
print("\n[STEP 4] Initializing vector store...")
try:
    # Get all records again (in case we just processed one)
    records = processor.get_all_product_records()

    if not records:
        print("⚠️  Cannot initialize vector store: No product records in MongoDB")
        print("   To fix this:")
        print("   1. Run Phase 1 capture system to create images")
        print("   2. Run Phase 2 chatbot with --process-metadata to process them")
        print("   3. Or answer 'y' above to process the latest metadata file")
    else:
        print(f"   Found {len(records)} records to index...")
        success = processor.initialize_vector_store()

        if success:
            print("✅ Vector store initialized successfully")

            # Test retrieval
            print("\n[STEP 5] Testing vector store retrieval...")
            vector_store = processor.get_vector_store()

            if vector_store:
                # Try a simple query
                test_query = "what is this product?"
                results = vector_store.similarity_search_with_score(test_query, k=2)

                print(f"   Query: '{test_query}'")
                print(f"   Results: {len(results)} documents")

                for i, (doc, score) in enumerate(results, 1):
                    print(f"\n   [{i}] Score: {score:.3f}")
                    print(f"       Session: {doc.metadata.get('session_id')}")
                    print(f"       Content preview: {doc.page_content[:100]}...")

            else:
                print("❌ Vector store not available after initialization")
        else:
            print("❌ Vector store initialization failed")

except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Cleanup
processor.close()

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
