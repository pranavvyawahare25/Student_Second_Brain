import { useState } from 'react'
import ResearchResult from './ResearchResult'
import './ChatSection.css'

function ChatSection({ chatHistory, onSendQuery }) {
    const [input, setInput] = useState('')

    const handleSend = () => {
        if (input.trim()) {
            onSendQuery(input.trim())
            setInput('')
        }
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') handleSend()
    }

    return (
        <div className="chat-section">
            <div className="chat-header">
                <span className="chat-icon">🤖</span>
                <h4>AI Query Assistant</h4>
                <span className="rag-badge">RAG Powered</span>
            </div>

            <div className="chat-messages">
                {chatHistory.length === 0 && (
                    <div className="chat-empty">
                        <p>Ask questions about your uploaded materials...</p>
                    </div>
                )}
                {chatHistory.map((msg, idx) => (
                    <div key={idx} className={`chat-msg ${msg.type}`}>
                        <span className="msg-icon">{msg.type === 'user' ? '👤' : '🤖'}</span>
                        <div className="msg-content">
                            {msg.type === 'research' ? (
                                <ResearchResult data={msg.data} />
                            ) : (
                                <span className="msg-text">{msg.text}</span>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            <div className="chat-input-area">
                <input
                    type="text"
                    placeholder="Ask about your course materials..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                />
                <button className="send-btn" onClick={handleSend}>
                    <span>Send</span>
                    <span className="send-icon">➤</span>
                </button>
            </div>
        </div>
    )
}

export default ChatSection
