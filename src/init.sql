/* TABLE jobs
Include basic information about job postings

Columns:
    job_id [int] PK: ID of job posting, crawled directly from topcv
    job_title [varchar]: Job title
    company [varchar]: Recruiter company
    salary_min, salary_max [smallint]: Salary range
        nullable
        min = max if single value
    yrs_of_exp_min, yrs_of_exp_max [smallint]: Experience required
        nullable
        min = max if single value
    job_city [varchar]: City of job location
    due_date [date]: Deadline for job applications
    jd [text]: Job description
*/

CREATE TABLE IF NOT EXISTS jobs (
    job_id INTEGER PRIMARY KEY,
    job_title VARCHAR,
    company VARCHAR,
    salary_min SMALLINT,
    salary_max SMALLINT,
    yrs_of_exp_min SMALLINT,
    yrs_of_exp_max SMALLINT,
    job_city VARCHAR,
    due_date DATE,
    jd TEXT,
    created_at TIMESTAMP(0) DEFAULT NOW(),
    last_modified TIMESTAMP(0) DEFAULT NOW()
);

-- Create trigger to update last modification timestamp of each record
CREATE OR REPLACE FUNCTION update_last_modified() 
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER update_row
BEFORE UPDATE ON jobs
FOR EACH ROW
EXECUTE FUNCTION update_last_modified();