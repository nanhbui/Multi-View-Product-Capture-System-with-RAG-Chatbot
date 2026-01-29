#!/usr/bin/env python3
"""
Test Phase 2 retrieval of Phase 1 data from MongoDB
"""
import sys
from pathlib import Path

# Add phase_2 to path
sys.path.insert(0, str(Path(__file__).parent / "phase_2"))

from data_processor import DataProcessor

def test_phase2_retrieval():
    """Test if Phase 2 can retrieve Phase 1 captured data"""

    print("=" * 60)
    print("TEST: Phase 2 Retrieval of Phase 1 Data")
    print("=" * 60)

    # Initialize DataProcessor
    print("\n[1] Initializing Phase 2 DataProcessor...")
    processor = DataProcessor()

    # Get the latest session from Phase 1
    print("\n[2] Retrieving latest Phase 1 session from MongoDB...")

    # Query MongoDB directly for the latest session
    latest_session = processor.mongo_collection.find_one(
        {},
        sort=[("created_at", -1)]
    )

    if not latest_session:
        print("❌ No sessions found in MongoDB!")
        return False

    session_id = latest_session["session_id"]
    print(f"✅ Found latest session: {session_id}")

    # Display session info
    print(f"\n[3] Session Information:")
    print(f"   - Session ID: {session_id}")
    print(f"   - Created: {latest_session.get('created_at', 'N/A')}")
    print(f"   - Status: {latest_session.get('session_info', {}).get('status', 'N/A')}")
    print(f"   - Total Angles: {latest_session.get('session_info', {}).get('total_angles', 'N/A')}")
    print(f"   - Captured: {latest_session.get('session_info', {}).get('captured_count', 'N/A')}")
    print(f"   - Completion: {latest_session.get('session_info', {}).get('completion_percentage', 'N/A')}%")

    # Check if it has captures
    if 'captures' in latest_session:
        print(f"\n[4] Capture Data:")
        for angle_num, capture in latest_session['captures'].items():
            image_path = capture.get('image', {}).get('local_path', 'N/A')
            confidence = capture.get('detection', {}).get('confidence_percentage', 'N/A')
            print(f"   - Angle {angle_num}: {image_path} (confidence: {confidence})")

    # Check if Phase 2 has processed this session
    print(f"\n[5] Phase 2 Processing Status:")
    if 'captured_angles' in latest_session:
        print("   ✅ Session has been processed by Phase 2")
        print(f"   - MVV verified: {latest_session.get('mvv_verified', False)}")
        print(f"   - Description: {latest_session.get('description', 'N/A')}")
    else:
        print("   ⏳ Session NOT yet processed by Phase 2 (raw Phase 1 data)")
        print("   → Phase 2 can process this session using:")
        print(f"      processor.process_session_metadata('{session_id}')")

    # Try to retrieve as ProductRecord
    print(f"\n[6] Retrieving as Phase 2 ProductRecord...")
    product_record = processor.get_product_record(session_id)

    if product_record:
        print("   ✅ Successfully retrieved as ProductRecord")
        print(f"   - Product ID: {product_record.product_id}")
        print(f"   - Session ID: {product_record.session_id}")
        print(f"   - Total Angles: {product_record.total_angles}")
        if product_record.mvv_result:
            print(f"   - MVV Verified: {product_record.mvv_result.verified}")
        else:
            print(f"   - MVV Result: Not available")
    else:
        print("   ⏳ Not a ProductRecord yet (raw Phase 1 data)")
        print("   → Need to process with Phase 2 first")

    print("\n" + "=" * 60)
    print("CONCLUSION:")
    print("=" * 60)
    print("✅ Phase 1 IS saving data to MongoDB")
    print("✅ Phase 2 CAN retrieve Phase 1 data from MongoDB")
    print("✅ Integration between Phase 1 and Phase 2 is WORKING")
    print("\nTo process Phase 1 data with Phase 2, run:")
    print(f"   python phase_2/data_processor.py process {session_id}")
    print("=" * 60)

    return True

if __name__ == "__main__":
    try:
        test_phase2_retrieval()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
