import AVFoundation
import CoreImage
import Vision
import simd

final class CameraSessionController: NSObject, ObservableObject {
    let session = AVCaptureSession()

    @Published private(set) var isSessionRunning = false

    private let sessionQueue = DispatchQueue(label: "camera.session.queue")
    private let fileManager = FileManager.default
    private let ciContext = CIContext()

    private var isConfigured = false
    private var latestDepthData: AVDepthData?
    private var pendingCapture: CheckedContinuation<CapturedPhoto, Error>?

    private let jointMapping: [String: VNHumanBodyPoseObservation.JointName] = [
        "left_shoulder": .leftShoulder,
        "right_shoulder": .rightShoulder,
        "left_hip": .leftHip,
        "right_hip": .rightHip,
        "neck": .neck,
        "left_elbow": .leftElbow,
        "right_elbow": .rightElbow,
        "left_wrist": .leftWrist,
        "right_wrist": .rightWrist,
        "left_hand": .leftWrist,
        "right_hand": .rightWrist,
        "left_knee": .leftKnee,
        "right_knee": .rightKnee,
        "left_ankle": .leftAnkle,
        "right_ankle": .rightAnkle,
        "left_foot": .leftAnkle,
        "right_foot": .rightAnkle,
        "left_toes": .leftAnkle,
        "right_toes": .rightAnkle
    ]

    func start() {
        sessionQueue.async { [weak self] in
            guard let self else { return }
            if !self.isConfigured {
                self.configureSession()
            }
            guard !self.session.isRunning else { return }
            self.session.startRunning()
            DispatchQueue.main.async {
                self.isSessionRunning = true
            }
        }
    }

    func stop() {
        sessionQueue.async { [weak self] in
            guard let self else { return }
            guard self.session.isRunning else { return }
            self.session.stopRunning()
            DispatchQueue.main.async {
                self.isSessionRunning = false
            }
        }
    }

    func reset() {
        stop()
        start()
    }

    func captureCurrentFrame() async throws -> CapturedPhoto {
        try await withCheckedThrowingContinuation { continuation in
            sessionQueue.async { [weak self] in
                guard let self else { return }
                if self.pendingCapture != nil {
                    continuation.resume(throwing: CaptureError.captureInProgress)
                    return
                }
                self.pendingCapture = continuation
            }
        }
    }

    private func configureSession() {
        guard let device = AVCaptureDevice.default(.builtInTrueDepthCamera, for: .video, position: .front) ??
                AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .front) else {
            return
        }

        session.beginConfiguration()
        session.sessionPreset = .high

        do {
            let input = try AVCaptureDeviceInput(device: device)
            if session.canAddInput(input) {
                session.addInput(input)
            }
        } catch {
            session.commitConfiguration()
            return
        }

