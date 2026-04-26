import Foundation

public class LLMService {
    public init() {}

    /// This is a mock function for the MLX-based inference as specified for the initial PR.
    /// It mimics text generation from an LLM.
    public func generate(prompt: String) async throws -> String {
        // Simulate network delay or inference time
        try await Task.sleep(nanoseconds: 1_000_000_000) // 1 second

        // Simple heuristic to provide a mock response for testing the loop
        if prompt.contains("1+1") {
            return """
            計算します。

            <execute_python>
            print(1+1)
            </execute_python>
            """
        } else if prompt.contains("Observation:") {
            return "実行結果を確認しました。タスクは完了です。"
        } else if prompt.contains("ユーザーが実行を拒否しました") {
            return "申し訳ありません。別の方法を提案しますか？"
        } else {
            return """
            こんにちは。お手伝いします。

            Pythonを実行する必要がある場合は、以下のようにお知らせします。

            <execute_python>
            import sys
            print("Hello from Python", sys.version)
            </execute_python>
            """
        }
    }
}
