import React from 'react';
import ReactMarkdown from 'react-markdown';

export default function Stage1({ responses }) {
  if (!responses || responses.length === 0) return null;

  return (
    <div className="cards-carousel">
      {responses.map((item, index) => (
        <div key={index} className="model-card">
          <div className="model-card-header">
            <div className="model-name">{item.model.split('/').pop()}</div>
          </div>
          <div className="model-response">
            <ReactMarkdown>{item.response}</ReactMarkdown>
          </div>
        </div>
      ))}
    </div>
  );
}
