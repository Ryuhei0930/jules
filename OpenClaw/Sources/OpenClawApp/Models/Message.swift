import Foundation

/// Represents a message in the chat
public struct Message: Identifiable, Equatable {
    public let id: UUID
    public let role: Role
    public let content: String
    public let timestamp: Date
    public var proposedCode: String?

    public enum Role: Equatable {
        case user
        case agent
        case system
    }

    public init(id: UUID = UUID(), role: Role, content: String, timestamp: Date = Date(), proposedCode: String? = nil) {
        self.id = id
        self.role = role
        self.content = content
        self.timestamp = timestamp
        self.proposedCode = proposedCode
    }
}
