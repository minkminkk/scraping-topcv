# scraping-topcv

This is a mini project which aims to crawl basic info about newest IT jobs on [TopCV](https://www.topcv.vn/viec-lam-it). The crawled data will be imported into PostgreSQL database.

Details about each job posting include:
- `job_id`: Job posting ID, as stored in their server backend.
- `job_title`: Job title.
- `company`: Recruiter company.
- `salary_min`, `salary_max`: Salary range (in million VND).
- `yrs_of_exp_min`, `yrs_of_exp_max`: Years of experience required.
- `job_city`: Working location (city).
- `due_date`: Deadline for application.
- `jd`: Job description.

## Required programs

- `git`.
- `docker` with `docker-compose`.

## Usage

### Clone the git repository

```shell
git clone https://github.com/minkminkk/scraping-topcv.git
```

### Set up

To initialize database and crawler, run:

```shell
docker compose up
```

PostgreSQL database with the required table will be set up, then the crawler will start crawling.

### Tear down

After you are done, run:

```shell
docker compose down
```

The containers and network will be deleted.

## Note

The crawler is **not yet** able to crawl the whole data as TopCV limits the request rate. In the future, crawling using rotating proxies could be implemented to overcome this.

## License

[MIT](https://choosealicense.com/licenses/mit/)