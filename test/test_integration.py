#!/usr/bin/env python3
"""
Integration Test Script for Phase 1 and Phase 2
Tests the complete data flow from capture to chatbot
"""

import sys
import json
from pathlib import Path
from datetime import datetime

print("="*80)
print("PHASE 1 → PHASE 2 INTEGRATION DIAGNOSTIC")
print("="*80)

# Test 1: Check metadata files
print("\n[TEST 1] Checking for metadata files...")
captured_images = Path("captured_images")

if not captured_images.exists():
    print("❌ FAILED: captured_images directory not found")
    sys.exit(1)

metadata_files = list(captured_images.glob("*/metadata.json"))
print(f"✅ Found {len(metadata_files)} metadata file(s)")

if metadata_files:
    latest = max(metadata_files, key=lambda p: p.stat().st_mtime)
    print(f"   Latest: {latest}")

    # Test 2: Validate metadata structure
    print("\n[TEST 2] Validating metadata structure...")
    try:
        with open(latest, 'r') as f:
            metadata = json.load(f)

        # Check for required fields
        required_fields = ['session_id', 'session_info', 'captures']
        missing = [f for f in required_fields if f not in metadata]

        if missing:
            print(f"❌ FAILED: Missing fields: {missing}")
        else:
            print(f"✅ Metadata structure valid")
            print(f"   Session ID: {metadata['session_id']}")
            print(f"   Total angles: {metadata['session_info']['total_angles']}")
            print(f"   Captured: {len(metadata['captures'])} angles")

            # Show first capture details
            if metadata['captures']:
                first_angle = list(metadata['captures'].values())[0]
                print(f"\n   Sample capture data:")
                print(f"   - Image: {first_angle['image']['filename']}")
                print(f"   - Confidence: {first_angle['detection']['confidence']:.2%}")
                print(f"   - Quality: {first_angle['quality_assessment']['overall_status']}")

    except Exception as e:
        print(f"❌ FAILED: Error reading metadata: {e}")
        import traceback
        traceback.print_exc()
else:
    print("⚠️  WARNING: No metadata files found. Run Phase 1 capture first.")

# Test 3: Check MongoDB connection
print("\n[TEST 3] Testing MongoDB connection...")
try:
    from pymongo import MongoClient

    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
    client.server_info()

    db = client['product_capture_db']
    collection = db['captures']

    count = collection.count_documents({})
    print(f"✅ MongoDB connected")
    print(f"   Database: product_capture_db")
    print(f"   Collection: captures")
    print(f"   Documents: {count}")

    if count > 0:
        latest_doc = collection.find_one(sort=[('last_updated', -1)])
        print(f"\n   Latest document:")
        print(f"   - Session ID: {latest_doc.get('session_id')}")
        print(f"   - Angles: {len(latest_doc.get('captures', {}))} captured")

    client.close()

except ImportError:
    print("❌ FAILED: pymongo not installed")
    print("   Run: pip install pymongo")
except Exception as e:
    print(f"❌ FAILED: MongoDB connection error: {e}")

# Test 4: Check Phase 2 dependencies
print("\n[TEST 4] Checking Phase 2 dependencies...")
dependencies = [
    ('openai', 'OpenAI SDK'),
    ('langchain', 'LangChain'),
    ('langchain_openai', 'LangChain OpenAI'),
    ('chromadb', 'ChromaDB'),
    ('pymongo', 'PyMongo'),
    ('pydantic', 'Pydantic')
]

all_installed = True
for module_name, display_name in dependencies:
    try:
        __import__(module_name)
        print(f"   ✅ {display_name}")
    except ImportError:
        print(f"   ❌ {display_name} - NOT INSTALLED")
        all_installed = False

if not all_installed:
    print("\n   Install missing dependencies:")
    print("   pip install -r requirements.txt")

# Test 5: Check environment variables
print("\n[TEST 5] Checking environment variables...")
try:
    from dotenv import load_dotenv
    import os

    load_dotenv()

    openai_key = os.getenv('OPENAI_API_KEY')
    mongodb_uri = os.getenv('MONGODB_URI')

    if openai_key and openai_key != '...':
        masked = openai_key[:8] + "..." + openai_key[-4:]
        print(f"   ✅ OPENAI_API_KEY: {masked}")
    else:
        print(f"   ❌ OPENAI_API_KEY: Not set or invalid")

    if mongodb_uri and mongodb_uri != '...':
        print(f"   ✅ MONGODB_URI: {mongodb_uri}")
    else:
        print(f"   ⚠️  MONGODB_URI: Using default (mongodb://localhost:27017/)")

except Exception as e:
    print(f"   ⚠️  Could not check environment: {e}")

# Test 6: Test data processor compatibility
print("\n[TEST 6] Testing data_processor compatibility...")
try:
    sys.path.insert(0, 'phase_2')
    from data_processor import DataProcessor

    # Initialize processor
    processor = DataProcessor()
    print("   ✅ DataProcessor initialized")

    # Test metadata processing with latest file
    if metadata_files:
        print(f"\n   Testing metadata conversion...")
        latest_file = str(max(metadata_files, key=lambda p: p.stat().st_mtime))

        # Just test loading, don't actually process (to avoid API calls)
        with open(latest_file, 'r') as f:
            test_data = json.load(f)

        # Check if it has the new format
        if 'captures' in test_data and 'session_info' in test_data:
            print("   ✅ Metadata format: New Phase 1 format (compatible)")
        else:
            print("   ⚠️  Metadata format: Unknown format")

    processor.close()

except ImportError as e:
    print(f"   ❌ FAILED: Cannot import data_processor: {e}")
except Exception as e:
    print(f"   ❌ FAILED: Error testing data_processor: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "="*80)
print("DIAGNOSTIC SUMMARY")
print("="*80)
print("\nNext steps:")
print("1. If metadata files exist: Run 'python phase_2/run_chatbot.py'")
print("2. If no metadata files: Run 'python phase_1/capture_system.py' first")
print("3. If dependencies missing: Run 'pip install -r requirements.txt'")
print("4. If MongoDB issues: Check that mongod service is running")
print("="*80)
