import { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

interface Message {
  role: 'user' | 'ai';
  content: string;
}

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const newMessages = [...messages, { role: 'user', content: input } as Message];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/chat', {
        message: input,
        warehouse_id: "WH-TRICHY-01" 
      });
      
      setMessages([...newMessages, { role: 'ai', content: response.data.reply }]);
    } catch (error) {
      console.error("API Error:", error);
      setMessages([...newMessages, { role: 'ai', content: 'System error: Unable to process supply chain constraints.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 p-4 font-sans">
      <header className="mb-4 text-center">
        <h1 className="text-2xl font-bold text-blue-900">SupplyChainGPT</h1>
        <p className="text-sm text-gray-500">Constraint-Aware Logistics Assistant</p>
      </header>

      <div className="flex-grow overflow-y-auto bg-white rounded-lg shadow-md p-4 mb-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`mb-4 flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`p-3 rounded-lg max-w-3xl ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800 border border-gray-200'}`}>
              
              {/* This is the Markdown Magic */}
              {msg.role === 'user' ? (
                msg.content
              ) : (
                <div className="prose prose-blue max-w-none text-sm md:text-base">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              )}

            </div>
          </div>
        ))}
        {loading && <div className="text-gray-400 italic mt-2">Analyzing constraints...</div>}
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask about inventory levels, routing constraints, or EOQ..."
          className="flex-grow p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button 
          onClick={sendMessage}
          disabled={loading}
          className="bg-blue-800 text-white px-6 py-3 rounded-lg hover:bg-blue-900 transition-colors disabled:bg-gray-400"
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default App;