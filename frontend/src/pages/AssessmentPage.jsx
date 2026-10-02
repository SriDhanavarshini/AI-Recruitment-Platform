export default function AssessmentPage() {
  return (
    <div className="section-wrap">
      <div className="section-header">
        <h2>Assessment</h2>
        <span className="status-badge">Timer: 42:17</span>
      </div>
      <div className="assessment-layout">
        <div className="card large-card">
          <p className="eyebrow">Section 2 / 3</p>
          <h3>What is the main advantage of indexing in a relational database?</h3>
          <div className="options-list">
            <label><input type="radio" name="answer" /> Faster data lookup for frequent queries</label>
            <label><input type="radio" name="answer" /> More secure storage</label>
            <label><input type="radio" name="answer" /> Automatic backups</label>
            <label><input type="radio" name="answer" /> Data encryption</label>
          </div>
          <div className="cta-row">
            <button className="secondary-button">Previous</button>
            <button className="primary-button">Next</button>
          </div>
        </div>
        <div className="side-panel card">
          <h4>Navigation</h4>
          <div className="question-grid">
            {[1,2,3,4,5,6].map((n) => (
              <span key={n} className={n === 2 ? 'question-pill active' : 'question-pill'}>{n}</span>
            ))}
          </div>
          <p className="muted">Camera preview active</p>
          <div className="camera-box">Camera</div>
        </div>
      </div>
    </div>
  );
}