        let videoOutput = AVCaptureVideoDataOutput()
        videoOutput.alwaysDiscardsLateVideoFrames = true
        videoOutput.videoSettings = [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA]
        videoOutput.setSampleBufferDelegate(self, queue: sessionQueue)
        if session.canAddOutput(videoOutput) {
            session.addOutput(videoOutput)
        }
        if let connection = videoOutput.connection(with: .video) {
            if #available(iOS 17.0, *) {
                connection.videoRotationAngle = 90
            } else {
                connection.videoOrientation = .portrait
            }
            if connection.isVideoMirroringSupported {
                connection.automaticallyAdjustsVideoMirroring = false
                connection.isVideoMirrored = true
            }
        }

        if supportsDepthData(device: device) {
            let depthOutput = AVCaptureDepthDataOutput()
            depthOutput.isFilteringEnabled = true
            depthOutput.setDelegate(self, callbackQueue: sessionQueue)
            if session.canAddOutput(depthOutput) {
                session.addOutput(depthOutput)
            }
            depthOutput.connection(with: .depthData)?.isEnabled = true
        }

        session.commitConfiguration()
        isConfigured = true
    }

    private func supportsDepthData(device: AVCaptureDevice) -> Bool {
        !device.activeFormat.supportedDepthDataFormats.isEmpty
    }

    private func processSampleBuffer(_ sampleBuffer: CMSampleBuffer) throws -> CapturedPhoto {
        guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else {
            throw CaptureError.missingFrame
        }

        let depthData = latestDepthData
        let joints = try detectSkeleton(in: pixelBuffer, depthData: depthData)
        guard !joints.isEmpty else {
            throw CaptureError.missingBody
        }

        let baseURL = try fileManager.createCaptureDirectory()
        let imageURL = baseURL.appendingPathComponent("capture.jpg")
        try writeImage(buffer: pixelBuffer, to: imageURL)

        var depthURL: URL?
        if let depthData {
            let depthMap = depthData.convertingToDepthFloat32().depthDataMap
            let url = baseURL.appendingPathComponent("depth.bin")
            try depthMap.serializedData().write(to: url)
            depthURL = url
        }

        let skeletonURL = baseURL.appendingPathComponent("skeleton.json")
        let skeletonData = try serializeSkeleton(joints)
        try skeletonData.write(to: skeletonURL)

        return CapturedPhoto(imageURL: imageURL, depthURL: depthURL, skeletonURL: skeletonURL)
    }

    private func detectSkeleton(in pixelBuffer: CVPixelBuffer, depthData: AVDepthData?) throws -> [String: SIMD3<Float>] {
        let request = VNDetectHumanBodyPoseRequest()
        let handler = VNImageRequestHandler(cvPixelBuffer: pixelBuffer, orientation: .upMirrored, options: [:])
        try handler.perform([request])
        guard let observation = request.results?.first,
              let points = try? observation.recognizedPoints(.all) else {
            return [:]
        }

        var joints: [String: SIMD3<Float>] = [:]

        for (name, jointName) in jointMapping {
            guard let point = points[jointName], point.confidence > 0.3 else { continue }
            joints[name] = project(point: point.location, using: depthData)
        }

        if joints["head"] == nil {
            if let nose = points[.nose], nose.confidence > 0.3 {
                joints["head"] = project(point: nose.location, using: depthData)
            }
        }

        if joints["head_top"] == nil {
            if let leftEar = points[.leftEar], let rightEar = points[.rightEar],
               leftEar.confidence > 0.3, rightEar.confidence > 0.3 {
                let mid = CGPoint(x: (leftEar.location.x + rightEar.location.x) / 2,
                                  y: (leftEar.location.y + rightEar.location.y) / 2)
                joints["head_top"] = project(point: mid, using: depthData)
            } else if let head = joints["head"] {
                joints["head_top"] = SIMD3(head.x, head.y + 0.1, head.z)
            }
        }

        if joints["spine_7"] == nil, let root = points[.root], root.confidence > 0.3 {
            joints["spine_7"] = project(point: root.location, using: depthData)
        }

        if joints["spine_3"] == nil,
           let neck = joints["neck"],
           let spine7 = joints["spine_7"] {
            let mid = (neck + spine7) / 2
            joints["spine_3"] = mid
            joints["spine_2"] = mid
            joints["spine_1"] = spine7
            joints["spine"] = spine7
        }

        return joints
    }

    private func project(point: CGPoint, using depthData: AVDepthData?) -> SIMD3<Float> {
        guard let depthData else {
            return SIMD3(Float(point.x), Float(point.y), 2.0)
        }

        let depthFloat = depthData.convertingToDepthFloat32()
        let depthMap = depthFloat.depthDataMap

        CVPixelBufferLockBaseAddress(depthMap, .readOnly)
        defer { CVPixelBufferUnlockBaseAddress(depthMap, .readOnly) }

        let width = CVPixelBufferGetWidth(depthMap)
        let height = CVPixelBufferGetHeight(depthMap)

        let clampedX = min(max(point.x, 0), 1)
        let clampedY = min(max(point.y, 0), 1)

        let pixelX = Int(CGFloat(width - 1) * clampedX)
        let pixelY = Int(CGFloat(height - 1) * (1 - clampedY))

        let pointer = unsafeBitCast(CVPixelBufferGetBaseAddress(depthMap), to: UnsafeMutablePointer<Float32>.self)
        let depth = pointer[pixelY * width + pixelX]

        guard let calibration = depthFloat.cameraCalibrationData else {
            return SIMD3(Float(clampedX), Float(clampedY), max(depth, 0.1))
        }

        let intrinsics = calibration.intrinsicMatrix
        let referenceSize = calibration.intrinsicMatrixReferenceDimensions

        let fx = intrinsics.columns.0.x
        let fy = intrinsics.columns.1.y
        let cx = intrinsics.columns.2.x
        let cy = intrinsics.columns.2.y

        let refWidth = Float(referenceSize.width)
        let refHeight = Float(referenceSize.height)

        let imageX = Float(clampedX) * refWidth
        let imageY = (1 - Float(clampedY)) * refHeight

        let z = max(depth, 0.1)
        let x = (imageX - cx) * z / fx
        let y = (imageY - cy) * z / fy

        return SIMD3(x, y, z)
    }

    private func writeImage(buffer: CVPixelBuffer, to url: URL) throws {
        let ciImage = CIImage(cvPixelBuffer: buffer)
        guard let colorSpace = CGColorSpace(name: CGColorSpace.sRGB),
              let data = ciContext.jpegRepresentation(of: ciImage, colorSpace: colorSpace, options: [:]) else {
            throw CaptureError.imageEncodingFailed
        }
        try data.write(to: url)
    }

    private func serializeSkeleton(_ skeleton: [String: SIMD3<Float>]) throws -> Data {
        var joints: [String: [Float]] = [:]
        for (name, vector) in skeleton {
            joints[name] = [vector.x, vector.y, vector.z]
        }
        let payload: [String: Any] = [
            "timestamp": Date().timeIntervalSince1970,
            "joints": joints
        ]
        return try JSONSerialization.data(withJSONObject: payload, options: .prettyPrinted)
    }
}

