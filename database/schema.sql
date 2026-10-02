CREATE TYPE user_role AS ENUM ('HR', 'CANDIDATE');
CREATE TYPE employment_type AS ENUM ('FULL_TIME', 'PART_TIME', 'INTERNSHIP', 'CONTRACT');
CREATE TYPE job_status AS ENUM ('OPEN', 'CLOSED');
CREATE TYPE application_status AS ENUM (
  'APPLIED',
  'ATS_SHORTLISTED',
  'ASSESSMENT_PENDING',
  'ASSESSMENT_PASSED',
  'AI_INTERVIEW_PENDING',
  'AI_INTERVIEW_COMPLETED',
  'SELECTED',
  'NOT_SELECTED'
);
CREATE TYPE question_type AS ENUM ('APTITUDE', 'TECHNICAL_MCQ', 'CODING');
CREATE TYPE difficulty AS ENUM ('EASY', 'MEDIUM', 'HARD');
CREATE TYPE proctoring_event_type AS ENUM (
  'FACE_NOT_DETECTED',
  'MULTIPLE_FACES',
  'TAB_SWITCH',
  'FULLSCREEN_EXIT',
  'CAMERA_DISCONNECTED'
);

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  full_name VARCHAR(255) NOT NULL,
  role user_role NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE companies (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  domain VARCHAR(255),
  owner_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE jobs (
  id SERIAL PRIMARY KEY,
  company_id INT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  required_skills JSONB DEFAULT '[]'::jsonb,
  required_experience VARCHAR(255),
  location VARCHAR(255),
  employment_type employment_type NOT NULL,
  status job_status NOT NULL DEFAULT 'OPEN',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE resumes (
  id SERIAL PRIMARY KEY,
  candidate_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  file_url VARCHAR(500) NOT NULL,
  storage_path VARCHAR(500) NOT NULL,
  extracted_skills JSONB DEFAULT '[]'::jsonb,
  extracted_keywords JSONB DEFAULT '[]'::jsonb,
  extracted_experience TEXT,
  education TEXT,
  projects TEXT,
  certifications TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE applications (
  id SERIAL PRIMARY KEY,
  candidate_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  job_id INT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  resume_id INT NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
  status application_status NOT NULL DEFAULT 'APPLIED',
  ats_score FLOAT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(candidate_id, job_id)
);

CREATE TABLE ats_results (
  id SERIAL PRIMARY KEY,
  application_id INT NOT NULL UNIQUE REFERENCES applications(id) ON DELETE CASCADE,
  score FLOAT NOT NULL,
  matching_skills JSONB DEFAULT '[]'::jsonb,
  missing_skills JSONB DEFAULT '[]'::jsonb,
  relevant_experience TEXT,
  extracted_resume_data JSONB DEFAULT '{}'::jsonb,
  explanation TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE questions (
  id SERIAL PRIMARY KEY,
  question TEXT NOT NULL,
  type question_type NOT NULL,
  topic VARCHAR(255) NOT NULL,
  difficulty difficulty NOT NULL,
  options JSONB DEFAULT '[]'::jsonb,
  correct_answer VARCHAR(255),
  explanation TEXT,
  marks INT DEFAULT 1,
  approved BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE assessments (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  duration_minutes INT NOT NULL DEFAULT 60,
  passing_score FLOAT NOT NULL DEFAULT 60,
  marks INT NOT NULL DEFAULT 100,
  difficulty difficulty DEFAULT 'MEDIUM',
  number_of_questions INT NOT NULL DEFAULT 40,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE assessment_attempts (
  id SERIAL PRIMARY KEY,
  assessment_id INT NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
  candidate_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status VARCHAR(50) DEFAULT 'IN_PROGRESS',
  score FLOAT DEFAULT 0,
  percentage FLOAT DEFAULT 0,
  pass_status BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  submitted_at TIMESTAMPTZ
);

CREATE TABLE answers (
  id SERIAL PRIMARY KEY,
  attempt_id INT NOT NULL REFERENCES assessment_attempts(id) ON DELETE CASCADE,
  question_id INT NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
  selected_answer VARCHAR(255),
  is_correct BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE coding_problems (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  statement TEXT NOT NULL,
  input_description TEXT,
  output_description TEXT,
  constraints TEXT,
  examples JSONB DEFAULT '[]'::jsonb,
  visible_test_cases JSONB DEFAULT '[]'::jsonb,
  hidden_test_cases JSONB DEFAULT '[]'::jsonb,
  supported_languages JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE coding_submissions (
  id SERIAL PRIMARY KEY,
  candidate_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  problem_id INT NOT NULL REFERENCES coding_problems(id) ON DELETE CASCADE,
  language VARCHAR(50) NOT NULL,
  code TEXT NOT NULL,
  passed_tests INT DEFAULT 0,
  failed_tests INT DEFAULT 0,
  execution_time_ms INT DEFAULT 0,
  memory_kb INT DEFAULT 0,
  score FLOAT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE proctoring_events (
  id SERIAL PRIMARY KEY,
  assessment_attempt_id INT NOT NULL REFERENCES assessment_attempts(id) ON DELETE CASCADE,
  event_type proctoring_event_type NOT NULL,
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE ai_interviews (
  id SERIAL PRIMARY KEY,
  candidate_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  category VARCHAR(50) DEFAULT 'TECHNICAL',
  status VARCHAR(50) DEFAULT 'PENDING',
  max_questions INT DEFAULT 5,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

CREATE TABLE interview_questions (
  id SERIAL PRIMARY KEY,
  interview_id INT NOT NULL REFERENCES ai_interviews(id) ON DELETE CASCADE,
  question TEXT NOT NULL,
  category VARCHAR(50) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE interview_answers (
  id SERIAL PRIMARY KEY,
  interview_id INT NOT NULL REFERENCES ai_interviews(id) ON DELETE CASCADE,
  question_id INT NOT NULL REFERENCES interview_questions(id) ON DELETE CASCADE,
  answer TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE interview_reports (
  id SERIAL PRIMARY KEY,
  interview_id INT NOT NULL UNIQUE REFERENCES ai_interviews(id) ON DELETE CASCADE,
  technical_score FLOAT DEFAULT 0,
  domain_score FLOAT DEFAULT 0,
  communication_score FLOAT DEFAULT 0,
  relevance_score FLOAT DEFAULT 0,
  overall_score FLOAT DEFAULT 0,
  strengths JSONB DEFAULT '[]'::jsonb,
  areas_for_improvement JSONB DEFAULT '[]'::jsonb,
  question_evaluations JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE candidate_status_history (
  id SERIAL PRIMARY KEY,
  candidate_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  application_id INT NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
  status VARCHAR(50) NOT NULL,
  note TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE reapplication_restrictions (
  id SERIAL PRIMARY KEY,
  candidate_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  job_id INT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  rejection_date DATE NOT NULL,
  eligible_reapply_date DATE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(candidate_id, job_id)
);

CREATE INDEX idx_jobs_company_id ON jobs(company_id);
CREATE INDEX idx_applications_candidate_id ON applications(candidate_id);
CREATE INDEX idx_applications_job_id ON applications(job_id);
CREATE INDEX idx_resumes_candidate_id ON resumes(candidate_id);
CREATE INDEX idx_questions_type ON questions(type);
CREATE INDEX idx_assessment_attempts_candidate_id ON assessment_attempts(candidate_id);
CREATE INDEX idx_proctoring_events_attempt_id ON proctoring_events(assessment_attempt_id);
