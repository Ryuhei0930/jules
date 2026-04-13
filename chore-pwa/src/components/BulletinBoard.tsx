"use client";

import { useState, useEffect } from "react";
import { AlertCircle, Send, MessageSquare } from "lucide-react";
import { supabase } from "@/utils/supabase/client";

// Define message type
interface Message {
  id: string;
  user_id: string;
  content: string;
  is_important: boolean;
  created_at: string;
  users: {
    name: string;
    role: string;
  };
}

/**
 * BulletinBoard component allowing both parent and child roles to read and post
 * messages to the family communication board.
 */
export default function BulletinBoard() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newContent, setNewContent] = useState("");
  const [isImportant, setIsImportant] = useState(false);
  const [loading, setLoading] = useState(false);

  // Fetch recent messages on mount and role change
  useEffect(() => {
    fetchMessages();
    // In a real app, you would set up Supabase Realtime subscriptions here.
  }, []);

  /**
   * Fetches the latest 5 messages from the database.
   */
  const fetchMessages = async () => {
    try {
      const { data, error } = await supabase
        .from("messages")
        .select(`
          *,
          users (name, role)
        `)
        .order("created_at", { ascending: false })
        .limit(5);

      if (error) {
        console.error("Error fetching messages:", error);
      } else if (data) {
        setMessages(data as unknown as Message[]);
      }
    } catch (err) {
      console.error("Unexpected error:", err);
    }
  };

  /**
   * Submits a new message to the database.
   */
  const handlePostMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newContent.trim()) return;

    setLoading(true);

    try {
      const { data: { user }, error: authError } = await supabase.auth.getUser();

      if (authError || !user) {
         console.error("Authentication required");
         return;
      }

      const { error } = await supabase.from("messages").insert([
        {
          user_id: user.id,
          content: newContent,
          is_important: isImportant,
        },
      ]);

      if (error) {
        console.error("Error posting message:", error);
      } else {
        setNewContent("");
        setIsImportant(false);
        // Refresh list
        fetchMessages();
      }
    } catch (err) {
      console.error("Unexpected error posting:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 mb-6">
      <div className="flex items-center gap-2 mb-4 text-gray-800">
        <MessageSquare className="w-5 h-5 text-blue-500" />
        <h2 className="text-lg font-bold">家族の伝言板</h2>
      </div>

      {/* Message List */}
      <div className="space-y-3 mb-4">
        {messages.length === 0 ? (
          <p className="text-gray-500 text-sm text-center py-4">まだメッセージはありません</p>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`p-3 rounded-xl border-l-4 ${
                msg.is_important
                  ? "bg-red-50 border-red-500"
                  : "bg-gray-50 border-gray-300"
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold text-gray-600">
                  {msg.users?.name || "Unknown"}
                </span>
                <span className="text-xs text-gray-400">
                  {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
              <div className="flex items-start gap-2">
                {msg.is_important && (
                  <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 shrink-0" />
                )}
                <p
                  className={`text-sm break-words ${
                    msg.is_important ? "text-red-700 font-medium" : "text-gray-800"
                  }`}
                >
                  {msg.content}
                </p>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Post Form */}
      <form onSubmit={handlePostMessage} className="bg-gray-50 rounded-xl p-3 border border-gray-200">
        <div className="flex flex-col gap-2">
          <textarea
            value={newContent}
            onChange={(e) => setNewContent(e.target.value)}
            placeholder="メッセージを入力..."
            className="w-full text-sm p-2 rounded-lg border-gray-300 border focus:ring-2 focus:ring-blue-500 focus:outline-none resize-none"
            rows={2}
          />
          <div className="flex justify-between items-center mt-1">
            <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
              <input
                type="checkbox"
                checked={isImportant}
                onChange={(e) => setIsImportant(e.target.checked)}
                className="w-4 h-4 rounded text-red-500 focus:ring-red-500 border-gray-300"
              />
              <span className="font-medium text-red-600 flex items-center gap-1">
                <AlertCircle className="w-4 h-4" /> 重要
              </span>
            </label>
            <button
              type="submit"
              disabled={loading || !newContent.trim()}
              className="flex items-center justify-center gap-1 bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-full font-bold text-sm transition-colors disabled:bg-blue-300"
            >
              <Send className="w-4 h-4" />
              送信
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
