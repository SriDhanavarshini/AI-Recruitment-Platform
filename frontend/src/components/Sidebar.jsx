import { NavLink } from 'react-router-dom';

const items = [
  { to: '/', label: 'Overview' },
  { to: '/jobs', label: 'Open Jobs' },
  { to: '/applications', label: 'Applications' },
  { to: '/assessment/1', label: 'Assessment' },
  { to: '/interview/1', label: 'Interview' },
  { to: '/results', label: 'Reports' },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <h3>Navigation</h3>
      {items.map((item) => (
        <NavLink key={item.to} to={item.to} className={({ isActive }) => (isActive ? 'side-link active' : 'side-link')}>
          {item.label}
        </NavLink>
      ))}
    </aside>
  );
}
