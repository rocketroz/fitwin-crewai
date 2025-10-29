import AVFoundation
import Foundation

/// Evaluates whether the front-camera capture flow can run on the current device.
struct DeviceRequirementChecker {
    /// Returns `true` when the device and OS can drive the front-camera LiDAR experience.
    var isFrontCameraCaptureSupported: Bool {
        guard #available(iOS 17.0, *) else { return false }
        if AVCaptureDevice.default(.builtInTrueDepthCamera, for: .video, position: .front) != nil {
            return true
        }
        if AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .front) != nil {
            return true
        }
        return false
    }

    /// User-facing copy that explains the fallback plan for unsupported devices.
    var unsupportedMessage: String {
        if !isFrontCameraCaptureSupported {
            return "iOS 17.0 or newer with a front-facing TrueDepth camera is required for selfie capture. \(manualFallbackInstructions)"
        }
        return manualFallbackInstructions
    }

    /// Placeholder instructions for the future two-person capture flow.
    var manualFallbackInstructions: String {
        "Manual capture flow (two people required) coming soon. Ask a teammate to photograph the subject with the rear camera and upload both front and side photos."
    }
}
