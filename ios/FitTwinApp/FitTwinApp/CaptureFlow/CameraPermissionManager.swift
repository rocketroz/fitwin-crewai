import AVFoundation
import Foundation

actor CameraPermissionManager {
    enum PermissionStatus {
        case authorized
        case denied
        case notDetermined
        case restricted
    }

    func currentStatus() -> PermissionStatus {
        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized:
            return .authorized
        case .denied:
            return .denied
        case .notDetermined:
            return .notDetermined
        case .restricted:
            return .restricted
        @unknown default:
            return .restricted
        }
    }

    func requestAccess() async -> PermissionStatus {
        let status = AVCaptureDevice.authorizationStatus(for: .video)
        switch status {
        case .authorized, .denied, .restricted:
            return currentStatus()
        case .notDetermined:
            let granted = await AVCaptureDevice.requestAccess(for: .video)
            return granted ? .authorized : .denied
        @unknown default:
            return .restricted
        }
    }
}
