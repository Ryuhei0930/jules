import Foundation
import Combine

@MainActor
public class ChatViewModel: ObservableObject {
    @Published public var messages: [Message] = []
    @Published public var isProcessing: Bool = false

    private let llmService: LLMService
    private let pythonExecutor: PythonExecutorService

    let systemPrompt = """
    You are a helpful assistant running on iPadOS. The user's instructions are absolute. You must always reply in Japanese. To solve tasks, propose Python code wrapped in <execute_python>...</execute_python> tags. You CANNOT execute it yourself; you must wait for the user to review and approve it.
    """

    public init(llmService: LLMService = LLMService(), pythonExecutor: PythonExecutorService = PythonExecutorService()) {
        self.llmService = llmService
        self.pythonExecutor = pythonExecutor

        // Add initial system message (optional, but good for context)
        let systemMsg = Message(role: .system, content: systemPrompt)
        messages.append(systemMsg)
    }

    public func sendMessage(_ text: String) {
        guard !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }

        let userMessage = Message(role: .user, content: text)
        messages.append(userMessage)

        Task {
            await runAgentLoop()
        }
    }

    private func runAgentLoop() async {
        isProcessing = true
        defer { isProcessing = false }

        // Format history
        let prompt = buildPrompt()

        do {
            let response = try await llmService.generate(prompt: prompt)

            // Check for python code tags
            let pythonRegex = try NSRegularExpression(pattern: "<execute_python>(.*?)</execute_python>", options: [.dotMatchesLineSeparators])
            let nsString = response as NSString
            let results = pythonRegex.matches(in: response, range: NSRange(location: 0, length: nsString.length))

            var proposedCode: String? = nil
            if let match = results.first {
                proposedCode = nsString.substring(with: match.range(at: 1)).trimmingCharacters(in: .whitespacesAndNewlines)
            }

            // Add agent message
            let agentMessage = Message(
                role: .agent,
                content: response,
                proposedCode: proposedCode
            )
            messages.append(agentMessage)

            // If there's proposed code, the loop naturally PAUSES here waiting for user input via UI buttons.

        } catch {
            let errorMsg = Message(role: .system, content: "Error generating response: \(error.localizedDescription)")
            messages.append(errorMsg)
        }
    }

    private func buildPrompt() -> String {
        return messages.map { "\($0.role == .user ? "User" : ($0.role == .agent ? "Agent" : "System")): \($0.content)" }.joined(separator: "\n")
    }

    public func approveCode(for messageId: UUID) {
        guard let index = messages.firstIndex(where: { $0.id == messageId }),
              let code = messages[index].proposedCode else { return }

        // Remove proposed code so buttons disappear
        messages[index].proposedCode = nil

        // Add a message indicating user approved
        messages.append(Message(role: .user, content: "コードの実行を許可しました。"))

        Task {
            isProcessing = true

            // Execute python on a background thread to prevent blocking the UI
            let result = await Task.detached {
                self.pythonExecutor.execute(code: code)
            }.value

            // Observation
            let observationMessage = Message(role: .system, content: "Observation:\n\(result)")
            messages.append(observationMessage)

            // Resume loop
            await runAgentLoop()
        }
    }

    public func rejectCode(for messageId: UUID) {
        guard let index = messages.firstIndex(where: { $0.id == messageId }) else { return }

        // Remove proposed code so buttons disappear
        messages[index].proposedCode = nil

        let rejectMessage = Message(role: .user, content: "ユーザーが実行を拒否しました。別のアプローチを提案してください。")
        messages.append(rejectMessage)

        Task {
            // Resume loop
            await runAgentLoop()
        }
    }
}
