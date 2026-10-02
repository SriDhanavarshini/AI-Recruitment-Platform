INSERT INTO users (email, full_name, role) VALUES
  ('hr@example.com', 'HR Manager', 'HR'),
  ('candidate@example.com', 'Candidate User', 'CANDIDATE');

INSERT INTO companies (name, domain, owner_id) VALUES
  ('Nova Labs', 'novalabs.com', 1);

INSERT INTO jobs (company_id, title, description, required_skills, required_experience, location, employment_type, status)
VALUES (
  1,
  'Senior Frontend Engineer',
  'Design user-facing experiences and collaborate with engineering teams to ship talent products.',
  '["React", "TypeScript", "UX", "Testing"]'::jsonb,
  '4+ years',
  'Remote',
  'FULL_TIME',
  'OPEN'
);

INSERT INTO questions (question, type, topic, difficulty, options, correct_answer, explanation, marks, approved)
VALUES (
  'Which of the following describes a primary advantage of an index in a relational database?',
  'APTITUDE',
  'Database Fundamentals',
  'MEDIUM',
  '["Faster reads on frequent queries", "Better encryption", "More storage capacity", "Automatic backups"]'::jsonb,
  'Faster reads on frequent queries',
  'Indexes speed up lookups for large tables by reducing scan work.',
  2,
  TRUE
);
