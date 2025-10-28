import ARKit
import RealityKit

@MainActor
final class LiDARSessionController: NSObject, ObservableObject, ARSessionDelegate {
    let session = ARSession()

    @Published private(set) var isSessionRunning = false
    @Published private(set) var latestBodyAnchor: ARBodyAnchor?

    private let fileManager = FileManager.default

    override init() {
        super.init()
        session.delegate = self
    }

    func start() {
        guard ARBodyTrackingConfiguration.isSupported else {
            let configuration = ARWorldTrackingConfiguration()
            configuration.frameSemantics = [.sceneDepth, .bodyDetection]
            session.run(configuration, options: [.resetTracking, .removeExistingAnchors])
            isSessionRunning = true
            return
        }

        let configuration = ARBodyTrackingConfiguration()
        configuration.isAutoFocusEnabled = true
        configuration.frameSemantics = [.sceneDepth, .smoothedSceneDepth]
        session.run(configuration, options: [.resetTracking, .removeExistingAnchors])
        isSessionRunning = true
    }

    func stop() {
        session.pause()
        isSessionRunning = false
    }

    func reset() {
        stop()
        start()
    }

    func session(_ session: ARSession, didUpdate frame: ARFrame) {
        if let bodyAnchor = frame.anchors.compactMap({ $0 as? ARBodyAnchor }).first {
            latestBodyAnchor = bodyAnchor
        }
    }

    func session(_ session: ARSession, didAdd anchors: [ARAnchor]) {
        if let bodyAnchor = anchors.compactMap({ $0 as? ARBodyAnchor }).first {
            latestBodyAnchor = bodyAnchor
        }
    }

    func session(_ session: ARSession, didUpdate anchors: [ARAnchor]) {
        if let bodyAnchor = anchors.compactMap({ $0 as? ARBodyAnchor }).first {
            latestBodyAnchor = bodyAnchor
        }
    }

    func captureCurrentFrame() throws -> CapturedPhoto {
        guard let frame = session.currentFrame else {
            throw CaptureError.missingFrame
        }

        guard let bodyAnchor = frame.anchors.compactMap({ $0 as? ARBodyAnchor }).first ?? latestBodyAnchor else {
            throw CaptureError.missingBodyAnchor
        }

        let baseURL = try fileManager.createCaptureDirectory()

        // Save image
        let imageURL = baseURL.appendingPathComponent("capture.jpg")
        let ciImage = CIImage(cvPixelBuffer: frame.capturedImage)
        let context = CIContext(options: nil)
        guard let colorSpace = CGColorSpace(name: CGColorSpace.sRGB),
              let data = context.jpegRepresentation(of: ciImage, colorSpace: colorSpace) else {
            throw CaptureError.imageEncodingFailed
        }
        try data.write(to: imageURL)

        // Save depth data if available
        var depthURL: URL?
        if let depthMap = frame.sceneDepth?.depthMap {
            let depthData = depthMap.serializedData()
            let url = baseURL.appendingPathComponent("depth.bin")
            try depthData.write(to: url)
            depthURL = url
        }

        // Save skeleton transforms
        let skeletonURL = baseURL.appendingPathComponent("skeleton.json")
        let skeletonData = try bodyAnchor.serializedSkeleton()
        try skeletonData.write(to: skeletonURL)

        return CapturedPhoto(imageURL: imageURL, depthURL: depthURL, skeletonURL: skeletonURL)
    }
}

extension LiDARSessionController {
    enum CaptureError: Error, LocalizedError {
        case missingFrame
        case missingBodyAnchor
        case imageEncodingFailed

        var errorDescription: String? {
            switch self {
            case .missingFrame:
                return "Unable to read the current camera frame."
            case .missingBodyAnchor:
                return "Could not detect a full body. Please ensure the subject is in view."
            case .imageEncodingFailed:
                return "Failed to encode the captured image."
            }
        }
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

private extension ARBodyAnchor {
    func serializedSkeleton() throws -> Data {
        let jointNames = ARSkeletonDefinition.defaultBody3D.jointNames
        var joints: [String: [Float]] = [:]
        for (index, name) in jointNames.enumerated() {
            let transform = skeleton.modelTransform(for: ARSkeleton.JointName(rawValue: name))
            let column = transform.columns.3
            joints[name] = [column.x, column.y, column.z]
        }
        let payload: [String: Any] = [
            "timestamp": Date().timeIntervalSince1970,
            "joints": joints
        ]
        return try JSONSerialization.data(withJSONObject: payload, options: .prettyPrinted)
    }
}
