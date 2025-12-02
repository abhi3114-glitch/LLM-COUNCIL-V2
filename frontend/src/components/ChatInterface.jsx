import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import Stage1 from './Stage1';
import Stage2 from './Stage2';
import Stage3 from './Stage3';
import './ChatInterface.css';

export default function ChatInterface({
  conversation,
  onSendMessage,
  isLoading,
}) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  if (!conversation) {
    return (
      <div className="chat-interface">
        <div className="empty-state">
          <h2>Welcome to LLM Council</h2>
          <p>Create a new conversation to get started</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-interface">
      <div className="messages-container">
        {conversation.messages.length === 0 ? (
          <div className="welcome-screen">
            <h2>LLM Council</h2>
            <p>Ask a question to convene the council of AI models. They will debate and synthesize the best possible answer for you.</p>
            <div className="suggestion-chips">
              <button onClick={() => setInput("Explain quantum computing like I'm 5")}>Explain quantum computing</button>
              <button onClick={() => setInput("Write a python script to scrape a website")}>Python scraping script</button>
              <button onClick={() => setInput("Is a tomato a fruit or a vegetable?")}>Tomato: Fruit or Veg?</button>
            </div>
          </div>
        ) : (
          conversation.messages.map((msg, index) => (
            <div key={index} className="message-wrapper">
              {msg.role === 'user' ? (
                <div className="message-user">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              ) : (
                <div className="message-assistant">
                  {/* Stage 1: Individual Responses */}
                  {(msg.loading?.stage1 || msg.stage1) && (
                    <div className="stage-container">
                      <div className="stage-header">Stage 1: Council Responses</div>
                      {msg.loading?.stage1 && (
                        <div className="loading-indicator">
                          <div className="spinner"></div>
                          <span>Gathering responses...</span>
                        </div>
                      )}
                      {msg.stage1 && <Stage1 responses={msg.stage1} />}
                    </div>
                  )}

                  {/* Stage 2: Debate/Ranking */}
                  {(msg.loading?.stage2 || msg.stage2) && (
                    <div className="stage-container">
                      <div className="stage-header">Stage 2: Peer Review</div>
                      {msg.loading?.stage2 && (
                        <div className="loading-indicator">
                          <div className="spinner"></div>
                          <span>Debating and ranking...</span>
                        </div>
                      )}
                      {msg.stage2 && (
                        <Stage2
                          rankings={msg.stage2}
                          labelToModel={msg.metadata?.label_to_model}
                          aggregateRankings={msg.metadata?.aggregate_rankings}
                        />
                      )}
                    </div>
                  )}

                  {/* Stage 3: Final Synthesis */}
                  {(msg.loading?.stage3 || msg.stage3) && (
                    <div className="stage-container">
                      <div className="stage-header">Stage 3: Chairman's Synthesis</div>
                      {msg.loading?.stage3 && (
                        <div className="loading-indicator">
                          <div className="spinner"></div>
                          <span>Synthesizing final answer...</span>
                        </div>
                      )}
                      {msg.stage3 && <Stage3 finalResponse={msg.stage3} />}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-form">
        <form className="input-wrapper" onSubmit={handleSubmit}>
          <textarea
            className="message-input"
            placeholder="Ask the council..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            rows={1}
            style={{ height: 'auto', minHeight: '24px' }}
            onInput={(e) => {
              e.target.style.height = 'auto';
              e.target.style.height = e.target.scrollHeight + 'px';
            }}
          />
          <button
            type="submit"
            className="send-button"
            disabled={!input.trim() || isLoading}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
