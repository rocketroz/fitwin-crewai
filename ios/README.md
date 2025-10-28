# FitTwin iOS Scaffold

This directory contains the starter SwiftUI app that will evolve into the native FitTwin capture experience.

## Project Layout

```
ios/FitTwinApp/
├── FitTwinApp.xcodeproj/        # Xcode project configured for SwiftUI
├── FitTwinApp/                  # Swift sources and resources
│   ├── ContentView.swift        # Placeholder home screen
│   ├── FitTwinAppApp.swift      # App entry point
│   ├── Assets.xcassets/         # Asset catalogs (AppIcon placeholder)
│   ├── Resources/Info.plist     # Bundle metadata
│   └── Preview Content/         # SwiftUI preview assets
└── README.md                    # This file
```

## Getting Started

1. Open the project in Xcode:
   ```bash
   open ios/FitTwinApp/FitTwinApp.xcodeproj
   ```
2. Select the *FitTwinApp* scheme and choose an iOS simulator (iPhone 15 recommended).
3. Press `⌘R` to build and run. You should see the placeholder home screen with a disabled “Start Prototype Flow” button.

## Next Steps

- Replace `ContentView` with the real measurement capture flow.
- Add ARKit / MediaPipe integrations under `Sources/` as separate Swift files or feature folders.
- Update `Assets.xcassets/AppIcon.appiconset` with production artwork before shipping.
- Configure bundle identifiers, signing team, and TestFlight settings in Xcode’s *Signing & Capabilities* tab.

The scaffold uses iOS 16.0 as the deployment target, Swift 5, and SwiftUI’s `NavigationStack` to provide a modern baseline. Let me know when you’re ready to hook this up to the Supabase-backed API or integrate camera tooling.***
