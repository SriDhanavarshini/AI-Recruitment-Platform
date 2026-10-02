export default function InterviewPage() {
  return (
    <div className="section-wrap">
      <div className="section-header">
        <h2>AI Interview</h2>
        <span className="status-badge">Technical</span>
      </div>
      <div className="card large-card">
        <p className="eyebrow">Question 2 of 5</p>
        <h3>Describe a production issue you resolved and how you traced the root cause.</h3>
        <textarea rows="7" placeholder="Provide your response here..."></textarea>
        <div className="cta-row">
          <button className="secondary-button">Pause</button>
          <button className="primary-button">Submit answer</button>
        </div>
      </div>
    </div>
  );
}
