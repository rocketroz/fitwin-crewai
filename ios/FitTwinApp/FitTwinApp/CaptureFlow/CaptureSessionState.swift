import Foundation

/// Represents the major checkpoints in the measurement capture journey.
enum CaptureSessionState: Equatable {
    case idle
    case requestingPermissions
    case readyForFront
    case capturingFront
    case readyForSide
    case capturingSide
    case processing
    case completed
    case error(String)

    var statusMessage: String {
        switch self {
        case .idle:
            return "Welcome to the FitTwin capture flow."
        case .requestingPermissions:
            return "Requesting camera access…"
        case .readyForFront:
            return "Align the subject for the front photo."
        case .capturingFront:
            return "Capturing front photo…"
        case .readyForSide:
            return "Turn 90° to capture the side profile."
        case .capturingSide:
            return "Capturing side photo…"
        case .processing:
            return "Uploading photos and calculating measurements…"
        case .completed:
            return "Capture complete. Measurements ready."
        case .error(let message):
            return message
        }
    }
}
