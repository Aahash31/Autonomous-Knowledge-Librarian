import { useState } from 'react'
import './App.css'

function App() {
  // 1. State Management
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isUploading, setIsUploading] = useState(false)

  // 2. Logic Zone (Handlers)
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/upload`, {
        method: "POST",
        body: formData,
      });
      if (response.ok) {
        alert("✅ Notes indexed!");
      }
    } catch (error) {
      console.error("Upload failed:", error);
    } finally {
      setIsUploading(false);
    }
  };

  const clearLibrary = async () => {
    if (!window.confirm("⚠️ Are you sure? This will delete ALL indexed notes from your database.")) return;

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/clear-notes`, {
        method: "DELETE",
      });
      if (response.ok) {
        alert("🗑️ Library cleared successfully!");
        setMessages([]);
      }
    } catch (error) {
      console.error("Failed to clear library:", error);
    }
  };

  // 3. Chat Logic
  const sendMessage = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    const newMessages = [...messages, { role: 'user', text: input }]
    setMessages(newMessages)
    setInput('')

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, thread_id: "3" })
      })
      const data = await response.json()
      setMessages([...newMessages, { role: 'librarian', text: data.response }])
    } catch (error) {
      console.error("Error:", error)
    }
  }

  return (
    <div className="app-wrapper">
      <header className="app-header">
        <div className="title-area">
          <h1>📚 My Personal Librarian</h1>
          <p>Your intelligent knowledge assistant</p>
        </div>
        
        {/* --- MANAGEMENT AREA --- */}
        <div className="controls-container">
          <div className="upload-container">
            <label htmlFor="file-upload" className="upload-button">
              {isUploading ? "⚡ Indexing..." : "📤 Upload Notes (.txt)"}
            </label>
            <input 
              id="file-upload"
              type="file" 
              onChange={handleFileUpload} 
              accept=".txt,.md" 
              hidden 
            />
          </div>

          {/* --- Clear Button --- */}
          <button onClick={clearLibrary} className="clear-button">
            🗑️ Clear Library
          </button>
        </div>
      </header>
    <main className="chat-container">
      <div className="chat-box">
        {messages.map((msg, index) => (
          <div key={index} className={`message-wrapper ${msg.role}`}>
            <div className="message-bubble">
              {msg.text}
            </div>
          </div>
        ))}
      </div>

        <form onSubmit={sendMessage} className="input-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your documents..."
          />
          <button type="submit">Send</button>
        </form>
      </main>
    </div>
  )
}

export default App