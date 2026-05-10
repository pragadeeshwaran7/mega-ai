-- Initial schema setup
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    query TEXT,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    full_context JSONB
);

CREATE TABLE IF NOT EXISTS execution_logs (
    id SERIAL PRIMARY KEY,
    job_id TEXT REFERENCES jobs(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    agent_id TEXT,
    event_type TEXT,
    content JSONB,
    latency FLOAT,
    token_count INTEGER
);

CREATE TABLE IF NOT EXISTS eval_runs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    test_case_id TEXT,
    category TEXT,
    scores JSONB,
    total_score FLOAT,
    job_id TEXT REFERENCES jobs(id)
);

CREATE TABLE IF NOT EXISTS prompt_versions (
    id SERIAL PRIMARY KEY,
    agent_role TEXT,
    content TEXT,
    version INTEGER,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    proposed_by_eval_run_id INTEGER,
    justification TEXT,
    status TEXT DEFAULT 'pending'
);
