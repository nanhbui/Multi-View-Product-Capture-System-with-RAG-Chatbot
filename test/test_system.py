"""
End-to-End Test Script for Multi-View Product Capture System

This script tests:
1. MongoDB connection
2. Data processor initialization
3. Metadata processing
4. Vector store initialization
5. Chatbot initialization

Author: Expert Python Software Engineer
Date: 2025-12-05
"""

import os
import json
from pathlib import Path
from datetime import datetime

# Import components
from phase_2.data_processor import DataProcessor
from phase_2.chatbot_rag import ProductRAGChatbot

def create_test_metadata():
    """Create a test metadata file for testing."""
    test_metadata = {
        "session_id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "total_angles": 3,
        "metadata": [
            {
                "angle_number": 1,
                "image_path": "test_images/angle_1.jpg",
                "timestamp": datetime.now().isoformat(),
                "bbox": {
                    "x1": 100.0,
                    "y1": 100.0,
                    "x2": 400.0,
                    "y2": 400.0
                },
                "bbox_area": 90000.0,
                "track_id": 5,
                "confidence": 0.92,
                "iqa_passed": True,
                "iqa_reason": "Quality checks passed"
            },
            {
                "angle_number": 2,
                "image_path": "test_images/angle_2.jpg",
                "timestamp": datetime.now().isoformat(),
                "bbox": {
                    "x1": 110.0,
                    "y1": 105.0,
                    "x2": 410.0,
                    "y2": 405.0
                },
                "bbox_area": 90000.0,
                "track_id": 5,
                "confidence": 0.89,
                "iqa_passed": True,
                "iqa_reason": "Quality checks passed"
            },
            {
                "angle_number": 3,
                "image_path": "test_images/angle_3.jpg",
                "timestamp": datetime.now().isoformat(),
                "bbox": {
                    "x1": 105.0,
                    "y1": 100.0,
                    "x2": 405.0,
                    "y2": 400.0
                },
                "bbox_area": 90000.0,
                "track_id": 5,
                "confidence": 0.91,
                "iqa_passed": True,
                "iqa_reason": "Quality checks passed"
            }
        ]
    }

    # Create test directory
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)

    # Save metadata
    metadata_file = test_dir / "test_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(test_metadata, f, indent=2)

    print(f"[INFO] Test metadata created: {metadata_file}")
    return str(metadata_file)


def test_mongodb_connection():
    """Test 1: MongoDB Connection"""
    print("\n" + "="*60)
    print("TEST 1: MongoDB Connection")
    print("="*60)

    try:
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        print(f"[INFO] Connecting to MongoDB: {mongodb_uri}")

        data_processor = DataProcessor(mongodb_uri=mongodb_uri)
        print("[SUCCESS] MongoDB connected successfully")
        return data_processor

    except Exception as e:
        print(f"[FAILED] MongoDB connection failed: {e}")
        return None


