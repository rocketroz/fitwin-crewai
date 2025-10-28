import Foundation

/// Represents the major checkpoints in the measurement capture journey.
enum CaptureSessionState: Equatable {
    case idle
    case requestingPermissions
    case readyForFront
    case countdownFront(Int)
    case capturingFront
    case reviewFront(CapturedPhoto)
    case readyForSide
    case countdownSide(Int)
    case capturingSide
    case reviewSide(CapturedPhoto)
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
        case .countdownFront(let seconds):
            return "Front photo in \(seconds)… Hold still about 7 ft from the camera."
        case .reviewFront:
            return "Review the front capture."
        case .capturingFront:
            return "Capturing front photo…"
        case .readyForSide:
            return "Turn 90° to capture the side profile."
        case .countdownSide(let seconds):
            return "Side photo in \(seconds)… Keep the 7 ft distance."
        case .reviewSide:
            return "Review the side capture."
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
