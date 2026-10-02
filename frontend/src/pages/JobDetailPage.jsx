import { useParams } from 'react-router-dom';

export default function JobDetailPage() {
  const { id } = useParams();

  return (
    <div className="section-wrap">
      <div className="section-header">
        <h2>Senior Frontend Engineer</h2>
        <span className="status-badge">OPEN</span>
      </div>
      <div className="card">
        <p><strong>Company:</strong> Nova Labs</p>
        <p><strong>Location:</strong> Remote</p>
        <p><strong>Experience:</strong> 4+ years</p>
        <p><strong>Skills:</strong> React, TypeScript, UX, Testing</p>
        <p>
          Lead product experiences for a platform that helps hiring teams identify strong technical and cultural signals at scale.
          Design, prototype, and close the loop between product, engineering, and recruitment stakeholders.
        </p>
        <button className="primary-button">Apply for this role</button>
      </div>
      <p className="muted">Job ID: {id}</p>
    </div>
  );
}
