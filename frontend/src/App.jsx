import { Link, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import DashboardPage from './pages/DashboardPage';
import JobsPage from './pages/JobsPage';
import JobDetailPage from './pages/JobDetailPage';
import ApplicationsPage from './pages/ApplicationsPage';
import AssessmentPage from './pages/AssessmentPage';
import InterviewPage from './pages/InterviewPage';
import ResultsPage from './pages/ResultsPage';

function App() {
  return (
    <div className="app-shell">
      <Navbar />
      <div className="content-shell">
        <Sidebar />
        <main className="page-content">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/jobs" element={<JobsPage />} />
            <Route path="/jobs/:id" element={<JobDetailPage />} />
            <Route path="/applications" element={<ApplicationsPage />} />
            <Route path="/assessment/:id" element={<AssessmentPage />} />
            <Route path="/interview/:id" element={<InterviewPage />} />
            <Route path="/results" element={<ResultsPage />} />
            <Route path="*" element={<div className="empty-state"><h2>Page not found</h2><Link to="/">Return home</Link></div>} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;
