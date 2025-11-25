import { useState, useRef, useEffect, useCallback } from 'react';
import { useLanguage } from '../i18n/LanguageContext';
import { sendChatMessage, getQuickQuestions } from '../services/api';

// Chat message component
const ChatMessage = ({ message, isUser, timestamp }) => {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-green-600 text-white rounded-br-md'
            : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-bl-md'
        }`}
      >
        {/* Render markdown-like formatting */}
        <div className="text-sm whitespace-pre-wrap">
          {message.split('\n').map((line, i) => {
            // Bold text
            if (line.startsWith('**') && line.includes(':**')) {
              const parts = line.split(':**');
              return (
                <p key={i} className="mb-1">
                  <strong className={isUser ? 'text-green-100' : 'text-green-700 dark:text-green-400'}>
                    {parts[0].replace(/\*\*/g, '')}:
                  </strong>
                  {parts[1]}
                </p>
              );
            }
            // Bullet points
            if (line.startsWith('•') || line.startsWith('-')) {
              return (
                <p key={i} className="ml-2 mb-1">
                  {line}
                </p>
              );
            }
            // Warning/Emergency
            if (line.includes('⚠️')) {
              return (
                <p key={i} className="font-bold text-yellow-300 dark:text-yellow-400 mb-2">
                  {line}
                </p>
              );
            }
            return line ? <p key={i} className="mb-1">{line}</p> : <br key={i} />;
          })}
        </div>
        <p className={`text-xs mt-2 ${isUser ? 'text-green-200' : 'text-gray-400'}`}>
          {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  );
};

// Typing indicator
const TypingIndicator = () => (
  <div className="flex justify-start mb-4">
    <div className="bg-gray-100 dark:bg-gray-700 rounded-2xl rounded-bl-md px-4 py-3">
      <div className="flex space-x-1">
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
      </div>
    </div>
  </div>
);

// Quick question button
const QuickQuestion = ({ question, onClick }) => (
  <button
    onClick={() => onClick(question.text)}
    className="flex items-center gap-2 px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-full text-sm text-gray-700 dark:text-gray-300 hover:bg-green-50 dark:hover:bg-green-900/30 hover:border-green-300 dark:hover:border-green-600 transition-colors whitespace-nowrap"
  >
    <span>{question.icon}</span>
    <span className="truncate max-w-[200px]">{question.text}</span>
  </button>
);

// Suggestion chip
const SuggestionChip = ({ text, onClick }) => (
  <button
    onClick={() => onClick(text)}
    className="px-3 py-1.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full text-xs hover:bg-green-200 dark:hover:bg-green-900/50 transition-colors"
  >
    {text}
  </button>
);

export default function ChatAssistant() {
  const { t, language } = useLanguage();
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [quickQuestions, setQuickQuestions] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Load quick questions
  useEffect(() => {
    const loadQuickQuestions = async () => {
      try {
        const data = await getQuickQuestions(language);
        setQuickQuestions(data.questions || []);
      } catch (error) {
        console.error('Failed to load quick questions:', error);
        // Fallback questions
        setQuickQuestions([
          { id: 'q1', text: t('chat.quickQ1') || 'What is late blight?', icon: '🍅' },
          { id: 'q2', text: t('chat.quickQ2') || 'How to prevent diseases?', icon: '🛡️' },
          { id: 'q3', text: t('chat.quickQ3') || 'Organic pest control', icon: '🌿' },
        ]);
      }
    };
    loadQuickQuestions();
  }, [language, t]);

  // Send initial greeting
  useEffect(() => {
    const greeting = {
      id: Date.now(),
      text: t('chat.greeting'),
      isUser: false,
      timestamp: new Date().toISOString(),
    };
    setMessages([greeting]);
  }, [language]); // Reset on language change

  // Send message handler
  const sendMessage = async (text) => {
    if (!text.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: text.trim(),
      isUser: true,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);
    setSuggestions([]);

    try {
      const response = await sendChatMessage(text.trim(), language, sessionId);
      
      const assistantMessage = {
        id: Date.now() + 1,
        text: response.response,
        isUser: false,
        timestamp: response.timestamp || new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
      setSuggestions(response.suggestions || []);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: t('chat.error') || 'Sorry, I encountered an error. Please try again.',
        isUser: false,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  // Handle form submit
  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputText);
  };

  // Handle quick question click
  const handleQuickQuestion = (text) => {
    sendMessage(text);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm px-4 py-3 flex items-center gap-3">
        <div className="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center">
          <span className="text-white text-xl">🤖</span>
        </div>
        <div>
          <h1 className="font-semibold text-gray-800 dark:text-white">
            {t('chat.title')}
          </h1>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {t('chat.subtitle')}
          </p>
        </div>
        <div className="ml-auto">
          <span className="inline-flex items-center gap-1 text-xs text-green-600 dark:text-green-400">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            {t('chat.online')}
          </span>
        </div>
      </div>

      {/* Quick Questions (show only when no messages or just greeting) */}
      {messages.length <= 1 && (
        <div className="px-4 py-3 bg-white dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
            {t('chat.quickQuestions')}
          </p>
          <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
            {quickQuestions.map((q) => (
              <QuickQuestion key={q.id} question={q} onClick={handleQuickQuestion} />
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {messages.map((msg) => (
          <ChatMessage
            key={msg.id}
            message={msg.text}
            isUser={msg.isUser}
            timestamp={msg.timestamp}
          />
        ))}
        
        {isLoading && <TypingIndicator />}
        
        {/* Suggestions */}
        {suggestions.length > 0 && !isLoading && (
          <div className="flex flex-wrap gap-2 mt-2 mb-4">
            {suggestions.map((suggestion, idx) => (
              <SuggestionChip
                key={idx}
                text={suggestion}
                onClick={handleQuickQuestion}
              />
            ))}
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white dark:bg-gray-800 border-t border-gray-100 dark:border-gray-700 px-4 py-3">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={t('chat.placeholder')}
            className="flex-1 px-4 py-3 bg-gray-100 dark:bg-gray-700 rounded-full text-gray-800 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!inputText.trim() || isLoading}
            className="px-4 py-3 bg-green-600 text-white rounded-full hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
            </svg>
          </button>
        </form>
        <p className="text-xs text-center text-gray-400 mt-2">
          {t('chat.disclaimer')}
        </p>
      </div>
    </div>
  );
}
