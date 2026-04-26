import Foundation

public enum Role: String, Codable {
    case user
    case assistant
    case system
    case observation // Used for the results of Python execution
}

public struct Message: Identifiable, Codable, Equatable {
    public let id: UUID
    public let role: Role
    public let content: String
    public let timestamp: Date
    public var proposedCode: String?

    public init(id: UUID = UUID(), role: Role, content: String, timestamp: Date = Date(), proposedCode: String? = nil) {
        self.id = id
        self.role = role
        self.content = content
        self.timestamp = timestamp
        self.proposedCode = proposedCode
    }
}
