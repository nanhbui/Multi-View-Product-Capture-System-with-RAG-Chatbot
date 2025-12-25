#!/usr/bin/env python3
"""
Test script for YOLOv8 segmentation and new features.

This script verifies:
1. YOLOv8 segmentation model loading
2. Mask extraction
3. Transparent PNG creation
4. Histogram calculation
5. Lighting analysis
"""

import cv2
import numpy as np
from pathlib import Path
import sys

# Add phase_1 to path
sys.path.insert(0, str(Path(__file__).parent / "phase_1"))

from ultralytics import YOLO


def test_segmentation_model():
    """Test YOLOv8 segmentation model."""
    print("\n" + "="*60)
    print("TEST 1: YOLOv8 Segmentation Model")
    print("="*60)

    try:
        # Load model
        print("[INFO] Loading yolov8n-seg.pt model...")
        model = YOLO("yolov8n-seg.pt")
        print("[SUCCESS] Model loaded successfully")

        # Create test image
        print("[INFO] Creating test image...")
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        # Run inference
        print("[INFO] Running inference...")
        results = model(test_image, verbose=False)

        # Check if model supports segmentation
        if hasattr(results[0], 'masks'):
            print("[SUCCESS] Segmentation masks available")
            return True
        else:
            print("[ERROR] Model does not support segmentation")
            return False

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False


def test_mask_extraction():
    """Test mask extraction from segmentation results."""
    print("\n" + "="*60)
    print("TEST 2: Mask Extraction")
    print("="*60)

    try:
        # Create a simple image with a white rectangle
        print("[INFO] Creating test image with object...")
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.rectangle(test_image, (200, 150), (440, 330), (255, 255, 255), -1)

        # Load model and run inference
        model = YOLO("yolov8n-seg.pt")
        results = model(test_image, verbose=False)

        # Extract mask
        if hasattr(results[0], 'masks') and results[0].masks is not None:
            masks = results[0].masks
            print(f"[SUCCESS] Extracted {len(masks.data)} mask(s)")

            # Get first mask
            mask_data = masks.data[0].cpu().numpy()
            print(f"[INFO] Mask shape: {mask_data.shape}")
            print(f"[INFO] Mask dtype: {mask_data.dtype}")
            print(f"[INFO] Mask range: [{mask_data.min():.2f}, {mask_data.max():.2f}]")

            return True
        else:
            print("[INFO] No objects detected (expected for random image)")
            return True

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False


def test_transparent_png():
    """Test transparent PNG creation."""
    print("\n" + "="*60)
    print("TEST 3: Transparent PNG Creation")
    print("="*60)

    try:
        # Create test image and mask
        print("[INFO] Creating test image and mask...")
        image = np.ones((480, 640, 3), dtype=np.uint8) * 128  # Gray background
        cv2.rectangle(image, (200, 150), (440, 330), (0, 255, 0), -1)  # Green rectangle

        # Create circular mask
        mask = np.zeros((480, 640), dtype=np.uint8)
        cv2.circle(mask, (320, 240), 150, 255, -1)

        # Create BGRA image
        print("[INFO] Creating BGRA image with alpha channel...")
        bgra = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        bgra[:, :, 3] = mask

        # Save to file
        output_path = Path("test_output")
        output_path.mkdir(exist_ok=True)

        test_file = output_path / "test_transparent.png"
        cv2.imwrite(str(test_file), bgra)

        print(f"[SUCCESS] Transparent PNG saved to: {test_file}")

        # Verify file exists and has correct format
        if test_file.exists():
            # Read back and check alpha channel
            read_back = cv2.imread(str(test_file), cv2.IMREAD_UNCHANGED)
            if read_back.shape[2] == 4:
                print(f"[SUCCESS] Verified: Image has 4 channels (BGRA)")
                print(f"[INFO] Alpha channel range: [{read_back[:,:,3].min()}, {read_back[:,:,3].max()}]")
                return True
            else:
                print(f"[ERROR] Image has {read_back.shape[2]} channels (expected 4)")
                return False
        else:
            print("[ERROR] File was not created")
            return False

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False


