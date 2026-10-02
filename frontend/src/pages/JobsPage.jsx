import JobCard from '../components/JobCard';

const jobs = [
  { id: 1, title: 'Senior Frontend Engineer', company: 'Nova Labs', location: 'Remote', skills: ['React', 'TypeScript', 'UX'], status: 'OPEN' },
  { id: 2, title: 'Backend Engineer', company: 'Northstar', location: 'Remote', skills: ['FastAPI', 'PostgreSQL', 'Python'], status: 'OPEN' },
  { id: 3, title: 'Machine Learning Engineer', company: 'Signal Valley', location: 'New York', skills: ['Python', 'ML', 'Systems'], status: 'OPEN' },
];

export default function JobsPage() {
  return (
    <div className="section-wrap">
      <div className="section-header">
        <h2>Available jobs</h2>
      </div>
      <div className="grid-3">
        {jobs.map((job) => (
          <JobCard key={job.id} job={job} />
        ))}
      </div>
    </div>
  );
}
