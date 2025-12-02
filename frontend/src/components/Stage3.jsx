import React from 'react';
import ReactMarkdown from 'react-markdown';

export default function Stage3({ finalResponse }) {
  if (!finalResponse) return null;

  return (
    <div className="hero-card">
      <div className="hero-header">
        <div className="chairman-badge">Chairman's Verdict</div>
      </div>
      <div className="hero-content">
        <ReactMarkdown>{finalResponse.response}</ReactMarkdown>
      </div>
    </div>
  );
}
