import SwiftUI

public struct ChatView: View {
    @StateObject private var viewModel: ChatViewModel
    @State private var inputText: String = ""

    public init(viewModel: ChatViewModel) {
        _viewModel = StateObject(wrappedValue: viewModel)
    }

    public var body: some View {
        VStack {
            ScrollView {
                LazyVStack(spacing: 12) {
                    ForEach(viewModel.messages) { message in
                        MessageRow(message: message, viewModel: viewModel)
                    }
                }
                .padding()
            }

            HStack {
                TextField("メッセージを入力...", text: $inputText)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .disabled(viewModel.isGenerating)

                Button(action: {
                    guard !inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
                    viewModel.sendMessage(text: inputText)
                    inputText = ""
                }) {
                    Image(systemName: "paperplane.fill")
                        .foregroundColor(viewModel.isGenerating ? .gray : .blue)
                }
                .disabled(viewModel.isGenerating)
            }
            .padding()
        }
        .navigationTitle("Open Claw")
    }
}

struct MessageRow: View {
    let message: Message
    @ObservedObject var viewModel: ChatViewModel

    var body: some View {
        VStack(alignment: message.role == .user ? .trailing : .leading, spacing: 8) {
            HStack {
                if message.role == .user { Spacer() }

                Text(message.content)
                    .padding()
                    .background(backgroundColor(for: message.role))
                    .foregroundColor(textColor(for: message.role))
                    .cornerRadius(12)

                if message.role != .user { Spacer() }
            }

            if let proposedCode = message.proposedCode {
                VStack(alignment: .leading) {
                    Text("実行するPythonコード:")
                        .font(.caption)
                        .foregroundColor(.gray)

                    Text(proposedCode)
                        .font(.system(.body, design: .monospaced))
                        .padding()
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(8)

                    // Human in the loop buttons
                    if message.id == viewModel.messages.last?.id && viewModel.isAwaitingApproval {
                        HStack(spacing: 16) {
                            Button(action: {
                                viewModel.approveCodeExecution(for: message)
                            }) {
                                Text("許可")
                                    .fontWeight(.bold)
                                    .foregroundColor(.white)
                                    .padding(.horizontal, 24)
                                    .padding(.vertical, 8)
                                    .background(Color.green)
                                    .cornerRadius(8)
                            }

                            Button(action: {
                                viewModel.rejectCodeExecution(for: message)
                            }) {
                                Text("拒否")
                                    .fontWeight(.bold)
                                    .foregroundColor(.white)
                                    .padding(.horizontal, 24)
                                    .padding(.vertical, 8)
                                    .background(Color.red)
                                    .cornerRadius(8)
                            }
                        }
                        .padding(.top, 4)
                    } else if message.id != viewModel.messages.last?.id {
                        Text("処理済み")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                }
                .padding(.horizontal)
            }
        }
    }

    private func backgroundColor(for role: Role) -> Color {
        switch role {
        case .user: return .blue
        case .assistant: return Color(UIColor.secondarySystemBackground)
        case .system: return .orange.opacity(0.2)
        case .observation: return .purple.opacity(0.1)
        }
    }

    private func textColor(for role: Role) -> Color {
        switch role {
        case .user: return .white
        default: return .primary
        }
    }
}
