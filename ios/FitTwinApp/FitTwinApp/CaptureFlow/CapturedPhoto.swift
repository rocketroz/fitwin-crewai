import Foundation
import SwiftUI
import UIKit

struct CapturedPhoto: Identifiable, Equatable {
    let id = UUID()
    let imageURL: URL
    let depthURL: URL?
    let skeletonURL: URL?

    var uiImage: UIImage? {
        guard let data = try? Data(contentsOf: imageURL) else { return nil }
        return UIImage(data: data)
    }

    func base64EncodedImage() -> String? {
        guard let data = try? Data(contentsOf: imageURL) else { return nil }
        return data.base64EncodedString()
    }

    func loadSkeletonData() -> Data? {
        guard let skeletonURL else { return nil }
        return try? Data(contentsOf: skeletonURL)
    }

    func loadDepthData() -> Data? {
        guard let depthURL else { return nil }
        return try? Data(contentsOf: depthURL)
    }
}
