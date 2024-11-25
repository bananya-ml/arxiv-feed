import { useState } from 'react';
import { Send, User, Bot } from 'lucide-react';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

interface ChatInterfaceProps {
  paper: any;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ paper }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: `Hi! I'm your research assistant. Ask me anything about "${paper.title}"`,
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate bot response (replace with actual API call)
    setTimeout(() => {
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "I'm analyzing the paper and will provide a response shortly...",
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);
      setIsTyping(false);
    }, 1000);
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-neutral-950 rounded-lg">
      <div className="p-4 border-b border-gray-200 dark:border-neutral-800">
        <h3 className="font-semibold text-lg">Chat with Paper</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Ask questions about the research paper
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex items-start gap-3 ${
              message.sender === 'user' ? 'flex-row-reverse' : ''
            }`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center
              ${message.sender === 'user' 
                ? 'bg-cyan-100 dark:bg-cyan-900' 
                : 'bg-gray-100 dark:bg-gray-800'
              }`}
            >
              {message.sender === 'user' 
                ? <User className="w-5 h-5 text-cyan-600 dark:text-cyan-400" />
                : <Bot className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              }
            </div>
            <div
              className={`max-w-[80%] px-4 py-2 rounded-lg ${
                message.sender === 'user'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
              }`}
            >
              <p className="text-sm">{message.content}</p>
              <span className="text-xs opacity-70 mt-1 block">
                {message.timestamp.toLocaleTimeString([], { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}
              </span>
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
            <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" />
            <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.2s' }} />
            <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.4s' }} />
          </div>
        )}
      </div>
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200 dark:border-neutral-800">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask a question about the paper..."
            className="flex-1 p-2 rounded-lg border border-gray-300 dark:border-neutral-700 
                     bg-white dark:bg-neutral-900 text-gray-900 dark:text-gray-100
                     focus:outline-none focus:ring-2 focus:ring-cyan-500 dark:focus:ring-cyan-600"
          />
          <button
            type="submit"
            disabled={!inputValue.trim()}
            className={`p-2 rounded-lg ${
              inputValue.trim()
                ? 'bg-cyan-600 hover:bg-cyan-700 text-white'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-400'
            } transition-colors duration-200`}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatInterface;