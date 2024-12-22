# Database Design

## Overview
This document details the database design of the Patient Management System, including schema design, relationships, and optimization strategies.

## Database Schema

### Core Tables

#### Patients
```sql
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    patient_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(1) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patient_search ON patients(
    patient_number, 
    last_name, 
    first_name, 
    date_of_birth
);
```

#### Clinical Data
```sql
CREATE TABLE vital_signs (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id),
    recorded_at TIMESTAMP NOT NULL,
    blood_pressure_systolic INTEGER,
    blood_pressure_diastolic INTEGER,
    heart_rate INTEGER,
    respiratory_rate INTEGER,
    temperature DECIMAL(4,1),
    spo2 INTEGER,
    recorded_by INTEGER REFERENCES users(id)
);

CREATE INDEX idx_vitals_patient_date ON vital_signs(
    patient_id, 
    recorded_at DESC
);
```

#### Laboratory Results
```sql
CREATE TABLE lab_results (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id),
    test_type VARCHAR(50) NOT NULL,
    result_value VARCHAR(50) NOT NULL,
    unit VARCHAR(20),
    reference_range VARCHAR(50),
    is_abnormal BOOLEAN DEFAULT FALSE,
    performed_at TIMESTAMP NOT NULL,
    reported_at TIMESTAMP NOT NULL,
    verified_by INTEGER REFERENCES users(id)
);

CREATE INDEX idx_lab_results_patient ON lab_results(
    patient_id, 
    test_type, 
    performed_at DESC
);
```

## Relationships

### Entity Relationship Diagram
```
[Patients] 1─┬─∞ [Vital Signs]
            ├─∞ [Lab Results]
            ├─∞ [Medications]
            └─∞ [Clinical Notes]

[Users] 1─┬─∞ [Clinical Notes]
         ├─∞ [Lab Results]
         └─∞ [Vital Signs]
```

### Foreign Key Constraints
```sql
-- Example constraints
ALTER TABLE vital_signs
    ADD CONSTRAINT fk_patient
    FOREIGN KEY (patient_id)
    REFERENCES patients(id)
    ON DELETE RESTRICT;

ALTER TABLE lab_results
    ADD CONSTRAINT fk_verified_by
    FOREIGN KEY (verified_by)
    REFERENCES users(id)
    ON DELETE SET NULL;
```

## Optimization

### Indexes
```sql
-- Patient search optimization
CREATE INDEX idx_patient_name ON patients(last_name, first_name);
CREATE INDEX idx_patient_dob ON patients(date_of_birth);

-- Clinical data retrieval optimization
CREATE INDEX idx_vitals_date ON vital_signs(recorded_at);
CREATE INDEX idx_labs_date ON lab_results(performed_at);
```

### Partitioning
```sql
-- Partition lab results by year
CREATE TABLE lab_results_partition OF lab_results
    PARTITION BY RANGE (performed_at);

CREATE TABLE lab_results_2023 
    PARTITION OF lab_results_partition
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');
```

## Data Types

### Custom Types
```sql
-- Enumerated types
CREATE TYPE gender_type AS ENUM ('M', 'F', 'O');
CREATE TYPE blood_type AS ENUM ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-');

-- Composite types
CREATE TYPE address_type AS (
    street TEXT,
    city VARCHAR(100),
    state VARCHAR(2),
    zip VARCHAR(10)
);
```

## Views

### Common Views
```sql
-- Patient summary view
CREATE VIEW patient_summary AS
SELECT 
    p.id,
    p.patient_number,
    p.first_name,
    p.last_name,
    p.date_of_birth,
    COUNT(v.id) as vital_signs_count,
    COUNT(l.id) as lab_results_count
FROM patients p
LEFT JOIN vital_signs v ON p.id = v.patient_id
LEFT JOIN lab_results l ON p.id = l.patient_id
GROUP BY p.id;

-- Recent lab results view
CREATE VIEW recent_labs AS
SELECT 
    patient_id,
    test_type,
    result_value,
    performed_at
FROM lab_results
WHERE performed_at >= CURRENT_DATE - INTERVAL '30 days';
```

## Security

### Row-Level Security
```sql
-- Enable RLS on patients table
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;

-- Create access policy
CREATE POLICY patient_access_policy ON patients
    USING (department_id IN (
        SELECT department_id 
        FROM user_departments 
        WHERE user_id = current_user_id()
    ));
```

### Data Encryption
```sql
-- Encrypted columns
CREATE EXTENSION pgcrypto;

ALTER TABLE patients
    ADD COLUMN ssn_encrypted BYTEA,
    ADD COLUMN medical_notes_encrypted BYTEA;
```

## Backup and Recovery

### Backup Strategy
```sql
-- Full backup
pg_dump -Fc -f backup.dump patient_db

-- Incremental backup using WAL
ALTER SYSTEM SET wal_level = replica;
ALTER SYSTEM SET archive_mode = on;
ALTER SYSTEM SET archive_command = 'cp %p /archive/%f';
```

## Related Documentation
- [[Data Models]]
- [[Query Optimization]]
- [[Backup Procedures]]
- [[Security Implementation]]

## Tags
#database #schema #postgresql #optimization 