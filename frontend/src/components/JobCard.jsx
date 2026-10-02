import { Link } from 'react-router-dom';

export default function JobCard({ job }) {
  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h3>{job.title}</h3>
          <p>{job.company}</p>
        </div>
        <span className="status-badge">{job.status || 'OPEN'}</span>
      </div>
      <p>{job.location}</p>
      <div className="chip-row">
        {(job.skills || ['React', 'Python', 'Product']).map((skill) => (
          <span className="chip" key={skill}>{skill}</span>
        ))}
      </div>
      <div className="cta-row">
        <Link to={`/jobs/${job.id || 1}`}>View details</Link>
      </div>
    </div>
  );
}
