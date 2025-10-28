import Foundation

@MainActor
final class CaptureFlowViewModel: ObservableObject {
    @Published private(set) var state: CaptureSessionState = .idle
    @Published var alertMessage: String?
    @Published private(set) var frontCapture: CapturedPhoto?
    @Published private(set) var sideCapture: CapturedPhoto?

    let sessionController = LiDARSessionController()

    private let permissionManager = CameraPermissionManager()
    private let measurementCalculator = LiDARMeasurementCalculator()
    private let apiClient = FitTwinAPI()
    private let frontCountdownStart = 10
    private let sideCountdownStart = 5
    private let sessionID = UUID().uuidString

    func startFlow() {
        Task {
            state = .requestingPermissions
            let status = await permissionManager.requestAccess()

            switch status {
            case .authorized:
                sessionController.start()
                state = .readyForFront
            case .denied, .restricted:
                let message = "Camera access is required to capture measurements. Update permissions in Settings."
                state = .error(message)
                alertMessage = message
            case .notDetermined:
                let message = "Camera permission not determined. Please try again."
                state = .error(message)
                alertMessage = message
            }
        }
    }

    func captureFrontPhoto() {
        startCountdown(forFront: true)
    }

    func captureSidePhoto() {
        startCountdown(forFront: false)
    }

    func acceptFrontCapture() {
        guard case .reviewFront(let photo) = state else { return }
        frontCapture = photo
        state = .readyForSide
    }

    func retakeFrontCapture() {
        state = .readyForFront
    }

    func acceptSideCapture() {
        guard case .reviewSide(let photo) = state else { return }
        sideCapture = photo
        state = .processing
        Task { await processMeasurements() }
    }

    func retakeSideCapture() {
        state = .readyForSide
    }

    private func processMeasurements() async {
        guard let frontCapture, let sideCapture,
              let skeletonData = frontCapture.loadSkeletonData() else {
            state = .error("Missing capture data. Please re-capture.")
            return
        }

        let calculation = measurementCalculator.calculate(frontSkeletonData: skeletonData, heightFallbackCM: nil)
        do {
            _ = try await apiClient.submitMeasurements(
                front: frontCapture,
                side: sideCapture,
                measurements: calculation.measurementsCM,
                sessionID: sessionID
            )
            state = .completed
        } catch {
            let message = error.localizedDescription.isEmpty ? "Failed to upload measurements." : error.localizedDescription
            state = .error(message)
            alertMessage = message
        }
    }

    func resetFlow() {
        state = .idle
        alertMessage = nil
        frontCapture = nil
        sideCapture = nil
        sessionController.reset()
    }

    private func startCountdown(forFront: Bool) {
        Task {
            let start = forFront ? frontCountdownStart : sideCountdownStart
            for remaining in stride(from: start, through: 1, by: -1) {
                state = forFront ? .countdownFront(remaining) : .countdownSide(remaining)
                try await Task.sleep(for: .seconds(1))
            }

            if forFront {
                await performFrontCapture()
            } else {
                await performSideCapture()
            }
        }
    }

    private func performFrontCapture() async {
        state = .capturingFront
        do {
            let capture = try sessionController.captureCurrentFrame()
            state = .reviewFront(capture)
        } catch {
            state = .error(error.localizedDescription)
            alertMessage = error.localizedDescription
        }
    }

    private func performSideCapture() async {
        state = .capturingSide
        do {
            let capture = try sessionController.captureCurrentFrame()
            state = .reviewSide(capture)
        } catch {
            state = .error(error.localizedDescription)
            alertMessage = error.localizedDescription
        }
    }
}
