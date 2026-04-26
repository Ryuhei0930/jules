import SwiftUI

public struct ChatView: View {
    @StateObject private var viewModel = ChatViewModel()
    @State private var inputText: String = ""

    public init() {}

    public var body: some View {
        VStack {
            ScrollView {
                LazyVStack(spacing: 12) {
                    ForEach(viewModel.messages) { message in
                        MessageRowView(message: message) { action in
                            switch action {
                            case .approve:
                                viewModel.approveCode(for: message.id)
                            case .reject:
                                viewModel.rejectCode(for: message.id)
                            }
                        }
                    }
                }
                .padding()
            }

            Divider()

            HStack {
                TextField("メッセージを入力...", text: $inputText)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .disabled(viewModel.isProcessing)

                Button(action: {
                    viewModel.sendMessage(inputText)
                    inputText = ""
                }) {
                    Image(systemName: "paperplane.fill")
                        .foregroundColor(inputText.isEmpty || viewModel.isProcessing ? .gray : .blue)
                }
                .disabled(inputText.isEmpty || viewModel.isProcessing)
            }
            .padding()
        }
        .navigationTitle("OpenClaw")
    }
}

struct MessageRowView: View {
    let message: Message
    let onAction: (MessageAction) -> Void

    enum MessageAction {
        case approve
        case reject
    }

    var body: some View {
        VStack(alignment: message.role == .user ? .trailing : .leading, spacing: 8) {
            HStack {
                if message.role == .user {
                    Spacer()
                }

                Text(message.content)
                    .padding(12)
                    .background(message.role == .user ? Color.blue.opacity(0.2) : Color.gray.opacity(0.2))
                    .cornerRadius(12)

                if message.role != .user {
                    Spacer()
                }
            }

            if let code = message.proposedCode {
                VStack(alignment: .leading, spacing: 8) {
                    Text("実行するPythonコード:")
                        .font(.caption)
                        .foregroundColor(.secondary)

                    Text(code)
                        .font(.system(.subheadline, design: .monospaced))
                        .padding()
                        .background(Color.black.opacity(0.05))
                        .cornerRadius(8)

                    HStack(spacing: 16) {
                        Button(action: { onAction(.approve) }) {
                            Text("許可")
                                .bold()
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 8)
                                .background(Color.green)
                                .foregroundColor(.white)
                                .cornerRadius(8)
                        }

                        Button(action: { onAction(.reject) }) {
                            Text("拒否")
                                .bold()
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 8)
                                .background(Color.red)
                                .foregroundColor(.white)
                                .cornerRadius(8)
                        }
                    }
                }
                .padding()
                .background(Color.orange.opacity(0.1))
                .cornerRadius(12)
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(Color.orange, lineWidth: 1)
                )
            }
        }
    }
}
