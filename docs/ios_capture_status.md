# iOS Capture Flow Status (2025-10-29)

## What changed
- Replaced `LiDARSessionController` with `CameraSessionController` built on `AVCaptureSession`, Vision body pose, and depth data (when available).
- Added `CameraPreviewView` with mirrored selfie feed.
- Added `DeviceRequirementChecker` to require iOS 17+ and front camera support.
- Updated `CaptureFlowView` layout (smaller fonts, scrollable, nav bar hidden) and cards to use solid backgrounds so text remains visible.
- Switched `Info.plist` to use `FITWIN_ENV=dev` and `FITWIN_API_URL=https://fitwin-dev.ngrok-free.app`.
- Removed LiDAR-specific files from the project.

## Still open
- Phone captures front/side photos successfully but upload fails with “The Internet connection appears to be offline” when hitting the new URL. Needs ngrok tunnel (or other remote endpoint) running and reachable from the device.
- Text layout and scrolling should be re-verified once the nav bar behaviour is final; we hid the nav bar to reclaim vertical space.

## Next steps
1. Run `ngrok http 8000` (or equivalent) on your backend machine and update `FITWIN_API_URL` if the hostname changes.
2. Rebuild & deploy the app to the phone and confirm the capture upload succeeds.
3. If the device still reports connectivity errors, capture Xcode console logs and inspect the network call in `FitTwinAPI.submitMeasurements`.

