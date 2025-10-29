# MediaPipe Landmark-to-Measurement Formulas

## Overview

This document describes the geometric formulas used to calculate anthropometric body measurements from MediaPipe Pose Landmarker v3.1 landmarks. The implementation is in `backend/app/core/validation.py` in the `calculate_measurements_from_landmarks()` function.

## MediaPipe Pose Landmarks

MediaPipe Pose Landmarker v3.1 detects 33 body landmarks (indices 0-32):

| Index | Body Part | Index | Body Part |
|-------|-----------|-------|-----------|
| 0 | Nose | 17 | Left pinky |
| 1 | Left eye (inner) | 18 | Right pinky |
| 2 | Left eye | 19 | Left index |
| 3 | Left eye (outer) | 20 | Right index |
| 4 | Right eye (inner) | 21 | Left thumb |
| 5 | Right eye | 22 | Right thumb |
| 6 | Right eye (outer) | 23 | Left hip |
| 7 | Left ear | 24 | Right hip |
| 8 | Right ear | 25 | Left knee |
| 9 | Mouth (left) | 26 | Right knee |
| 10 | Mouth (right) | 27 | Left ankle |
| 11 | Left shoulder | 28 | Right ankle |
| 12 | Right shoulder | 29 | Left heel |
| 13 | Left elbow | 30 | Right heel |
| 14 | Right elbow | 31 | Left foot index |
| 15 | Left wrist | 32 | Right foot index |
| 16 | Right wrist | | |

## Coordinate System

MediaPipe provides landmarks in two coordinate systems:

1. **Normalized Image Coordinates**: x, y, z values in range [0, 1]
   - x: horizontal position (0 = left, 1 = right)
   - y: vertical position (0 = top, 1 = bottom)
   - z: depth (relative to hips, negative = closer to camera)

2. **World Coordinates**: Real-world 3D coordinates in meters

Our implementation uses normalized coordinates and scales them to centimeters using a reference height.

## Scaling Strategy

Since MediaPipe landmarks are normalized, we need to scale them to real-world measurements:

1. Calculate height in pixels: distance from ankle to nose
2. Use reference height (170 cm) to establish pixels-per-cm ratio
3. Apply this ratio to all other measurements
4. **Future improvement**: Use user-provided height for better accuracy

## Measurement Formulas

### 1. Height

**Formula**: Distance from ankle to top of head (nose as proxy)

```python
ankle_y = (left_ankle['y'] + right_ankle['y']) / 2
head_y = nose['y']
height_pixels = abs(ankle_y - head_y)
height_cm = height_pixels / pixels_per_cm
```

**Landmarks used**: 0 (nose), 27 (left ankle), 28 (right ankle)

### 2. Shoulder Width

**Formula**: Euclidean distance between left and right shoulder landmarks

```python
shoulder_width_cm = distance(left_shoulder, right_shoulder) / pixels_per_cm
```

**Landmarks used**: 11 (left shoulder), 12 (right shoulder)

### 3. Chest Circumference

**Formula**: Ellipse circumference using width from front view and depth from side view

The chest is approximated as an ellipse. We use Ramanujan's approximation for ellipse circumference:

```
C ≈ π * (3(a+b) - sqrt((3a+b)(a+3b)))
```

Where:
- a = chest_width / 2 (from front view)
- b = chest_depth / 2 (from side view)

```python
chest_width_cm = shoulder_width_cm * 1.1  # Chest is ~10% wider than shoulders
chest_depth_cm = chest_depth_from_side * 1.2
a = chest_width_cm / 2
b = chest_depth_cm / 2
chest_cm = π * (3(a+b) - sqrt((3a+b)(a+3b)))
```

**Landmarks used**: 11, 12 (shoulders from both views)

### 4. Waist Circumference

**Formula**: Ellipse circumference at waist level (midpoint between shoulders and hips)

```python
waist_width_cm = hip_width * 0.9  # Waist is narrower than hips
waist_depth_cm = hip_depth_from_side * 0.85
a = waist_width_cm / 2
b = waist_depth_cm / 2
waist_cm = π * (3(a+b) - sqrt((3a+b)(a+3b)))
```

**Landmarks used**: 11, 12 (shoulders), 23, 24 (hips)

### 5. Hip Circumference

**Formula**: Ellipse circumference using hip landmarks

```python
hip_width_cm = distance(left_hip, right_hip) / pixels_per_cm
hip_depth_cm = depth_from_side_view / pixels_per_cm
a = hip_width_cm / 2
b = hip_depth_cm / 2
hip_cm = π * (3(a+b) - sqrt((3a+b)(a+3b)))
```

**Landmarks used**: 23 (left hip), 24 (right hip)

### 6. Inseam

**Formula**: Distance from ankle to hip (crotch level)

```python
inseam_cm = distance(left_ankle, left_hip) / pixels_per_cm
```

**Landmarks used**: 27 (left ankle), 23 (left hip)

### 7. Outseam

**Formula**: Vertical distance from ankle to waist level

```python
outseam_cm = abs(ankle_y - waist_y) / pixels_per_cm
```

**Landmarks used**: 27/28 (ankles), waist level calculated from shoulders and hips

### 8. Sleeve Length

**Formula**: Distance from shoulder to wrist

```python
sleeve_cm = distance(left_shoulder, left_wrist) / pixels_per_cm
```

**Landmarks used**: 11 (left shoulder), 15 (left wrist)