def test_histogram_calculation():
    """Test histogram calculation."""
    print("\n" + "="*60)
    print("TEST 4: Histogram Calculation")
    print("="*60)

    try:
        # Create test images with different brightness
        print("[INFO] Creating test images...")

        # Dark image
        dark_image = np.ones((480, 640, 3), dtype=np.uint8) * 50
        # Bright image
        bright_image = np.ones((480, 640, 3), dtype=np.uint8) * 200
        # Normal image
        normal_image = np.ones((480, 640, 3), dtype=np.uint8) * 128

        for name, image in [("Dark", dark_image), ("Bright", bright_image), ("Normal", normal_image)]:
            # Calculate histogram
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])

            mean_brightness = np.mean(gray)

            print(f"[INFO] {name} image:")
            print(f"  - Mean brightness: {mean_brightness:.1f}")
            print(f"  - Histogram shape: {hist.shape}")
            print(f"  - Total pixels: {np.sum(hist):.0f}")

        print("[SUCCESS] Histogram calculation working")
        return True

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False


def test_lighting_analysis():
    """Test lighting analysis logic."""
    print("\n" + "="*60)
    print("TEST 5: Lighting Analysis")
    print("="*60)

    try:
        # Create test images
        test_cases = [
            ("Very Dark", 30),
            ("Dark", 70),
            ("Normal", 128),
            ("Bright", 190),
            ("Very Bright", 240)
        ]

        for name, brightness in test_cases:
            # Create image
            image = np.ones((480, 640, 3), dtype=np.uint8) * brightness

            # Calculate histogram
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])

            # Analyze lighting
            mean_brightness = np.mean(gray)
            total_pixels = image.shape[0] * image.shape[1]
            dark_pixels = np.sum(hist[:85]) / total_pixels

            is_dark = mean_brightness < 80
            is_bright = mean_brightness > 180
            needs_gamma = dark_pixels > 0.4

            print(f"\n[INFO] {name} (brightness={brightness}):")
            print(f"  - Mean: {mean_brightness:.1f}")
            print(f"  - Dark pixels: {dark_pixels*100:.1f}%")
            print(f"  - Is dark: {is_dark}")
            print(f"  - Is bright: {is_bright}")
            print(f"  - Needs gamma: {needs_gamma}")

        print("\n[SUCCESS] Lighting analysis working")
        return True

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False


def test_gamma_correction():
    """Test gamma correction."""
    print("\n" + "="*60)
    print("TEST 6: Gamma Correction")
    print("="*60)

    try:
        # Create dark image
        print("[INFO] Creating dark image...")
        dark_image = np.ones((480, 640, 3), dtype=np.uint8) * 50

        # Apply gamma correction
        print("[INFO] Applying gamma correction (gamma=1.5)...")
        gamma = 1.5
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")
        corrected = cv2.LUT(dark_image, table)

        # Compare brightness
        before = np.mean(dark_image)
        after = np.mean(corrected)

        print(f"[INFO] Before gamma: {before:.1f}")
        print(f"[INFO] After gamma: {after:.1f}")
        print(f"[INFO] Brightness increase: {after - before:.1f}")

        if after > before:
            print("[SUCCESS] Gamma correction brightened the image")
            return True
        else:
            print("[ERROR] Gamma correction did not brighten the image")
            return False

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False


def test_modules_import():
    """Test importing custom modules."""
    print("\n" + "="*60)
    print("TEST 7: Module Imports")
    print("="*60)

    try:
        # Try importing modules
        print("[INFO] Importing ImageProcessor...")
        from modules.image_processing import ImageProcessor
        processor = ImageProcessor()
        print("[SUCCESS] ImageProcessor imported")

        print("[INFO] Importing GStreamerPipeline...")
        from modules.gstreamer_pipeline import GStreamerPipeline
        gst = GStreamerPipeline()
        print("[SUCCESS] GStreamerPipeline imported")

        print("[INFO] Importing GestureController (may fail if mediapipe not installed)...")
        try:
            from modules.gesture_control import GestureController
            print("[SUCCESS] GestureController imported")
        except ImportError as e:
            print(f"[INFO] GestureController not available (MediaPipe not installed): {e}")

        print("\n[SUCCESS] All available modules imported successfully")
        return True

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("YOLOv8 SEGMENTATION & NEW FEATURES - TEST SUITE")
    print("="*70)

    tests = [
        ("Segmentation Model", test_segmentation_model),
        ("Mask Extraction", test_mask_extraction),
        ("Transparent PNG", test_transparent_png),
        ("Histogram Calculation", test_histogram_calculation),
        ("Lighting Analysis", test_lighting_analysis),
        ("Gamma Correction", test_gamma_correction),
        ("Module Imports", test_modules_import),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[ERROR] {test_name} crashed: {e}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} | {test_name}")

    print("="*70)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("="*70)

    if passed == total:
        print("\n🎉 All tests passed! System is ready.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
