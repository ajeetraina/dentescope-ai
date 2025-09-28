#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration parameters for dental width predictor.

This module contains adjustable parameters for different aspects of the
detection and measurement pipeline. Users can modify these parameters
to improve results for their specific dataset.
"""

import cv2
import numpy as np

# Detection Parameters
DETECTION_CONFIG = {
    # Edge detection parameters (adjust based on image contrast)
    "edge_detection": {
        "sigma_values": [1.5, 2.5],  # Lower values for sharper edges, higher for smoother
        "sigma_alternatives": [
            [1.0, 3.0],  # For high contrast images
            [2.0, 3.5],  # For low contrast images
            [0.8, 4.0]   # For very detailed images
        ]
    },
    
    # Contour filtering parameters
    "contour_filtering": {
        "min_area": 150,        # Reduced minimum area for better small tooth detection
        "max_area": 30000,      # Increased maximum area for larger teeth
        "min_eccentricity": 0.08,  # Reduced for more inclusive detection
        "min_solidity": 0.4,    # Reduced for better irregular tooth shapes
        
        # Alternative parameter sets for different image types
        "alternative_sets": [
            {"min_area": 100, "max_area": 35000, "min_eccentricity": 0.06, "min_solidity": 0.3},
            {"min_area": 200, "max_area": 25000, "min_eccentricity": 0.10, "min_solidity": 0.5},
            {"min_area": 175, "max_area": 28000, "min_eccentricity": 0.08, "min_solidity": 0.4}
        ]
    },
    
    # Morphological operations parameters
    "morphology": {
        "dilation_radius": 2,    # Radius for edge dilation
        "closing_radius": 3,     # Radius for morphological closing
        "hole_fill_threshold": 50  # Minimum area for hole filling
    },
    
    # Dental arch filtering parameters
    "dental_arch": {
        "arch_top_ratio": 0.25,      # Top of dental arch (height fraction)
        "arch_bottom_ratio": 0.75,   # Bottom of dental arch (height fraction)
        "arch_width_ratio": 0.75,    # Width of dental arch (width fraction)
        "aspect_ratio_min": 0.3,     # Reduced minimum aspect ratio
        "aspect_ratio_max": 3.0      # Reduced maximum aspect ratio
    }
}

# Classification Parameters - IMPROVED VERSION
CLASSIFICATION_CONFIG = {
    # Area-based classification thresholds (refined for better accuracy)
    "area_thresholds": {
        "large_tooth_multiplier": 1.3,    # Increased for primary molars (they're larger)
        "small_tooth_multiplier": 0.7,    # Decreased for premolars (they're smaller)
        "median_area_weight": 1.2          # Higher weight for median area calculation
    },
    
    # Shape-based classification (improved parameters)
    "shape_features": {
        "compactness_threshold": 0.15,     # Lowered for better molar detection
        "texture_contrast_threshold": 60,  # Adjusted for radiographic contrast
        "texture_homogeneity_threshold": 0.4, # Adjusted for tooth texture
        "intensity_threshold": 80,         # Lowered for radiographic images
        "aspect_ratio_min": 0.4,          # More inclusive range
        "aspect_ratio_max": 2.5           # More inclusive range
    },
    
    # Position-based classification (CRITICAL FIX)
    "position_weights": {
        # Fixed positioning logic for anatomically correct detection
        "posterior_region_start": 0.55,    # Posterior region starts at 55% from anterior
        "posterior_region_end": 0.9,       # Posterior region ends at 90% from anterior
        "middle_region_start": 0.35,       # Middle region for premolars
        "middle_region_end": 0.75,         # Middle region end (overlapping for mixed dentition)
        
        # Vertical positioning in mixed dentition
        "primary_molar_vertical_range": (0.25, 0.7),  # Upper portion of dental arch
        "premolar_vertical_range": (0.35, 0.8),       # Lower portion, overlapping
        
        # Distance thresholds for tooth pairing
        "horizontal_alignment_threshold": 80,  # Increased for more flexibility
        "vertical_separation_min": 15,         # Reduced minimum vertical separation
        "vertical_separation_max": 150,        # Maximum vertical separation
        
        # Priority scoring for classification
        "position_score_weight": 0.45,        # Increased position importance
        "size_score_weight": 0.35,           # Size importance  
        "shape_score_weight": 0.20           # Reduced shape importance
    },
    
    # Anatomical relationship constraints (NEW)
    "anatomical_constraints": {
        "primary_molar_posterior_bias": 0.75,  # Strong bias towards posterior region
        "premolar_beneath_molar": True,        # Premolars should be below molars
        "molar_premolar_proximity": 100,       # Maximum distance between paired teeth
        "enforce_size_relationship": True,     # Primary molars > premolars
        "size_difference_threshold": 0.1,     # Minimum 10% size difference
        "horizontal_overlap_max": 60,          # Maximum horizontal overlap
        "vertical_offset_preference": 20       # Preferred vertical offset
    }
}

# Measurement Parameters
MEASUREMENT_CONFIG = {
    # Contact point detection
    "contact_points": {
        "alignment_threshold": 80,         # Increased for better pairing
        "vertical_separation_penalty": 1.5, # Reduced penalty for mixed dentition
        "pca_fallback_threshold": 1.2,    # Aspect ratio threshold for PCA vs simple measurement
    },
    
    # Width measurement methods
    "measurement_methods": {
        "primary_method": "pca_based",     # Options: "pca_based", "convex_hull", "bounding_box"
        "fallback_method": "convex_hull",  # Fallback if primary method fails
        "approximation_factor": 1.1       # Reduced multiplier for more accurate measurements
    },
    
    # Calibration
    "calibration": {
        "default_factor": 0.1,            # Default mm/pixel ratio
        "auto_detect_dpi": True,          # Try to detect DPI from image metadata
        "common_dpi_values": [72, 96, 150, 300], # Common DPI values to try
        "pixel_size_estimates": {         # Rough estimates for different image sources
            "intraoral": 0.05,            # High resolution intraoral cameras
            "panoramic": 0.1,             # Standard panoramic radiographs
            "cbct": 0.2                   # CBCT slice images
        }
    }
}

# Preprocessing Parameters
PREPROCESSING_CONFIG = {
    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
    "clahe": {
        "clip_limit": 3.5,               # Increased contrast enhancement
        "tile_grid_size": (8, 8),        # Grid size for local enhancement
        
        # Adaptive CLAHE parameters based on image characteristics
        "adaptive_params": {
            "dark_image": {"clip_limit": 4.5, "tile_grid_size": (6, 6)},
            "bright_image": {"clip_limit": 2.5, "tile_grid_size": (10, 10)},
            "low_contrast": {"clip_limit": 5.5, "tile_grid_size": (8, 8)}
        }
    },
    
    # Filtering parameters
    "filtering": {
        "bilateral_d": 9,                # Bilateral filter neighborhood size
        "bilateral_sigma_color": 75,     # Color sigma for bilateral filter
        "bilateral_sigma_space": 75,     # Space sigma for bilateral filter
        "gaussian_kernel_size": (3, 3),  # Gaussian blur kernel size
        "gaussian_sigma": 0              # Gaussian blur sigma (0 = calculate from kernel)
    },
    
    # Histogram stretching
    "histogram": {
        "percentile_low": 1,             # Lower percentile for stretching
        "percentile_high": 99,           # Upper percentile for stretching
        "gamma_correction": 0.9          # Gamma value for correction
    },
    
    # Sharpening
    "sharpening": {
        "enable": True,                  # Enable sharpening
        "kernel": [[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]], # Sharpening kernel
        "weight": 0.8                    # Reduced weight for sharpening
    }
}

# Debug and Visualization Parameters
DEBUG_CONFIG = {
    # Output settings
    "save_intermediate": True,           # Save intermediate processing steps
    "save_failed_cases": True,          # Save results even for failed cases
    "verbose_logging": True,            # Enable detailed logging
    
    # Visualization settings
    "colors": {
        "primary_molar": (0, 255, 0),   # Green for primary molars
        "premolar": (0, 0, 255),        # Red for premolars
        "other": (255, 0, 0),           # Blue for other teeth
        "contour": (0, 255, 255),       # Yellow for contours
        "measurement": (255, 255, 0)    # Cyan for measurements
    },
    
    # Text settings
    "font": cv2.FONT_HERSHEY_SIMPLEX,
    "font_scale": 0.5,
    "font_thickness": 1,
    "text_color": (255, 255, 255)
}

# Batch Processing Parameters
BATCH_CONFIG = {
    # Processing limits
    "max_consecutive_failures": 10,     # Stop after this many consecutive failures
    "max_processing_time": 300,         # Maximum time per image (seconds)
    "chunk_size": 50,                   # Process images in chunks
    
    # Retry logic
    "retry_failed": True,               # Retry failed images with different parameters
    "retry_max_attempts": 3,            # Maximum retry attempts
    "retry_parameter_variations": [     # Different parameter sets for retries
        {"method": "traditional", "preprocessing": "enhanced"},
        {"method": "traditional", "preprocessing": "aggressive"},
        {"method": "traditional", "preprocessing": "gentle"}
    ],
    
    # Output settings
    "save_summary": True,               # Save CSV summary
    "save_detailed_log": True,          # Save detailed processing log
    "save_batch_report": True           # Save batch processing report
}

# Quality Control Parameters
QUALITY_CONFIG = {
    # Measurement validation
    "validation": {
        "min_width_mm": 2.0,            # Minimum reasonable tooth width (mm)
        "max_width_mm": 15.0,           # Maximum reasonable tooth width (mm)
        "max_width_difference": 8.0,    # Maximum reasonable width difference (mm)
        "min_pair_distance": 15,        # Reduced minimum distance between paired teeth
        "max_pair_distance": 250        # Increased maximum distance between paired teeth
    },
    
    # Outlier detection
    "outlier_detection": {
        "enable": True,                 # Enable outlier detection
        "std_threshold": 2.5,           # Increased threshold for outlier detection
        "min_samples": 3                # Minimum samples needed for outlier detection
    },
    
    # Quality scoring
    "quality_scoring": {
        "min_contours": 3,              # Reduced minimum contours for good quality
        "min_classifications": 2,       # Minimum classifications for good quality
        "min_measurements": 1           # Minimum measurements for good quality
    }
}

def classify_tooth_type(contour, position, image_shape, all_contours):
    """
    Improved tooth classification using anatomical constraints.
    
    Args:
        contour: Individual tooth contour
        position: (x, y) centroid position  
        image_shape: (height, width) of the image
        all_contours: List of all detected tooth contours
        
    Returns:
        str: 'primary_molar', 'premolar', or 'other'
    """
    
    # Calculate relative position in image
    rel_x = position[0] / image_shape[1]  # Horizontal position (0=left, 1=right)
    rel_y = position[1] / image_shape[0]  # Vertical position (0=top, 1=bottom)
    
    # Calculate contour properties
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)
    
    # Bounding rectangle for aspect ratio
    x, y, w, h = cv2.boundingRect(contour)
    aspect_ratio = float(w) / h
    
    # Calculate area percentile among all contours
    all_areas = [cv2.contourArea(c) for c in all_contours]
    if len(all_areas) > 1:
        area_percentile = (sorted(all_areas).index(area) + 1) / len(all_areas)
    else:
        area_percentile = 0.5
    
    # Classification scores
    scores = {
        'primary_molar': 0.0,
        'premolar': 0.0,
        'other': 0.0
    }
    
    config = CLASSIFICATION_CONFIG
    
    # Position-based scoring (IMPROVED)
    posterior_start = config["position_weights"]["posterior_region_start"]
    posterior_end = config["position_weights"]["posterior_region_end"]
    middle_start = config["position_weights"]["middle_region_start"]
    middle_end = config["position_weights"]["middle_region_end"]
    
    # Primary molar scoring (should be in posterior region)
    if posterior_start <= rel_x <= posterior_end:
        scores['primary_molar'] += 0.5  # Increased weight
        # Additional bonus for being more posterior
        if rel_x > 0.7:
            scores['primary_molar'] += 0.2
    
    # Premolar scoring (should be in middle region, beneath molars)
    if middle_start <= rel_x <= middle_end:
        scores['premolar'] += 0.4
        # Bonus for being in the central posterior region
        if 0.45 <= rel_x <= 0.65:
            scores['premolar'] += 0.2
    
    # Vertical position scoring
    molar_v_min, molar_v_max = config["position_weights"]["primary_molar_vertical_range"]
    premolar_v_min, premolar_v_max = config["position_weights"]["premolar_vertical_range"]
    
    if molar_v_min <= rel_y <= molar_v_max:
        scores['primary_molar'] += 0.2
    
    if premolar_v_min <= rel_y <= premolar_v_max:
        scores['premolar'] += 0.2
    
    # Size-based scoring (IMPROVED)
    if area_percentile > 0.65:  # Large tooth
        scores['primary_molar'] += 0.4
    elif area_percentile > 0.35:  # Medium tooth
        scores['premolar'] += 0.3
        scores['primary_molar'] += 0.1
    else:  # Small tooth
        scores['premolar'] += 0.2
    
    # Shape-based scoring
    if perimeter > 0:
        compactness = 4 * np.pi * area / (perimeter * perimeter)
        
        if compactness > config["shape_features"]["compactness_threshold"]:
            scores['primary_molar'] += 0.15
            scores['premolar'] += 0.1
    
    # Aspect ratio scoring
    if 0.6 <= aspect_ratio <= 1.6:  # More square-like (molars)
        scores['primary_molar'] += 0.15
    elif 0.8 <= aspect_ratio <= 2.2:  # Slightly elongated (premolars)
        scores['premolar'] += 0.15
    
    # Return classification with highest score
    max_score = max(scores.values())
    if max_score < 0.4:  # Increased confidence threshold
        return 'other'
    
    return max(scores, key=scores.get)

def validate_tooth_pairs(detected_teeth):
    """
    Validate detected tooth pairs based on anatomical relationships.
    
    Args:
        detected_teeth: List of detected teeth with classifications
        
    Returns:
        dict: Validated and corrected tooth classifications
    """
    
    primary_molars = [t for t in detected_teeth if t['type'] == 'primary_molar']
    premolars = [t for t in detected_teeth if t['type'] == 'premolar']
    
    validated_pairs = []
    config = CLASSIFICATION_CONFIG["anatomical_constraints"]
    
    for molar in primary_molars:
        # Find closest premolar that meets anatomical constraints
        best_premolar = None
        best_score = 0
        
        for premolar in premolars:
            # Calculate distance and relationship
            dx = molar['position'][0] - premolar['position'][0]
            dy = molar['position'][1] - premolar['position'][1]
            distance = np.sqrt(dx*dx + dy*dy)
            
            # Anatomical constraint scoring
            score = 0
            
            # Distance constraint
            if distance < config["molar_premolar_proximity"]:
                score += 0.3
            
            # Horizontal alignment (should be reasonably close horizontally)
            if abs(dx) < config["horizontal_overlap_max"]:
                score += 0.2
            
            # Vertical relationship (premolar should be below molar in mixed dentition)
            if 0 < dy < 80:  # Premolar below molar
                score += 0.3
            elif -20 < dy < 20:  # Similar level (also acceptable)
                score += 0.2
            
            # Size relationship (molar should be larger)
            if config["enforce_size_relationship"]:
                size_ratio = molar['area'] / premolar['area'] if premolar['area'] > 0 else 0
                if size_ratio > (1 + config["size_difference_threshold"]):
                    score += 0.2
            
            # Position relationship (molar should be more posterior)
            if molar['position'][0] > premolar['position'][0]:
                score += 0.1
            
            if score > best_score and score > 0.6:  # Minimum threshold
                best_score = score
                best_premolar = premolar
        
        if best_premolar:
            pair_confidence = min(
                molar.get('confidence', 0.8), 
                best_premolar.get('confidence', 0.8),
                best_score
            )
            
            validated_pairs.append({
                'primary_molar': molar,
                'premolar': best_premolar,
                'confidence': pair_confidence,
                'anatomical_score': best_score
            })
    
    return validated_pairs

def get_config(config_name):
    """Get a specific configuration dictionary.
    
    Args:
        config_name (str): Name of the configuration
        
    Returns:
        dict: Configuration parameters
    """
    configs = {
        "detection": DETECTION_CONFIG,
        "classification": CLASSIFICATION_CONFIG,
        "measurement": MEASUREMENT_CONFIG,
        "preprocessing": PREPROCESSING_CONFIG,
        "debug": DEBUG_CONFIG,
        "batch": BATCH_CONFIG,
        "quality": QUALITY_CONFIG
    }
    
    return configs.get(config_name, {})

def create_custom_config(image_type="panoramic", quality="standard"):
    """Create a custom configuration based on image type and quality requirements.
    
    Args:
        image_type (str): Type of image ("panoramic", "intraoral", "cbct")
        quality (str): Quality setting ("fast", "standard", "high_quality")
        
    Returns:
        dict: Custom configuration parameters
    """
    base_config = {
        "detection": DETECTION_CONFIG.copy(),
        "classification": CLASSIFICATION_CONFIG.copy(),
        "measurement": MEASUREMENT_CONFIG.copy(),
        "preprocessing": PREPROCESSING_CONFIG.copy()
    }
    
    # Adjust for image type
    if image_type == "panoramic":
        base_config["measurement"]["calibration"]["default_factor"] = 0.1
        base_config["detection"]["contour_filtering"]["min_area"] = 150
    elif image_type == "intraoral":
        base_config["measurement"]["calibration"]["default_factor"] = 0.05
        base_config["detection"]["contour_filtering"]["min_area"] = 300
    elif image_type == "cbct":
        base_config["measurement"]["calibration"]["default_factor"] = 0.2
        base_config["detection"]["contour_filtering"]["min_area"] = 100
    
    # Adjust for quality setting
    if quality == "fast":
        base_config["detection"]["edge_detection"]["sigma_values"] = [2.0, 3.0]
        base_config["preprocessing"]["clahe"]["clip_limit"] = 2.5
    elif quality == "high_quality":
        base_config["detection"]["edge_detection"]["sigma_values"] = [1.0, 1.5, 2.0, 2.5, 3.0]
        base_config["preprocessing"]["clahe"]["clip_limit"] = 4.0
    
    return base_config

def save_config_to_file(config, filepath):
    """Save configuration to a JSON file.
    
    Args:
        config (dict): Configuration to save
        filepath (str): Path to save the configuration
    """
    import json
    
    with open(filepath, 'w') as f:
        json.dump(config, f, indent=2, default=str)

def load_config_from_file(filepath):
    """Load configuration from a JSON file.
    
    Args:
        filepath (str): Path to the configuration file
        
    Returns:
        dict: Loaded configuration
    """
    import json
    
    with open(filepath, 'r') as f:
        return json.load(f)

# Example usage and configuration templates
if __name__ == "__main__":
    print("Dental Width Predictor Configuration Parameters - UPDATED")
    print("=" * 60)
    
    # Show available configurations
    configs = ["detection", "classification", "measurement", "preprocessing", "debug", "batch", "quality"]
    
    for config_name in configs:
        config = get_config(config_name)
        print(f"\n{config_name.upper()} PARAMETERS:")
        print(f"  Available parameters: {len(config)}")
        
        # Show key improvements
        if config_name == "classification":
            print(f"  - Posterior region: {config['position_weights']['posterior_region_start']}-{config['position_weights']['posterior_region_end']}")
            print(f"  - Anatomical constraints: {len(config['anatomical_constraints'])} rules")
        elif config_name == "detection":
            print(f"  - Min area: {config['contour_filtering']['min_area']}")
            print(f"  - Max area: {config['contour_filtering']['max_area']}")
    
    print(f"\nKey improvements in this version:")
    print("- Enhanced anatomical positioning constraints")
    print("- Improved size-based classification")
    print("- Better vertical relationship detection")
    print("- More robust tooth pairing validation")
