from utils.processors import PageProcessor, JobProcessor
from psycopg2 import sql
import psycopg2 as pg


def main():
    # Process pages recursively from first page
    job_listing_url = "https://www.topcv.vn/viec-lam-it?sort=up_top"
    detail_urls = PageProcessor().generate_page_urls(job_listing_url, recursive = True)
    
    try:
        # Connect to PostgreSQL database
        conn = pg.connect(dbname = "topcv", user = "postgres", password = "postgres")
        cur = conn.cursor()
        conn.autocommit = True
        script = open("init.sql", "r")

        cur.execute(script.read())

        # Crawl each job detail page into PostgreSQL DB
        job_processor = JobProcessor()
        for job_url in detail_urls:
            # Crawl each job page data into job_item
            job_item = job_processor.process_job(job_url, pause_between_jobs = 3)

            # Insert crawled record into PostgreSQL DB
            q = sql.SQL("""
                INSERT INTO jobs ({}) VALUES ({})
                ON CONFLICT (job_id) DO UPDATE SET ({}) = ({});
            """).format(
                sql.SQL(", ").join(map(sql.Identifier, job_item.keys())),
                sql.SQL(", ").join(map(sql.Placeholder, job_item.keys())),
                sql.SQL(", ").join(map(sql.Identifier, list(job_item.keys())[1:])),
                sql.SQL(", ").join(map(
                    sql.Identifier,
                    ["excluded" for _ in range(len(job_item) - 1)], 
                    list(job_item.keys())[1:]
                ))
            ).as_string(conn)
            cur.execute(q, job_item)
    except pg.errors.Error as e:
        print(e)
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
        script.close()
    

if __name__ == "__main__":
    main()
