import XCTest
@testable import FitTwinApp

final class FitTwinAppTests: XCTestCase {
    func testIdleStatusMessageWelcomesUser() {
        let message = CaptureSessionState.idle.statusMessage
        XCTAssertTrue(message.contains("Welcome"), "Idle state should surface a welcome message")
    }
}
