import Foundation

struct FitTwinAPI {
    enum APIError: Error {
        case invalidURL
        case requestFailed
        case decodingFailed
    }

    let baseURL: URL
    let apiKey: String

    init() {
        let bundle = Bundle.main
        let baseURLString = bundle.object(forInfoDictionaryKey: "FITWIN_API_URL") as? String ?? "http://127.0.0.1:8000"
        guard let url = URL(string: baseURLString) else {
            fatalError("Invalid FITWIN_API_URL in Info.plist")
        }
        baseURL = url
        apiKey = bundle.object(forInfoDictionaryKey: "FITWIN_API_KEY") as? String ?? "staging-secret-key"
    }

    func submitMeasurements(
        front: CapturedPhoto,
        side: CapturedPhoto,
        measurements: [String: Double],
        sessionID: String
    ) async throws -> [String: Any] {
        let url = baseURL.appendingPathComponent("/measurements/validate")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.addValue(apiKey, forHTTPHeaderField: "X-API-Key")

        var payload: [String: Any] = measurements
        payload["session_id"] = sessionID
        payload["source_type"] = "lidar_ios"
        payload["platform"] = "ios"
        payload["source"] = "lidar"
        payload["model_version"] = "lidar-v1"
        payload["confidence"] = 0.8
        if let encodedFront = front.base64EncodedImage() {
            payload["front_photo_data"] = encodedFront
        }
        if let encodedSide = side.base64EncodedImage() {
            payload["side_photo_data"] = encodedSide
        }

        request.httpBody = try JSONSerialization.data(withJSONObject: payload, options: [])

        let (data, response) = try await URLSession.shared.data(for: request)
        guard let httpResponse = response as? HTTPURLResponse,
              200..<300 ~= httpResponse.statusCode else {
            throw APIError.requestFailed
        }

        guard let json = try JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            throw APIError.decodingFailed
        }
        return json
    }
}
