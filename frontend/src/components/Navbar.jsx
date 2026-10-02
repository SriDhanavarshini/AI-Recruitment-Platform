import { Link } from 'react-router-dom';

export default function Navbar() {
  return (
    <header className="navbar">
      <div className="brand-group">
        <div className="brand-mark">AI</div>
        <div>
          <strong>Recruitment Platform</strong>
          <small>Talent intelligence suite</small>
        </div>
      </div>
      <nav className="nav-links">
        <Link to="/">Dashboard</Link>
        <Link to="/jobs">Jobs</Link>
        <Link to="/applications">Applications</Link>
        <Link to="/results">Results</Link>
      </nav>
    </header>
  );
}
