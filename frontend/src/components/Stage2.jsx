import React from 'react';

export default function Stage2({ rankings, labelToModel, aggregateRankings }) {
  if (!aggregateRankings || aggregateRankings.length === 0) return null;

  return (
    <div className="ranking-container">
      {aggregateRankings.map((item, index) => (
        <div key={index} className="ranking-item">
          <div className="rank-badge">{index + 1}</div>
          <div className="rank-model">
            {item.model.split('/').pop()}
          </div>
          <div className="rank-score">
            Avg Rank: {item.average_rank}
          </div>
        </div>
      ))}
    </div>
  );
}
