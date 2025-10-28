import ARKit
import RealityKit
import SwiftUI

struct LiDARPreviewView: UIViewRepresentable {
    @ObservedObject var controller: LiDARSessionController

    func makeUIView(context: Context) -> ARView {
        let arView = ARView(frame: .zero)
        arView.session = controller.session
        arView.automaticallyConfigureSession = false
        arView.renderOptions.insert(.disablePersonOcclusion)
        return arView
    }

    func updateUIView(_ uiView: ARView, context: Context) {
        // Session updates handled by LiDARSessionController.
    }
}
