import Foundation
import PythonKit

public class PythonExecutorService {
    public init() {
        // Initialize Python environment if needed.
        // In a real environment, you might need to set PYTHON_LIBRARY and set up a virtualenv.
        // For standard local python, PythonKit usually finds the default installation.
    }

    /// Executes Python code and captures the output asynchronously to avoid blocking the main thread
    public func execute(code: String) async -> String {
        return await Task.detached { [weak self] in
            guard self != nil else { return "実行エラー" }
            return Self.runPython(code: code)
        }.value
    }

    private static func runPython(code: String) -> String {
        do {
            let sys = try Python.attemptImport("sys")
            let io = try Python.attemptImport("io")
            let contextlib = try Python.attemptImport("contextlib")

            // Set up string buffer to capture stdout and stderr
            let stdoutBuffer = io.StringIO()
            let stderrBuffer = io.StringIO()

            let stdoutRedirect = contextlib.redirect_stdout(stdoutBuffer)
            let stderrRedirect = contextlib.redirect_stderr(stderrBuffer)

            // Enter context managers
            let stdoutContext = stdoutRedirect.__enter__()
            let stderrContext = stderrRedirect.__enter__()

            // Execute the code
            let globals = Python.dict()
            let locals = Python.dict()

            do {
                let codeObject = try Python.builtins.compile(code, "<string>", "exec")
                try Python.builtins.exec(codeObject, globals, locals)
            } catch let error as PythonError {
                // If there's an error in execution, capture it and restore standard streams
                let _ = stdoutRedirect.__exit__(nil, nil, nil)
                let _ = stderrRedirect.__exit__(nil, nil, nil)

                return "Python Execution Error:\n\(error)"
            } catch {
                let _ = stdoutRedirect.__exit__(nil, nil, nil)
                let _ = stderrRedirect.__exit__(nil, nil, nil)

                return "Unknown Swift Error:\n\(error)"
            }

            // Exit context managers
            let _ = stdoutRedirect.__exit__(nil, nil, nil)
            let _ = stderrRedirect.__exit__(nil, nil, nil)

            let stdoutStr = String(stdoutBuffer.getvalue()) ?? ""
            let stderrStr = String(stderrBuffer.getvalue()) ?? ""

            var result = ""
            if !stdoutStr.isEmpty {
                result += "標準出力 (stdout):\n\(stdoutStr)"
            }
            if !stderrStr.isEmpty {
                if !result.isEmpty { result += "\n" }
                result += "標準エラー (stderr):\n\(stderrStr)"
            }

            if result.isEmpty {
                result += "実行成功。出力はありませんでした。"
            }

            return result
        } catch {
            return "Python Environment Error: Could not import required modules. \(error)"
        }
    }
}
