import Foundation
import simd

/// Uses LiDAR skeleton data to estimate anthropometric measurements.
/// The heuristics are based on NASA / ANSUR II studies and can be tuned by
/// adjusting the calibration constants once empirical data is collected.
struct LiDARMeasurementCalculator {
    struct Calibration {
        let chestDepthRatio: Float
        let waistDepthRatio: Float
        let hipDepthRatio: Float
        let limbCircumferenceMultiplier: Float
        let calfCircumferenceMultiplier: Float
        let ankleCircumferenceMultiplier: Float
        let inseamMultiplier: Float
        let sleeveMultiplier: Float
        let heightBiasCM: Float

        static let `default` = Calibration(
            chestDepthRatio: 0.80,
            waistDepthRatio: 0.75,
            hipDepthRatio: 0.85,
            limbCircumferenceMultiplier: 3.35,
            calfCircumferenceMultiplier: 2.9,
            ankleCircumferenceMultiplier: 2.5,
            inseamMultiplier: 1.08,
            sleeveMultiplier: 1.05,
            heightBiasCM: 0.5
        )
    }

    struct Result {
        let measurementsCM: [String: Double]
        let confidence: Double
    }

    private let calibration: Calibration

    init(calibration: Calibration = .default) {
        self.calibration = calibration
    }

