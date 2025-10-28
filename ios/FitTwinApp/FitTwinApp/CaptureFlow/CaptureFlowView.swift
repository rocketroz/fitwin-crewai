import SwiftUI

struct CaptureFlowView: View {
    @StateObject private var viewModel = CaptureFlowViewModel()

    var body: some View {
        VStack(spacing: 24) {
            Text(viewModel.state.statusMessage)
                .font(.headline)
                .multilineTextAlignment(.center)

            switch viewModel.state {
            case .idle, .requestingPermissions:
                ProgressView()

            case .readyForFront:
                instructionCard(
                    title: "Front Photo",
                    message: "Stand straight with arms slightly away from the body.",
                    actionTitle: "Capture Front",
                    action: viewModel.captureFrontPhoto
                )

            case .capturingFront, .capturingSide, .processing:
                ProgressView()
                    .progressViewStyle(.circular)
                    .tint(.blue)

            case .readyForSide:
                instructionCard(
                    title: "Side Photo",
                    message: "Turn 90° to the right with arms relaxed.",
                    actionTitle: "Capture Side",
                    action: viewModel.captureSidePhoto
                )

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
                Button("Retry") {
                    viewModel.resetFlow()
                    viewModel.startFlow()
                }
                .buttonStyle(.borderedProminent)
            }

            Spacer()
        }
        .padding(24)
        .navigationTitle("Capture")
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

    private func instructionCard(
        title: String,
        message: String,
        actionTitle: String,
        action: @escaping () -> Void
    ) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(title)
                .font(.title3.bold())
            Text(message)
                .font(.body)
            Button(actionTitle, action: action)
                .buttonStyle(.borderedProminent)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 16))
    }
}

#Preview {
    NavigationStack {
        CaptureFlowView()
    }
}
