import Foundation

@MainActor
final class CaptureFlowViewModel: ObservableObject {
    @Published private(set) var state: CaptureSessionState = .idle
    @Published var alertMessage: String?

    private let permissionManager = CameraPermissionManager()

    func startFlow() {
        Task {
            state = .requestingPermissions
            let status = await permissionManager.requestAccess()

            switch status {
            case .authorized:
                state = .readyForFront
            case .denied, .restricted:
                let message = "Camera access is required to capture measurements. Update permissions in Settings."
                state = .error(message)
                alertMessage = message
            case .notDetermined:
                // Should not happen because requestAccess handles the prompt,
                // but we fallback to error to avoid hanging.
                let message = "Camera permission not determined. Please try again."
                state = .error(message)
                alertMessage = message
            }
        }
    }

    func captureFrontPhoto() {
        // Placeholder logic until camera pipeline is implemented.
        state = .capturingFront

        Task {
            try await Task.sleep(for: .seconds(1))
            state = .readyForSide
        }
    }

    func captureSidePhoto() {
        state = .capturingSide

        Task {
            try await Task.sleep(for: .seconds(1))
            state = .processing
            await processMeasurements()
        }
    }

    private func processMeasurements() async {
        // Simulated network call.
        do {
            try await Task.sleep(for: .seconds(1.5))
            state = .completed
        } catch {
            let message = "Failed to process measurements. Please retry."
            state = .error(message)
            alertMessage = message
        }
    }

    func resetFlow() {
        state = .idle
        alertMessage = nil
    }
}