extension CameraSessionController {
    enum CaptureError: Error, LocalizedError {
        case missingFrame
        case missingBody
        case imageEncodingFailed
        case captureInProgress

        var errorDescription: String? {
            switch self {
            case .missingFrame:
                return "Unable to read the current camera frame."
            case .missingBody:
                return "FitTwin could not detect a full body. Please step fully into view."
            case .imageEncodingFailed:
                return "Failed to encode the captured image."
            case .captureInProgress:
                return "Please wait for the current capture to finish."
            }
        }
    }
}

extension CameraSessionController: AVCaptureVideoDataOutputSampleBufferDelegate, AVCaptureDepthDataOutputDelegate {
    func captureOutput(_ output: AVCaptureOutput,
                      didOutput sampleBuffer: CMSampleBuffer,
                      from connection: AVCaptureConnection) {
        if let continuation = pendingCapture {
            pendingCapture = nil
            do {
                let capture = try processSampleBuffer(sampleBuffer)
                continuation.resume(returning: capture)
            } catch {
                continuation.resume(throwing: error)
            }
        }
    }

    func depthDataOutput(_ output: AVCaptureDepthDataOutput,
                         didOutput depthData: AVDepthData,
                         timestamp: CMTime,
                         connection: AVCaptureConnection) {
        latestDepthData = depthData.convertingToDepthFloat32()
    }
}

private extension AVDepthData {
    func convertingToDepthFloat32() -> AVDepthData {
        if depthDataType == kCVPixelFormatType_DepthFloat32 {
            return self
        }
        return converting(toDepthDataType: kCVPixelFormatType_DepthFloat32)
    }
}

private extension CVPixelBuffer {
    func serializedData() -> Data {
        CVPixelBufferLockBaseAddress(self, .readOnly)
        defer { CVPixelBufferUnlockBaseAddress(self, .readOnly) }

        let width = CVPixelBufferGetWidth(self)
        let height = CVPixelBufferGetHeight(self)
        let count = width * height
        let pointer = unsafeBitCast(CVPixelBufferGetBaseAddress(self), to: UnsafeMutablePointer<Float32>.self)
        let buffer = UnsafeBufferPointer(start: pointer, count: count)
        var floats = Array(buffer)
        return Data(bytes: &floats, count: MemoryLayout<Float32>.size * count)
    }
}

private extension FileManager {
    func createCaptureDirectory() throws -> URL {
        let caches = try url(for: .cachesDirectory, in: .userDomainMask, appropriateFor: nil, create: true)
        let directory = caches.appendingPathComponent("captures/\(UUID().uuidString)", isDirectory: true)
        try createDirectory(at: directory, withIntermediateDirectories: true)
        return directory
    }
}

extension CameraSessionController: @unchecked Sendable {}
