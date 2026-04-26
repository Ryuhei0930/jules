import Foundation
import PythonKit

public class PythonExecutorService {
    public init() {}

    public func execute(code: String) -> String {
        do {
            let sys = try Python.attemptImport("sys")
            let io = try Python.attemptImport("io")
            let contextlib = try Python.attemptImport("contextlib")

            // Redirect stdout and stderr
            let stdout = io.StringIO()
            let stderr = io.StringIO()

            // We use Python's exec function
            let builtins = try Python.attemptImport("builtins")

            // Execute the code within the redirected context
            sys.stdout = stdout
            sys.stderr = stderr

            // Safe execution
            let globals = Python.dict()
            let locals = Python.dict()

            builtins.exec(code, globals, locals)

            // Restore stdout and stderr
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

            let outStr = String(stdout.getvalue()) ?? ""
            let errStr = String(stderr.getvalue()) ?? ""

            if !errStr.isEmpty {
                return "Output:\n\(outStr)\nError:\n\(errStr)"
            } else {
                return outStr.isEmpty ? "Executed successfully with no output." : outStr
            }
        } catch let error as PythonError {
            // Restore stdout and stderr just in case
            if let sys = try? Python.attemptImport("sys") {
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
            }
            return "PythonError: \(error.localizedDescription)"
        } catch {
            return "Execution failed with error: \(error.localizedDescription)"
        }
    }
}
