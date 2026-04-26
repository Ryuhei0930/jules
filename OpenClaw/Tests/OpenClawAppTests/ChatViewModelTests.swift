import XCTest
@testable import OpenClawApp

@MainActor
final class ChatViewModelTests: XCTestCase {

    // Create a mock LLM service that returns predictable responses
    class MockLLMService: LLMService {
        var responseToReturn: String = ""
        var receivedPrompt: String = ""

        override func generate(prompt: String) async throws -> String {
            self.receivedPrompt = prompt
            return responseToReturn
        }
    }

    // Create a mock Python Executor
    class MockPythonExecutor: PythonExecutorService {
        var executedCode: String = ""
        var resultToReturn: String = "Mock execution success"

        override func execute(code: String) -> String {
            self.executedCode = code
            return resultToReturn
        }
    }

    func testSendMessage_AddsUserMessageAndTriggersLLM() async {
        let mockLLM = MockLLMService()
        mockLLM.responseToReturn = "Test response"
        let mockExecutor = MockPythonExecutor()

        let viewModel = ChatViewModel(llmService: mockLLM, pythonExecutor: mockExecutor)

        let initialCount = viewModel.messages.count // Should be 1 (System prompt)

        viewModel.sendMessage("Hello")

        // Yield to allow Task to run
        try? await Task.sleep(nanoseconds: 100_000_000)

        XCTAssertEqual(viewModel.messages.count, initialCount + 2) // User msg + Agent msg
        XCTAssertEqual(viewModel.messages[initialCount].role, .user)
        XCTAssertEqual(viewModel.messages[initialCount].content, "Hello")
        XCTAssertEqual(viewModel.messages[initialCount + 1].role, .agent)
        XCTAssertEqual(viewModel.messages[initialCount + 1].content, "Test response")
    }

    func testLLMResponse_WithPythonCode_SetsProposedCode() async {
        let mockLLM = MockLLMService()
        mockLLM.responseToReturn = """
        Here is the code:
        <execute_python>
        print('hello')
        </execute_python>
        """
        let mockExecutor = MockPythonExecutor()

        let viewModel = ChatViewModel(llmService: mockLLM, pythonExecutor: mockExecutor)
        let initialCount = viewModel.messages.count

        viewModel.sendMessage("Write code")
        try? await Task.sleep(nanoseconds: 100_000_000)

        let agentMessage = viewModel.messages.last!
        XCTAssertEqual(agentMessage.role, .agent)
        XCTAssertEqual(agentMessage.proposedCode, "print('hello')")
    }

    func testApproveCode_ExecutesCodeAndResumesLoop() async {
        let mockLLM = MockLLMService()
        mockLLM.responseToReturn = "Response after execution"
        let mockExecutor = MockPythonExecutor()
        mockExecutor.resultToReturn = "Printed output"

        let viewModel = ChatViewModel(llmService: mockLLM, pythonExecutor: mockExecutor)

        // Manually inject a message with proposed code
        var agentMsg = Message(role: .agent, content: "Some text", proposedCode: "print('x')")
        viewModel.messages.append(agentMsg)

        viewModel.approveCode(for: agentMsg.id)
        try? await Task.sleep(nanoseconds: 100_000_000)

        XCTAssertEqual(mockExecutor.executedCode, "print('x')")

        // Check message trace: User Approval -> System Observation -> Agent response
        let messages = viewModel.messages
        XCTAssertEqual(messages[messages.count - 3].content, "コードの実行を許可しました。")
        XCTAssertTrue(messages[messages.count - 2].content.contains("Observation:\nPrinted output"))
        XCTAssertEqual(messages.last!.content, "Response after execution")
    }

    func testRejectCode_SendsRejectionAndResumesLoop() async {
        let mockLLM = MockLLMService()
        mockLLM.responseToReturn = "Alternative response"
        let mockExecutor = MockPythonExecutor()

        let viewModel = ChatViewModel(llmService: mockLLM, pythonExecutor: mockExecutor)

        var agentMsg = Message(role: .agent, content: "Some text", proposedCode: "print('x')")
        viewModel.messages.append(agentMsg)

        viewModel.rejectCode(for: agentMsg.id)
        try? await Task.sleep(nanoseconds: 100_000_000)

        XCTAssertEqual(mockExecutor.executedCode, "") // Should not execute

        let messages = viewModel.messages
        XCTAssertEqual(messages[messages.count - 2].content, "ユーザーが実行を拒否しました。別のアプローチを提案してください。")
        XCTAssertEqual(messages.last!.content, "Alternative response")
    }
}