def test_metadata_processing(data_processor, metadata_file):
    """Test 2: Metadata Processing"""
    print("\n" + "="*60)
    print("TEST 2: Metadata Processing")
    print("="*60)

    try:
        product_record = data_processor.process_session_metadata(
            metadata_file_path=metadata_file,
            product_id="TEST_PRODUCT_001",
            notes="End-to-end test product"
        )

        if product_record:
            print(f"[SUCCESS] Metadata processed successfully")
            print(f"  Session ID: {product_record.session_id}")
            print(f"  Total Angles: {product_record.total_angles}")
            print(f"  MVV Confidence: {product_record.mvv_result.confidence_score:.2f}")
            print(f"  MVV Verified: {product_record.mvv_result.verified}")
            return True
        else:
            print("[FAILED] Metadata processing failed")
            return False

    except Exception as e:
        print(f"[FAILED] Metadata processing error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vector_store(data_processor):
    """Test 3: Vector Store Initialization"""
    print("\n" + "="*60)
    print("TEST 3: Vector Store Initialization")
    print("="*60)

    try:
        success = data_processor.initialize_vector_store()

        if success:
            print("[SUCCESS] Vector store initialized")
            return True
        else:
            print("[FAILED] Vector store initialization failed")
            return False

    except Exception as e:
        print(f"[FAILED] Vector store error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chatbot_initialization(data_processor):
    """Test 4: Chatbot Initialization"""
    print("\n" + "="*60)
    print("TEST 4: Chatbot Initialization")
    print("="*60)

    try:
        chatbot = ProductRAGChatbot(
            data_processor=data_processor,
            product_context="Test Product"
        )

        print("[SUCCESS] Chatbot initialized successfully")
        return chatbot

    except Exception as e:
        print(f"[FAILED] Chatbot initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_chatbot_query(chatbot):
    """Test 5: Chatbot Query"""
    print("\n" + "="*60)
    print("TEST 5: Chatbot Query (In-Scope)")
    print("="*60)

    try:
        test_query = "What are the details of this product?"
        print(f"[INFO] Test query: {test_query}")

        result = chatbot.query(test_query)

        if result['success']:
            print("[SUCCESS] Query processed successfully")
            print(f"[RESPONSE] {result['response'][:200]}...")  # First 200 chars
            return True
        else:
            print("[FAILED] Query processing failed")
            return False

    except Exception as e:
        print(f"[FAILED] Query error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_out_of_scope_query(chatbot):
    """Test 6: Out-of-Scope Query"""
    print("\n" + "="*60)
    print("TEST 6: Chatbot Query (Out-of-Scope)")
    print("="*60)

    try:
        test_query = "What's the weather today?"
        print(f"[INFO] Test query: {test_query}")

        result = chatbot.query(test_query)

        if result['success']:
            print("[SUCCESS] Out-of-scope query handled")
            print(f"[RESPONSE] {result['response'][:200]}...")
            return True
        else:
            print("[WARNING] Query processing had issues")
            return False

    except Exception as e:
        print(f"[FAILED] Query error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("END-TO-END SYSTEM TEST")
    print("Multi-View Product Data Capture System")
    print("="*60)

    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("[ERROR] OPENAI_API_KEY not set in environment")
        print("[INFO] Please set OPENAI_API_KEY in .env file")
        return

    if not os.getenv("MONGODB_URI"):
        print("[WARNING] MONGODB_URI not set, using default: mongodb://localhost:27017/")

    # Create test metadata
    metadata_file = create_test_metadata()

    # Run tests
    results = {
        "mongodb_connection": False,
        "metadata_processing": False,
        "vector_store": False,
        "chatbot_init": False,
        "in_scope_query": False,
        "out_of_scope_query": False
    }

    # Test 1: MongoDB Connection
    data_processor = test_mongodb_connection()
    results["mongodb_connection"] = data_processor is not None

    if not data_processor:
        print("\n[FATAL] Cannot continue without MongoDB connection")
        return

    # Test 2: Metadata Processing
    results["metadata_processing"] = test_metadata_processing(data_processor, metadata_file)

    # Test 3: Vector Store
    results["vector_store"] = test_vector_store(data_processor)

    # Test 4: Chatbot Initialization
    chatbot = test_chatbot_initialization(data_processor)
    results["chatbot_init"] = chatbot is not None

    if chatbot:
        # Test 5: In-Scope Query
        results["in_scope_query"] = test_chatbot_query(chatbot)

        # Test 6: Out-of-Scope Query
        results["out_of_scope_query"] = test_out_of_scope_query(chatbot)

    # Print Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name.replace('_', ' ').title():.<40} {status}")

    total_tests = len(results)
    passed_tests = sum(results.values())
    print("="*60)
    print(f"Total: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.0f}%)")
    print("="*60 + "\n")

    # Cleanup
    data_processor.close()


if __name__ == "__main__":
    main()
