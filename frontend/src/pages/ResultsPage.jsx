export default function ResultsPage() {
  return (
    <div className="section-wrap">
      <div className="section-header">
        <h2>Candidate results</h2>
      </div>
      <div className="overview-grid">
        <div className="stat-card"><span>Aptitude</span><strong>82%</strong></div>
        <div className="stat-card"><span>Technical</span><strong>88%</strong></div>
        <div className="stat-card"><span>Coding</span><strong>91%</strong></div>
        <div className="stat-card"><span>Overall</span><strong>87%</strong></div>
      </div>
      <div className="card">
        <h3>Interview summary</h3>
        <p>Strong technical reasoning and communication. One opportunity is to provide more concrete examples of architecture trade-offs.</p>
      </div>
    </div>
  );
}
