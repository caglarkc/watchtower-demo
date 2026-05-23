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

INSERT INTO payroll (employee, salary)
SELECT 'alice', 50000 WHERE NOT EXISTS (SELECT 1 FROM payroll WHERE employee = 'alice');

INSERT INTO customers (name, email)
SELECT 'acme', 'a@acme.corp' WHERE NOT EXISTS (SELECT 1 FROM customers WHERE name = 'acme');