### 9. Bicep Circumference

**Formula**: Estimated from upper arm length (shoulder to elbow)

```python
bicep_length_cm = distance(left_shoulder, left_elbow) / pixels_per_cm
bicep_cm = bicep_length_cm * 0.3  # Circumference ≈ 30% of length
```

**Landmarks used**: 11 (left shoulder), 13 (left elbow)

**Note**: This is an approximation. Actual bicep circumference varies significantly by muscle mass.

### 10. Forearm Circumference

**Formula**: Estimated from forearm length (elbow to wrist)

```python
forearm_length_cm = distance(left_elbow, left_wrist) / pixels_per_cm
forearm_cm = forearm_length_cm * 0.25  # Circumference ≈ 25% of length
```

**Landmarks used**: 13 (left elbow), 15 (left wrist)

### 11. Thigh Circumference

**Formula**: Estimated from thigh length (hip to knee)

```python
thigh_length_cm = distance(left_hip, left_knee) / pixels_per_cm
thigh_cm = thigh_length_cm * 0.35  # Circumference ≈ 35% of length
```

**Landmarks used**: 23 (left hip), 25 (left knee)

### 12. Knee Circumference

**Formula**: Estimated as proportion of thigh circumference

```python
knee_cm = thigh_cm * 0.7  # Knee is ~70% of thigh
```

**Derived from**: Thigh measurement

### 13. Calf Circumference

**Formula**: Estimated from calf length (knee to ankle)

```python
calf_length_cm = distance(left_knee, left_ankle) / pixels_per_cm
calf_cm = calf_length_cm * 0.25  # Circumference ≈ 25% of length
```

**Landmarks used**: 25 (left knee), 27 (left ankle)

### 14. Ankle Circumference

**Formula**: Estimated as proportion of calf circumference

```python
ankle_cm = calf_cm * 0.65  # Ankle is ~65% of calf
```

**Derived from**: Calf measurement

### 15. Neck Circumference

**Formula**: Estimated from shoulder width

```python
neck_cm = shoulder_width_cm * 0.4  # Neck is ~40% of shoulder width
```

**Derived from**: Shoulder width

### 16. Underbust Circumference

**Formula**: Average of chest and waist, slightly reduced

```python
underbust_cm = (chest_cm + waist_cm) / 2 * 0.95
```

**Derived from**: Chest and waist measurements

### 17. Front Rise

**Formula**: Vertical distance from hip to waist (front view)

```python
front_rise_cm = abs(waist_y - hip_y) / pixels_per_cm
```

**Landmarks used**: Hip and waist levels

### 18. Back Rise

**Formula**: Front rise with adjustment for typical back rise length

```python
back_rise_cm = front_rise_cm * 1.2  # Back rise is typically 20% longer
```

**Derived from**: Front rise

## Accuracy Estimation

The `estimate_accuracy()` function evaluates measurement confidence based on:

1. **Average Visibility**: Mean visibility score across all landmarks
2. **Key Landmark Visibility**: Visibility of critical landmarks (shoulders, hips, knees, ankles)

**Accuracy Thresholds**:
- 95%: avg_visibility > 0.85 AND key_visibility > 0.9
- 90%: avg_visibility > 0.7 AND key_visibility > 0.75
- 85%: avg_visibility > 0.5 AND key_visibility > 0.6
- 80%: Otherwise

## Limitations and Future Improvements

### Current Limitations

1. **Fixed Reference Height**: Uses 170 cm as default scaling factor
2. **Circumference Approximations**: Limb circumferences estimated from length ratios
3. **No Pose Correction**: Assumes proper standing pose
4. **Single Body Type**: Ratios may not fit all body types equally

### Planned Improvements

1. **User Height Input**: Use actual user height for accurate scaling
2. **Calibration Data**: Train on real measurements to refine ratios
3. **Body Type Detection**: Adjust formulas based on detected body type
4. **Pose Quality Checks**: Validate pose before calculating measurements
5. **Multi-View Fusion**: Better combine front and side view data
6. **Machine Learning**: Train ML model on landmark-to-measurement mappings

## References

1. MediaPipe Pose Landmarker Documentation: https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker
2. "Predicting Human Body Measurements Using MediaPipe Pose Auto-Capture" (Zong et al., 2023)
3. Anthropometric Survey of US Army Personnel (ANSUR II)
4. Ramanujan's Ellipse Circumference Approximation

## Testing

To test the implementation:

1. Capture front and side photos with MediaPipe landmarks
2. Manually measure the subject with a tape measure
3. Compare calculated vs. actual measurements
4. Calculate percentage error for each dimension
5. Target: <5% error for core dimensions (height, chest, waist, hip, inseam)

## Usage Example

```python
from backend.app.core.validation import calculate_measurements_from_landmarks
from backend.app.schemas.measure_schema import MediaPipeLandmarks

# Assume front_landmarks and side_landmarks are MediaPipeLandmarks objects
measurements = calculate_measurements_from_landmarks(
    front_landmarks=front_landmarks,
    side_landmarks=side_landmarks
)

print(f"Height: {measurements['height_cm']:.1f} cm")
print(f"Chest: {measurements['chest_cm']:.1f} cm")
print(f"Waist: {measurements['waist_natural_cm']:.1f} cm")
print(f"Hip: {measurements['hip_low_cm']:.1f} cm")
print(f"Inseam: {measurements['inseam_cm']:.1f} cm")
```
