import Foundation
import MLX

public class LLMService {
    public init() {}

    /// Generates text based on an array of messages representing the conversation history.
    /// Uses a mocked implementation for initial setup, to be replaced by actual mlx-swift local inference.
    public func generate(messages: [Message]) async throws -> String {
        // Mocking an LLM processing delay
        try await Task.sleep(nanoseconds: 2_000_000_000)

        guard let lastMessage = messages.last else {
            return "エラー: メッセージがありません。"
        }

        let content = lastMessage.content

        // Very basic mock logic for demonstration purposes
        if content.contains("計算") || content.contains("Python") {
            return """
            承知いたしました。Pythonを使用して計算を行います。以下のコードを実行させてください。

            <execute_python>
            result = 10 + 5 * 2
            print(f"計算結果は {result} です。")
            </execute_python>

            実行を許可しますか？
            """
        } else if lastMessage.role == .observation {
            return "実行結果を確認しました。\n\n結果: \(content)\n\nこの結果でよろしいでしょうか？他に何かお手伝いできることはありますか？"
        } else {
            return "ご質問ありがとうございます。「\(content)」ですね。\nもしシステムの機能が必要な場合は、Pythonの実行を提案します。"
        }
    }
}
