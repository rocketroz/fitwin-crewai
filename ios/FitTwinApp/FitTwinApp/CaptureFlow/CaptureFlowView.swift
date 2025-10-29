import SwiftUI

struct CaptureFlowView: View {
    @StateObject private var viewModel = CaptureFlowViewModel()

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                Spacer(minLength: 12)

                if showsPreview {
                    CameraPreviewView(controller: viewModel.sessionController)
                        .frame(height: 320)
                        .cornerRadius(20)
                        .overlay(RoundedRectangle(cornerRadius: 20).stroke(style: StrokeStyle(lineWidth: 1, dash: [6])))
                }

                Text(viewModel.state.statusMessage)
                    .font(.system(size: 12, weight: .semibold))
                    .multilineTextAlignment(.center)
                    .minimumScaleFactor(0.7)
                    .padding(.horizontal, 12)

                Group {
                    switch viewModel.state {
                    case .idle, .requestingPermissions:
                        ProgressView()

                    case .readyForFront:
                        instructionCard(
                            title: "Front Photo",
                            message: "Stand straight with arms slightly away, feet shoulder width apart, and position yourself about 7 ft from the camera.",
                            actionTitle: "Begin Countdown",
                            action: viewModel.captureFrontPhoto
                        )

                    case .countdownFront(let seconds):
                        countdownView(seconds: seconds)

                    case .capturingFront, .capturingSide, .processing:
                        ProgressView()
                            .progressViewStyle(.circular)
                            .tint(.blue)

                    case .reviewFront(let photo):
                        reviewCard(photo: photo, acceptAction: viewModel.acceptFrontCapture, retakeAction: viewModel.retakeFrontCapture)

                    case .readyForSide:
                        instructionCard(
                            title: "Side Photo",
                            message: "Turn 90° to the right, keep arms relaxed, and maintain the same 7 ft distance.",
                            actionTitle: "Begin Countdown",
                            action: viewModel.captureSidePhoto
                        )

                    case .countdownSide(let seconds):
                        countdownView(seconds: seconds)

                    case .reviewSide(let photo):
                        reviewCard(photo: photo, acceptAction: viewModel.acceptSideCapture, retakeAction: viewModel.retakeSideCapture)

                    case .completed:
                        VStack(spacing: 12) {
                            Image(systemName: "checkmark.circle.fill")
                                .font(.system(size: 64))
                                .foregroundStyle(.green)
                            Text("Measurements ready to review.")
                                .font(.title3).bold()
                            Button("Restart Flow") {
                                viewModel.resetFlow()
                                viewModel.startFlow()
                            }
                        }

                    case .error:
                        if viewModel.requiresManualFallback {
                            VStack(spacing: 12) {
                                Text(viewModel.manualFallbackInstructions)
                                    .font(.system(size: 12))
                                    .foregroundStyle(.secondary)
                                    .multilineTextAlignment(.center)
                                    .minimumScaleFactor(0.8)
                                Text("A two-person manual capture checklist will replace this screen soon.")
                                    .font(.system(size: 11))
                                    .foregroundStyle(.tertiary)
                                    .multilineTextAlignment(.center)
                            }
                            .padding()
                            .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 16))
                        } else {
                            Button("Retry") {
                                viewModel.resetFlow()
                                viewModel.startFlow()
                            }
                            .buttonStyle(.borderedProminent)
                        }
                    }
                }

                Spacer(minLength: 32)
            }
            .frame(maxWidth: .infinity, alignment: .center)
            .padding(.horizontal, 20)
            .padding(.bottom, 40)
        }
        .scrollIndicators(.hidden)
        .toolbar(.hidden, for: .navigationBar)
        .safeAreaInset(edge: .top, spacing: 0) { Color.black.opacity(0.001).frame(height: 10) }
        .safeAreaInset(edge: .bottom, spacing: 0) { Color.black.opacity(0.001).frame(height: 16) }
        .onAppear {
            if viewModel.state == .idle {
                viewModel.startFlow()
            }
        }
        .alert("Capture Error",
               isPresented: Binding(
                get: { viewModel.alertMessage != nil },
                set: { _ in viewModel.alertMessage = nil }
               ),
               actions: {
            Button("OK", role: .cancel) {}
        }, message: {
            Text(viewModel.alertMessage ?? "")
        })
    }
    private var showsPreview: Bool {
        switch viewModel.state {
        case .readyForFront, .readyForSide, .countdownFront, .countdownSide, .capturingFront, .capturingSide:
            return true
        default:
            return false
        }
    }

    private func instructionCard(
        title: String,
        message: String,
        actionTitle: String,
        action: @escaping () -> Void
    ) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(title)
                .font(.system(size: 14, weight: .semibold))
                .foregroundStyle(.primary)
            Text(message)
                .font(.system(size: 12))
                .foregroundStyle(.secondary)
                .minimumScaleFactor(0.85)
            Button(actionTitle, action: action)
                .buttonStyle(.borderedProminent)
                .font(.system(size: 13, weight: .semibold))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(.ultraThinMaterial.opacity(0.85), in: RoundedRectangle(cornerRadius: 16))
    }
    
    private func countdownView(seconds: Int) -> some View {
        VStack(spacing: 16) {
            Text("Hold your position")
                .font(.system(size: 14, weight: .semibold))
                .foregroundStyle(.secondary)
            Text("\(seconds)")
                .font(.system(size: 88, weight: .bold))
                .monospacedDigit()
            Text("Keeping roughly 7 ft from the camera ensures accurate measurements.")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
                .font(.system(size: 11))
                .minimumScaleFactor(0.85)
        }
        .frame(maxWidth: .infinity)
    }

    private func reviewCard(photo: CapturedPhoto, acceptAction: @escaping () -> Void, retakeAction: @escaping () -> Void) -> some View {
        VStack(spacing: 16) {
            if let image = photo.uiImage {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFit()
                    .cornerRadius(16)
                    .frame(maxWidth: .infinity)
            } else {
                Text("Unable to load preview")
                    .foregroundStyle(.secondary)
            }

            HStack(spacing: 16) {
                Button("Retake", action: retakeAction)
                    .buttonStyle(.bordered)

                Button("Accept", action: acceptAction)
                    .buttonStyle(.borderedProminent)
            }
        }
        .padding()
        .background(.ultraThinMaterial.opacity(0.85), in: RoundedRectangle(cornerRadius: 16))
    }
}

#Preview {
    NavigationStack {
        CaptureFlowView()
    }
}
