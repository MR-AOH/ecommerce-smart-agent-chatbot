// Import React and its hooks for component state and lifecycle management
// Import Font Awesome icons for the chat interface

import { useState, useEffect, useRef } from 'react'
import { FaRobot, FaPaperPlane, FaTimes, FaCommentDots } from 'react-icons/fa'

// ChatWidget Component
const ChatWidget = () => {
  // State to track if chat window is open or closed
  const [isOpen, setIsOpen] = useState(false)
  // State to store all chat messages (array of message objects)
  const [messages, setMessages] = useState([])
  // State to track current input field value
  const [inputValue, setInputValue] = useState('')
  // State to store conversation thread ID (null for new conversations)
  const [threadId, setThreadId] = useState(null)
  // Ref to reference the bottom of messages container for auto-scrolling
  const messagesEndRef = useRef(null)

  // Effect hook: Show initial greeting when chat is first opened
  useEffect(() => {
    // Only run if chat is open AND no messages exist yet
    if (isOpen && messages.length === 0) {
      // Create initial greeting message
      const initialMessages = [
        {
          text: "Hello! I'm your shopping assistant. How can I help you today?", // Greeting text
          isAgent: true // Flag to indicate this is from the AI agent
        }
      ]
      // Add greeting to messages state
      setMessages(initialMessages)
    }
  }, [isOpen, messages.length]) // Dependencies: re-run when isOpen or message count changes

  // Effect hook: Auto-scroll to bottom when new messages are added
  useEffect(() => {
    // Scroll the messages container to bottom smoothly
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages]) // Dependency: re-run whenever messages array changes

  // Function to toggle chat window open/closed
  const toggleChat = () => {
    // Flip the current isOpen state (true becomes false, false becomes true)
    setIsOpen(!isOpen)
  }

  // Function to handle changes in the input field
  const handleInputChange = (e) => {
    // Update inputValue state with current text field value
    setInputValue(e.target.value)
  }

  // Log messages to console for debugging purposes
  console.log(messages)
  
  // Function to send user message and get AI response
  const handleSendMessage = async (e) => {
    // Prevent default form submission behavior (page refresh)
    e.preventDefault()
    // Log user input for debugging
    console.log(inputValue)

    // Create message object for user's input
    const message = {
      text: inputValue,  // User's typed message
      isAgent: false,    // Flag indicating this is from user, not AI
    }

    // Add user message to messages array using spread operator
    setMessages(prevMessages => [...prevMessages, message])
    // Clear input field immediately after sending
    setInputValue("")

    // Determine API endpoint: use existing thread if available, otherwise create new
    const endpoint = threadId ? `http://localhost:8000/chat/${threadId}` : 'http://localhost:8000/chat'

    try {
      // Make HTTP POST request to backend API
      const response = await fetch(endpoint, {
        method: 'POST', // HTTP method
        headers: {
          'Content-Type': 'application/json', // Tell server we're sending JSON
        },
        body: JSON.stringify({
          message: inputValue // Send user's message in request body
        }),
      })

      // Check if response status indicates success (200-299 range)
      if (!response.ok) {
        // Throw error if response status indicates failure
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      // Parse JSON response from server
      const data = await response.json()
      // Log successful response for debugging
      console.log('Success:', data)
      
      // Create message object for AI agent's response
      const agentResponse = {
        text: data.response,    // AI's response text
        isAgent: true,          // Flag indicating this is from AI agent
        threadId: data.threadId // Thread ID for conversation continuity
      }
      
      // Add AI response to messages array
      setMessages(prevMessages => [...prevMessages, agentResponse])
      // Update thread ID for future messages in this conversation
      setThreadId(data.threadId)
      // Log updated messages for debugging
      console.log(messages)
    } catch (error) {
      // Log any errors that occur during API call
      console.error('Error:', error)
    }
  }


  return (
    <div className={`fixed bottom-6 right-6 z-50 transition-all duration-300 ease-in-out ${isOpen ? 'w-96 h-[500px]' : 'w-16 h-16'}`}>
      {isOpen ? (
        <div className="bg-white rounded-2xl shadow-2xl border border-gray-100 flex flex-col h-full overflow-hidden backdrop-blur-xl">
          <div className="bg-gradient-to-r from-purple-600 via-pink-500 to-red-500 text-white p-4 flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                <FaRobot className="text-sm" />
              </div>
              <h3 className="font-semibold">AI Shop Assistant</h3>
            </div>
            <button onClick={toggleChat} className="text-white/80 hover:text-white transition-colors">
              <FaTimes />
            </button>
          </div>

          <div className="flex-1 p-4 overflow-y-auto space-y-3">
            {messages.map((message, index) => (
              <div key={index} className={`flex ${message.isAgent ? 'justify-start' : 'justify-end'}`}>
                <div className={`max-w-[80%] px-4 py-2 rounded-2xl text-sm ${
                  message.isAgent 
                    ? 'bg-gray-100 text-gray-800 rounded-bl-md' 
                    : 'bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-br-md'
                }`}>
                  {message.text}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          <form className="p-4 border-t border-gray-100 flex gap-2" onSubmit={handleSendMessage}>
            <input
              type="text"
              className="flex-1 px-4 py-2 border border-gray-200 rounded-full outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Type your message..."
              value={inputValue}
              onChange={handleInputChange}
            />
            <button
              type="submit"
              disabled={inputValue.trim() === ''}
              className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg transition-all"
            >
              <FaPaperPlane className="text-sm" />
            </button>
          </form>
        </div>
      ) : (
        <button
          onClick={toggleChat}
          className="w-16 h-16 bg-gradient-to-r from-purple-600 via-pink-500 to-red-500 text-white rounded-full shadow-2xl hover:shadow-purple-500/25 hover:scale-110 transition-all duration-300 flex items-center justify-center group"
        >
          <FaCommentDots className="text-xl group-hover:animate-pulse" />
        </button>
      )}
    </div>
  )
}

// Export component as default export
export default ChatWidget