import Foundation

@MainActor
public class ChatViewModel: ObservableObject {
    @Published public var messages: [Message] = []
    @Published public var isGenerating: Bool = false
    @Published public var isAwaitingApproval: Bool = false

    private let llmService: LLMService
    private let pythonService: PythonExecutorService

    private let systemPrompt = """
    You are a helpful assistant running on iPadOS. The user's instructions are absolute. You must always reply in natural Japanese.
    To solve tasks, you can propose Python code. You MUST wrap the Python code in `<execute_python>...</execute_python>` tags.
    You CANNOT execute it yourself; you must wait for the user to review and approve it.
    """

    public init(llmService: LLMService = LLMService(), pythonService: PythonExecutorService = PythonExecutorService()) {
        self.llmService = llmService
        self.pythonService = pythonService

        // Initialize with system prompt (hidden from UI, but used for generation context)
        self.messages = [Message(role: .system, content: systemPrompt)]
    }

    public func sendMessage(text: String) {
        let userMessage = Message(role: .user, content: text)
        messages.append(userMessage)

        Task {
            await generateResponse()
        }
    }

    private func generateResponse() async {
        isGenerating = true
        isAwaitingApproval = false

        do {
            let responseText = try await llmService.generate(messages: messages)

            // Parse response for <execute_python> tags
            if let extractedCode = extractPythonCode(from: responseText) {
                // If code is found, set it in the message and pause for human-in-the-loop
                let assistantMessage = Message(role: .assistant, content: responseText, proposedCode: extractedCode)
                messages.append(assistantMessage)
                isAwaitingApproval = true
            } else {
                // Regular response
                let assistantMessage = Message(role: .assistant, content: responseText)
                messages.append(assistantMessage)
            }
        } catch {
            let errorMessage = Message(role: .assistant, content: "エラーが発生しました: \(error.localizedDescription)")
            messages.append(errorMessage)
        }

        isGenerating = false
    }

    public func approveCodeExecution(for message: Message) {
        guard let code = message.proposedCode else { return }

        // Remove the approval state to avoid repeated executions
        isAwaitingApproval = false

        Task {
            isGenerating = true

            // Execute python code asynchronously to not block UI
            let result = await pythonService.execute(code: code)

            // Add observation to chat history
            let observationMessage = Message(role: .observation, content: "Python実行結果:\n\(result)")
            messages.append(observationMessage)

            isGenerating = false

            // Send the observation back to the LLM to continue the ReAct loop
            await generateResponse()
        }
    }

    public func rejectCodeExecution(for message: Message) {
        isAwaitingApproval = false

        let rejectionMessage = Message(role: .observation, content: "ユーザーが実行を拒否しました。別のアプローチを提案してください。")
        messages.append(rejectionMessage)

        Task {
            await generateResponse()
        }
    }

    private func extractPythonCode(from text: String) -> String? {
        let openTag = "<execute_python>"
        let closeTag = "</execute_python>"

        guard let startIndex = text.range(of: openTag)?.upperBound,
              let endIndex = text.range(of: closeTag)?.lowerBound,
              startIndex < endIndex else {
            return nil
        }

        return String(text[startIndex..<endIndex]).trimmingCharacters(in: .whitespacesAndNewlines)
    }
}
