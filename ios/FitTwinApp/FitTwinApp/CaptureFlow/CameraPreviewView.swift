import AVFoundation
import SwiftUI

struct CameraPreviewView: UIViewRepresentable {
    @ObservedObject var controller: CameraSessionController

    func makeUIView(context: Context) -> PreviewView {
        let view = PreviewView()
        let layer = view.videoPreviewLayer
        layer.session = controller.session
        layer.videoGravity = .resizeAspectFill
        if #available(iOS 17.0, *) {
            layer.connection?.videoRotationAngle = 90
        } else {
            layer.connection?.videoOrientation = .portrait
        }
        if let connection = layer.connection, connection.isVideoMirroringSupported {
            connection.automaticallyAdjustsVideoMirroring = false
            connection.isVideoMirrored = true
        }
        layer.connection?.isVideoMirrored = true
        return view
    }

    func updateUIView(_ uiView: PreviewView, context: Context) {
        if uiView.videoPreviewLayer.session !== controller.session {
            uiView.videoPreviewLayer.session = controller.session
        }
    }
}

final class PreviewView: UIView {
    override class var layerClass: AnyClass { AVCaptureVideoPreviewLayer.self }

    var videoPreviewLayer: AVCaptureVideoPreviewLayer {
        guard let layer = self.layer as? AVCaptureVideoPreviewLayer else {
            fatalError("Unexpected layer type")
        }
        return layer
    }
}
