#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Improved dental analysis pipeline with anatomically correct tooth detection.

This module implements the enhanced tooth detection and classification system
that accurately identifies primary molars and premolars based on their
anatomical positions and characteristics.
"""

import cv2
import numpy as np
import time
from typing import List, Dict, Tuple, Optional
from config_parameters import (
    CLASSIFICATION_CONFIG, 
    DETECTION_CONFIG, 
    PREPROCESSING_CONFIG,
    MEASUREMENT_CONFIG,
    classify_tooth_type, 
    validate_tooth_pairs
)

def preprocess_dental_image(image: np.ndarray) -> np.ndarray:
    """
    Enhanced preprocessing for dental radiographs.
    
    Args:
        image: Input dental radiograph
        
    Returns:
        Preprocessed image optimized for tooth detection
    """
    
    config = PREPROCESSING_CONFIG
    
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Apply CLAHE for enhanced contrast
    clahe_params = config["clahe"]
    clahe = cv2.createCLAHE(
        clipLimit=clahe_params["clip_limit"],
        tileGridSize=clahe_params["tile_grid_size"]
    )
    enhanced = clahe.apply(gray)
    
    # Histogram stretching
    hist_params = config["histogram"]
    p_low = np.percentile(enhanced, hist_params["percentile_low"])
    p_high = np.percentile(enhanced, hist_params["percentile_high"])
    
    # Stretch histogram
    stretched = np.clip((enhanced - p_low) * 255.0 / (p_high - p_low), 0, 255).astype(np.uint8)
    
    # Apply bilateral filtering for noise reduction while preserving edges
    filter_params = config["filtering"]
    filtered = cv2.bilateralFilter(
        stretched,
        filter_params["bilateral_d"],
        filter_params["bilateral_sigma_color"],
        filter_params["bilateral_sigma_space"]
    )
    
    # Optional sharpening
    if config["sharpening"]["enable"]:
        kernel = np.array(config["sharpening"]["kernel"], dtype=np.float32)
        sharpened = cv2.filter2D(filtered, -1, kernel)
        weight = config["sharpening"]["weight"]
        result = cv2.addWeighted(filtered, 1 - weight, sharpened, weight, 0)
    else:
        result = filtered
    
    return result

def detect_teeth_contours(image: np.ndarray) -> List[np.ndarray]:
    """
    Detect tooth contours using improved edge detection and filtering.
    
    Args:
        image: Preprocessed dental image
        
    Returns:
        List of tooth contours
    """
    
    config = DETECTION_CONFIG
    
    # Multi-scale edge detection for robustness
    edges_combined = np.zeros_like(image)
    
    sigma_values = config["edge_detection"]["sigma_values"]
    for sigma in sigma_values:
        # Gaussian blur with different sigma values
        blurred = cv2.GaussianBlur(image, (0, 0), sigma)
        
        # Canny edge detection
        edges = cv2.Canny(blurred, 50, 150)
        edges_combined = cv2.bitwise_or(edges_combined, edges)
    
    # Morphological operations to close gaps and fill holes
    morph_config = config["morphology"]
    
    # Closing operation to connect nearby edges
    closing_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, 
        (morph_config["closing_radius"] * 2 + 1, morph_config["closing_radius"] * 2 + 1)
    )
    closed = cv2.morphologyEx(edges_combined, cv2.MORPH_CLOSE, closing_kernel)
    
    # Dilation to strengthen edges
    dilation_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (morph_config["dilation_radius"] * 2 + 1, morph_config["dilation_radius"] * 2 + 1)
    )
    dilated = cv2.dilate(closed, dilation_kernel, iterations=1)
    
    # Find contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours based on size and shape
    filtered_contours = filter_tooth_contours(contours, image.shape)
    
    return filtered_contours

def filter_tooth_contours(contours: List[np.ndarray], image_shape: Tuple[int, int]) -> List[np.ndarray]:
    """
    Filter contours to keep only tooth-like shapes.
    
    Args:
        contours: List of detected contours
        image_shape: Shape of the input image
        
    Returns:
        Filtered list of tooth contours
    """
    
    config = DETECTION_CONFIG
    filter_config = config["contour_filtering"]
    arch_config = config["dental_arch"]
    
    filtered_contours = []
    
    # Define dental arch region
    height, width = image_shape
    arch_top = int(height * arch_config["arch_top_ratio"])
    arch_bottom = int(height * arch_config["arch_bottom_ratio"])
    arch_left = int(width * (1 - arch_config["arch_width_ratio"]) / 2)
    arch_right = int(width * (1 + arch_config["arch_width_ratio"]) / 2)
    
    for contour in contours:
        # Basic size filtering
        area = cv2.contourArea(contour)
        if not (filter_config["min_area"] <= area <= filter_config["max_area"]):
            continue
        
        # Shape filtering
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
        
        # Compactness (circularity measure)
        compactness = 4 * np.pi * area / (perimeter * perimeter)
        if compactness < 0.05:  # Too elongated
            continue
        
        # Solidity (ratio of contour area to its convex hull area)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        if hull_area > 0:
            solidity = area / hull_area
            if solidity < filter_config["min_solidity"]:
                continue
        
        # Aspect ratio filtering
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h
        if not (arch_config["aspect_ratio_min"] <= aspect_ratio <= arch_config["aspect_ratio_max"]):
            continue
        
        # Position filtering (must be in dental arch region)
        centroid_x = x + w // 2
        centroid_y = y + h // 2
        
        if not (arch_left <= centroid_x <= arch_right and arch_top <= centroid_y <= arch_bottom):
            continue
        
        filtered_contours.append(contour)
    
    return filtered_contours

def calculate_confidence(contour: np.ndarray, position: Tuple[int, int], image_shape: Tuple[int, int]) -> float:
    """
    Calculate confidence score for tooth detection.
    
    Args:
        contour: Tooth contour
        position: Centroid position
        image_shape: Shape of the input image
        
    Returns:
        Confidence score between 0 and 1
    """
    
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)
    
    confidence = 0.3  # Base confidence
    
    # Size confidence (optimal size range)
    if 300 <= area <= 20000:
        confidence += 0.3
    elif 150 <= area <= 30000:
        confidence += 0.2
    
    # Shape confidence (compactness)
    if perimeter > 0:
        compactness = 4 * np.pi * area / (perimeter * perimeter)
        if compactness > 0.15:
            confidence += 0.2
        elif compactness > 0.1:
            confidence += 0.1
    
    # Position confidence (in dental arch region)
    rel_y = position[1] / image_shape[0]
    if 0.25 < rel_y < 0.8:  # In typical dental arch region
        confidence += 0.2
    elif 0.2 < rel_y < 0.85:
        confidence += 0.1
    
    # Aspect ratio confidence
    x, y, w, h = cv2.boundingRect(contour)
    aspect_ratio = float(w) / h
    if 0.5 <= aspect_ratio <= 2.0:
        confidence += 0.1
    
    return min(confidence, 1.0)

def measure_tooth_width(contour: np.ndarray, calibration_factor: float = 0.1) -> Tuple[float, float]:
    """
    Measure tooth width using PCA-based method for accuracy.
    
    Args:
        contour: Tooth contour
        calibration_factor: Pixel to mm conversion factor
        
    Returns:
        Tuple of (width_mm, width_pixels)
    """
    
    # Get contour points
    points = contour.reshape(-1, 2).astype(np.float32)
    
    if len(points) < 5:  # Need at least 5 points for PCA
        # Fallback to bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
        width_pixels = min(w, h)  # Use smaller dimension as width
        width_mm = width_pixels * calibration_factor
        return width_mm, width_pixels
    
    # Calculate PCA
    mean = np.mean(points, axis=0)
    points_centered = points - mean
    cov_matrix = np.cov(points_centered.T)
    
    try:
        eigenvals, eigenvecs = np.linalg.eigh(cov_matrix)
        
        # Sort by eigenvalue (largest first)
        sort_indices = np.argsort(eigenvals)[::-1]
        eigenvals = eigenvals[sort_indices]
        eigenvecs = eigenvecs[:, sort_indices]
        
        # Project points onto principal axes
        projections = np.dot(points_centered, eigenvecs)
        
        # Calculate ranges along each axis
        range_major = np.max(projections[:, 0]) - np.min(projections[:, 0])
        range_minor = np.max(projections[:, 1]) - np.min(projections[:, 1])
        
        # Tooth width is typically the smaller dimension
        width_pixels = min(range_major, range_minor)
        
    except np.linalg.LinAlgError:
        # Fallback to bounding rectangle if PCA fails
        x, y, w, h = cv2.boundingRect(contour)
        width_pixels = min(w, h)
    
    # Convert to millimeters
    width_mm = width_pixels * calibration_factor
    
    return width_mm, width_pixels

def analyze_dental_radiograph(image_path: str, calibration_factor: Optional[float] = None) -> Dict:
    """
    Main function to analyze dental radiograph and detect tooth width differences.
    
    Args:
        image_path: Path to the dental radiograph
        calibration_factor: Optional pixel to mm conversion factor
        
    Returns:
        Analysis results dictionary
    """
    
    start_time = time.time()
    
    try:
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        # Preprocess image
        preprocessed = preprocess_dental_image(image)
        
        # Detect tooth contours
        contours = detect_teeth_contours(preprocessed)
        
        if len(contours) < 2:
            return {
                "error": "Insufficient teeth detected",
                "suggestions": [
                    "Ensure image shows clear dental structures",
                    "Check image quality and contrast",
                    "Verify panoramic radiograph includes posterior teeth"
                ],
                "processing_time_ms": int((time.time() - start_time) * 1000)
            }
        
        # Classify and detect teeth
        detected_teeth = []
        image_shape = preprocessed.shape
        
        for contour in contours:
            # Calculate centroid
            M = cv2.moments(contour)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                
                # Classify tooth type
                tooth_type = classify_tooth_type(contour, (cx, cy), image_shape, contours)
                
                if tooth_type in ['primary_molar', 'premolar']:
                    confidence = calculate_confidence(contour, (cx, cy), image_shape)
                    
                    detected_teeth.append({
                        'contour': contour,
                        'position': (cx, cy),
                        'type': tooth_type,
                        'area': cv2.contourArea(contour),
                        'confidence': confidence
                    })
        
        # Validate and pair teeth
        validated_pairs = validate_tooth_pairs(detected_teeth)
        
        if not validated_pairs:
            return {
                "error": "No valid tooth pairs detected",
                "detected_teeth_count": len(detected_teeth),
                "suggestions": [
                    "Image may not show clear primary molar and premolar pairs",
                    "Try adjusting image contrast or brightness",
                    "Ensure the radiograph includes the posterior dental region"
                ],
                "processing_time_ms": int((time.time() - start_time) * 1000)
            }
        
        # Use the best pair (highest confidence)
        best_pair = max(validated_pairs, key=lambda p: p['confidence'])
        
        primary_molar = best_pair['primary_molar']
        premolar = best_pair['premolar']
        
        # Determine calibration factor
        if calibration_factor is None:
            calibration_factor = MEASUREMENT_CONFIG["calibration"]["default_factor"]
        
        # Measure widths
        molar_width_mm, molar_width_pixels = measure_tooth_width(
            primary_molar['contour'], calibration_factor
        )
        premolar_width_mm, premolar_width_pixels = measure_tooth_width(
            premolar['contour'], calibration_factor
        )
        
        # Calculate difference
        width_difference = molar_width_mm - premolar_width_mm
        percentage_difference = (width_difference / premolar_width_mm) * 100 if premolar_width_mm > 0 else 0
        
        # Get bounding rectangles for visualization
        molar_rect = cv2.boundingRect(primary_molar['contour'])
        premolar_rect = cv2.boundingRect(premolar['contour'])
        
        # Generate clinical recommendations
        recommendations = generate_clinical_recommendations(width_difference, abs(percentage_difference))
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            "tooth_width_analysis": {
                "primary_second_molar": {
                    "width_mm": round(molar_width_mm, 2),
                    "confidence": round(primary_molar['confidence'], 2),
                    "coordinates": {
                        "x": int(molar_rect[0]),
                        "y": int(molar_rect[1]),
                        "width": int(molar_rect[2]),
                        "height": int(molar_rect[3])
                    }
                },
                "second_premolar": {
                    "width_mm": round(premolar_width_mm, 2),
                    "confidence": round(premolar['confidence'], 2),
                    "coordinates": {
                        "x": int(premolar_rect[0]),
                        "y": int(premolar_rect[1]),
                        "width": int(premolar_rect[2]),
                        "height": int(premolar_rect[3])
                    }
                },
                "width_difference": {
                    "value_mm": round(width_difference, 2),
                    "percentage": round(percentage_difference, 1),
                    "clinical_significance": classify_clinical_significance(width_difference)
                }
            },
            "image_quality": {
                "resolution": f"{image.shape[1]}x{image.shape[0]}",
                "detected_teeth_count": len(detected_teeth),
                "validated_pairs_count": len(validated_pairs),
                "best_pair_confidence": round(best_pair['confidence'], 2)
            },
            "clinical_recommendations": recommendations,
            "processing_time_ms": processing_time,
            "calibration_factor": calibration_factor,
            "anatomical_score": round(best_pair.get('anatomical_score', 0.0), 2)
        }
    
    except Exception as e:
        return {
            "error": f"Analysis failed: {str(e)}",
            "processing_time_ms": int((time.time() - start_time) * 1000)
        }

def generate_clinical_recommendations(width_difference: float, abs_percentage: float) -> List[str]:
    """
    Generate clinical recommendations based on width measurements.
    
    Args:
        width_difference: Width difference in mm
        abs_percentage: Absolute percentage difference
        
    Returns:
        List of clinical recommendations
    """
    
    recommendations = []
    
    if abs(width_difference) > 3.0:
        recommendations.extend([
            "Significant width discrepancy detected (>3mm)",
            "Space maintainer placement strongly recommended",
            "Immediate orthodontic consultation advised",
            "Monitor for potential crowding issues"
        ])
    elif abs(width_difference) > 2.0:
        recommendations.extend([
            "Moderate width discrepancy detected (2-3mm)",
            "Consider space maintainer placement",
            "Orthodontic consultation recommended",
            "Regular monitoring advised"
        ])
    elif abs(width_difference) > 1.0:
        recommendations.extend([
            "Minor width discrepancy detected (1-2mm)",
            "Monitor eruption pattern closely",
            "Consider preventive measures",
            "Regular follow-up recommended"
        ])
    else:
        recommendations.extend([
            "Normal width relationship detected",
            "Continue routine monitoring",
            "No immediate intervention required"
        ])
    
    # Additional recommendations based on percentage
    if abs_percentage > 30:
        recommendations.append("Percentage difference >30% indicates high risk")
    elif abs_percentage > 20:
        recommendations.append("Percentage difference >20% requires attention")
    
    return recommendations

def classify_clinical_significance(width_difference: float) -> str:
    """
    Classify the clinical significance of width difference.
    
    Args:
        width_difference: Width difference in mm
        
    Returns:
        Clinical significance classification
    """
    
    abs_diff = abs(width_difference)
    
    if abs_diff > 3.0:
        return "Highly Significant"
    elif abs_diff > 2.0:
        return "Significant"
    elif abs_diff > 1.0:
        return "Moderate"
    else:
        return "Normal"

# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python improved_analysis.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    print("Starting improved dental analysis...")
    results = analyze_dental_radiograph(image_path)
    
    print("\nAnalysis Results:")
    print("=" * 50)
    
    if "error" in results:
        print(f"Error: {results['error']}")
        if "suggestions" in results:
            print("\nSuggestions:")
            for suggestion in results["suggestions"]:
                print(f"- {suggestion}")
    else:
        analysis = results["tooth_width_analysis"]
        
        print(f"Primary Molar Width: {analysis['primary_second_molar']['width_mm']}mm "
              f"(confidence: {analysis['primary_second_molar']['confidence']})")
        
        print(f"Premolar Width: {analysis['second_premolar']['width_mm']}mm "
              f"(confidence: {analysis['second_premolar']['confidence']})")
        
        diff = analysis["width_difference"]
        print(f"Width Difference: {diff['value_mm']}mm ({diff['percentage']}%) "
              f"- {diff['clinical_significance']}")
        
        print(f"\nClinical Recommendations:")
        for rec in results["clinical_recommendations"]:
            print(f"- {rec}")
        
        print(f"\nProcessing time: {results['processing_time_ms']}ms")
        print(f"Anatomical score: {results['anatomical_score']}")