    func calculate(frontSkeletonData: Data, heightFallbackCM: Double?, depthData: Data? = nil) -> Result {
        guard let skeletonJSON = try? JSONSerialization.jsonObject(with: frontSkeletonData) as? [String: Any],
              let joints = skeletonJSON["joints"] as? [String: [Double]] else {
            return Result(measurementsCM: [:], confidence: 0.4)
        }

        func joint(named candidates: [String]) -> SIMD3<Float>? {
            for name in candidates {
                if let values = joints[name], values.count == 3 {
                    return SIMD3(Float(values[0]), Float(values[1]), Float(values[2]))
                }
            }
            return nil
        }

        func ellipseCircumference(a: Float, b: Float) -> Float {
            let h = pow(a - b, 2) / pow(a + b, 2)
            return Float.pi * (a + b) * (1 + 3 * h / (10 + sqrt(4 - 3 * h)))
        }

        var results: [String: Double] = [:]
        var confidenceAccumulator: Float = 0
        var confidenceSamples: Float = 0

        let leftShoulder = joint(named: ["left_shoulder", "left_shoulder_1"])
        let rightShoulder = joint(named: ["right_shoulder", "right_shoulder_1"])
        let leftHip = joint(named: ["left_hip", "left_hip_1"])
        let rightHip = joint(named: ["right_hip", "right_hip_1"])
        let neck = joint(named: ["neck_1", "neck"])
        let spineUpper = joint(named: ["spine_7", "spine_3"])
        let spineMid = joint(named: ["spine_3", "spine_2"])
        let spineLower = joint(named: ["spine_1", "spine"])
        let sternum = neck

        if let leftShoulder, let rightShoulder {
            let shoulderWidth = distance(leftShoulder, rightShoulder)
            results["shoulder_cm"] = Double(shoulderWidth * 100)
            confidenceAccumulator += 0.9
            confidenceSamples += 1
        }

        if let leftShoulder, let rightShoulder, let sternum, let spineUpper {
            let breadth = distance(leftShoulder, rightShoulder)
            let depth = max(distance(sternum, spineUpper), breadth * calibration.chestDepthRatio)
            let chest = ellipseCircumference(a: breadth / 2, b: depth / 2) * 100
            results["chest_cm"] = Double(chest)
            confidenceAccumulator += 0.85
            confidenceSamples += 1
        }

        if let leftHip, let rightHip, let spineMid, let spineLower {
            let breadth = distance(leftHip, rightHip)
            let depth = max(distance(spineLower, spineMid), breadth * calibration.waistDepthRatio)
            let waist = ellipseCircumference(a: breadth / 2, b: depth / 2) * 100
            results["waist_natural_cm"] = Double(waist)
            confidenceAccumulator += 0.8
            confidenceSamples += 1
        }

        if let leftHip, let rightHip {
            let breadth = distance(leftHip, rightHip)
            let depth = breadth * calibration.hipDepthRatio
            let hips = ellipseCircumference(a: breadth / 2, b: depth / 2) * 100
            results["hip_low_cm"] = Double(hips)
            confidenceAccumulator += 0.75
            confidenceSamples += 1
        }

        if let head = joint(named: ["head", "head_top"]),
           let leftFoot = joint(named: ["left_foot", "left_toes"]),
           let rightFoot = joint(named: ["right_foot", "right_toes"]) {
            let foot = (leftFoot + rightFoot) / 2
            let height = distance(head, foot) * 100 + calibration.heightBiasCM
            results["height_cm"] = Double(height)
            confidenceAccumulator += 0.9
            confidenceSamples += 1
        } else if let fallback = heightFallbackCM {
            results["height_cm"] = fallback
            confidenceAccumulator += 0.5
            confidenceSamples += 1
        }

        if let leftShoulder, let leftElbow = joint(named: ["left_elbow", "left_elbow_1"]) {
            let upperArm = distance(leftShoulder, leftElbow)
            results["bicep_cm"] = Double(upperArm * calibration.limbCircumferenceMultiplier * 100)
            confidenceAccumulator += 0.65
            confidenceSamples += 1
        }

        if let leftElbow = joint(named: ["left_elbow", "left_elbow_1"]),
           let leftWrist = joint(named: ["left_wrist", "left_hand"]) {
            let forearm = distance(leftElbow, leftWrist)
            results["forearm_cm"] = Double(forearm * (calibration.limbCircumferenceMultiplier - 0.4) * 100)
            if let leftShoulder {
                let sleeve = (distance(leftShoulder, leftElbow) + forearm) * calibration.sleeveMultiplier * 100
                results["sleeve_cm"] = Double(sleeve)
            }
        }

        if let leftHip, let leftKnee = joint(named: ["left_knee", "left_knee_1"]) {
            let thigh = distance(leftHip, leftKnee)
            results["thigh_cm"] = Double(thigh * calibration.limbCircumferenceMultiplier * 100)
        }

        if let leftKnee = joint(named: ["left_knee", "left_knee_1"]),
           let leftAnkle = joint(named: ["left_ankle", "left_ankle_1"]) {
            let lowerLeg = distance(leftKnee, leftAnkle)
            results["calf_cm"] = Double(lowerLeg * calibration.calfCircumferenceMultiplier * 100)
            results["ankle_cm"] = Double(lowerLeg * calibration.ankleCircumferenceMultiplier * 100)

            let hip = leftHip ?? joint(named: ["right_hip", "right_hip_1"])
            if let hip {
                let inseam = distance(hip, leftAnkle) * calibration.inseamMultiplier * 100
                results["inseam_cm"] = Double(inseam)
            }
        }

        if let leftHip, let leftKnee = joint(named: ["left_knee", "left_knee_1"]),
           let leftAnkle = joint(named: ["left_ankle", "left_ankle_1"]) {
            let outseam = (distance(leftHip, leftKnee) + distance(leftKnee, leftAnkle)) * 100
            results["outseam_cm"] = Double(outseam)
            let rise = distance(leftHip, leftKnee) * 0.35 * 100
            results["front_rise_cm"] = Double(rise)
            results["back_rise_cm"] = Double(rise * 1.2)
        }

        let defaults: [String: Double] = [
            "neck_cm": 37,
            "waist_natural_cm": 80,
            "hip_low_cm": 100,
            "bicep_cm": 30,
            "forearm_cm": 25,
            "thigh_cm": 55,
            "knee_cm": 38,
            "calf_cm": 35,
            "ankle_cm": 22,
            "front_rise_cm": 25,
            "back_rise_cm": 35,
            "inseam_cm": 76,
            "outseam_cm": 100,
            "sleeve_cm": 60
        ]

        for (key, value) in defaults where results[key] == nil {
            results[key] = value
        }

        let confidence = confidenceSamples > 0 ? Double(confidenceAccumulator / confidenceSamples) : 0.6
        return Result(measurementsCM: results, confidence: confidence)
    }
}
