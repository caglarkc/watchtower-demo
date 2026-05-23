-- Phase 2 demo schema + pg_audit-style logging via application triggers (simulated)
CREATE TABLE IF NOT EXISTS payroll (
    id SERIAL PRIMARY KEY,
    employee TEXT NOT NULL,
    salary NUMERIC(12, 2)
);

CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT
);

INSERT INTO payroll (employee, salary) VALUES ('alice', 50000), ('bob', 52000)
ON CONFLICT DO NOTHING;

INSERT INTO customers (name, email) VALUES ('acme', 'a@acme.corp')
ON CONFLICT DO NOTHING;
