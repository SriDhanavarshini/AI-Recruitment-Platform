export default function ApplicationsPage() {
  const rows = [
    { candidate: 'Aisha Khan', job: 'Data Engineer', status: 'ATS_SHORTLISTED', score: 89 },
    { candidate: 'Marcus Lee', job: 'AI Product Analyst', status: 'ASSESSMENT_PASSED', score: 76 },
    { candidate: 'Sara Gomez', job: 'Frontend Engineer', status: 'AI_INTERVIEW_COMPLETED', score: 82 },
  ];

  return (
    <div className="section-wrap">
      <div className="section-header">
        <h2>Applications pipeline</h2>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Candidate</th>
              <th>Role</th>
              <th>ATS score</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.candidate}>
                <td>{row.candidate}</td>
                <td>{row.job}</td>
                <td>{row.score}</td>
                <td><span className="status-badge">{row.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
