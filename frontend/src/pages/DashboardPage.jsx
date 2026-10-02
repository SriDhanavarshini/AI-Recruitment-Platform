import JobCard from '../components/JobCard';

const jobs = [
  { id: 1, title: 'Senior Frontend Engineer', company: 'Nova Labs', location: 'Remote', skills: ['React', 'TypeScript', 'UX'], status: 'OPEN' },
  { id: 2, title: 'AI Product Analyst', company: 'Signal Valley', location: 'Berlin', skills: ['Python', 'AI', 'SQL'], status: 'OPEN' },
  { id: 3, title: 'Data Engineer', company: 'Northstar', location: 'London', skills: ['ETL', 'Snowflake', 'Python'], status: 'CLOSED' },
];

export default function DashboardPage() {
  return (
    <div>
      <section className="overview-grid">
        <div className="stat-card"><span>Open Jobs</span><strong>24</strong></div>
        <div className="stat-card"><span>Applicants</span><strong>148</strong></div>
        <div className="stat-card"><span>Shortlisted</span><strong>31</strong></div>
        <div className="stat-card"><span>AI Interviewed</span><strong>12</strong></div>
      </section>

      <section className="section-wrap">
        <div className="section-header">
          <h2>Featured opportunities</h2>
        </div>
        <div className="grid-3">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      </section>
    </div>
  );
}
