import SwiftUI

struct ContentView: View {
    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                Image(systemName: "ruler")
                    .font(.system(size: 64))
                    .foregroundStyle(.blue.gradient)

                VStack(spacing: 8) {
                    Text("FitTwin iOS")
                        .font(.title2.weight(.semibold))
                    Text("Foundation for the measurement capture experience.")
                        .font(.subheadline)
                        .multilineTextAlignment(.center)
                        .foregroundStyle(.secondary)
                }

                NavigationLink {
                    CaptureFlowView()
                } label: {
                    Text("Start Prototype Flow")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)

                Spacer()
            }
            .padding(32)
            .navigationTitle("Home")
        }
    }
}

#Preview {
    ContentView()
}
