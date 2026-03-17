import { useState } from 'react'
import './App.css'

function App() {
  // Hold chat history and the current text box input
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')

  // Run when "send" button is clicked
  const sendMessage = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    // Add new question to the screen immediately
    const newMessages = [...messages, { role: 'user', text: input }]
    setMessages(newMessages)
    setInput('')

    // Fetch API Url from environment file
    const API_BASE_URL = import.meta.env.VITE_API_URL;
    try {
      // Fire the JSON payload to FastAPI server
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, thread_id: "3" })
      })
      const data = await response.json()

      // Add Librarian's response to the screen
      setMessages([...newMessages, { role: 'librarian', text: data.response }])
    } catch (error) {
      console.error("Error communicating with API:", error)
    }
  }

  return (
    <div className="chat-container">
      <h1>📚 My Personal Librarian</h1>
      
      <div className="chat-box">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <strong>{msg.role === 'user' ? 'You' : 'Librarian'}: </strong>
            {msg.text}
          </div>
        ))}
      </div>

      <form onSubmit={sendMessage} className="input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me about your notes..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  )
}

export default App