from typing import override

from bs4 import BeautifulSoup
from bs4.element import Tag
from datetime import date, datetime, timedelta
from time import sleep

from utils.send_requests import send_request

USD_TO_VND = 24000

#################################################


class PageProcessor():
    """
    Processor class for job listing pages.
    """
    def generate_page_urls(self, 
        url: str, 
        recursive: bool = False
    ):
        """
        Generate job detail page URLs to JobProcessor and its derived classes.

        Arguments:
            url [str]: Processed URL.
            recursive [bool]: Enable processing pages recursively.

        Yields:
            job_url [str]: URL for job detail pages.

        Usage: 
            detail_url_gen = PageProcessor().get_job_detail_urls(
                <job_listing_url>,
                ...
            )
            for job_url in detail_url_gen:
                do something 
        """
        # Send requests and parse job details page and gather job data
        print("Scraping job URLs at", url)
        response = send_request("get", url)
        soup = BeautifulSoup(response.content, "html.parser")
        jobs_in_page = soup.find_all("div", "job-item-2")
        for job in jobs_in_page:
            job_url = job.find("a", target = "_blank")["href"]
            yield job_url

        # Process next page if found
        next_page_url = soup.find("a", rel = "next")["href"]
        if next_page_url and recursive:
            print("Page finished. Moving on to next page.")
            for job_url in self.generate_page_urls(next_page_url, recursive):
                yield job_url
        print("Page finished. Crawl ended.")


#################################################


class JobProcessor():
    """
    Base class for processors of job details page from given URL. 
    Main entrypoint for job page processing applications. 
    Can handle different site templates.
    """
    def process_job(self, url: str, pause_between_jobs: int = 3):
        """
        Parse URL to find job detail page template based on first-level subdirectory

        Arguments:
            url [str]: URL of job detail page.
            pause_between_jobs [int]: Seconds between each request 
                to get job detail page.

        Returns:
            job_item [dict]: Processed data.
        
        Usage: To scrape a job detail page onto job_item:
            job_item = Processor().process_job(<job_detail_url>)
        """
        print("Scraping job info at", url)

        # Parse URL and get keyword
        keyword = url.strip("https://www.").split("/")[1]
        keyword_map = {
            "viec-lam": _NormalJobProcessor(),
            "brand": _BrandJobProcessor()
        }

        # Instantiate suitable processor based on URL keyword
        try:
            processor = keyword_map[keyword]
        except KeyError:
            raise ValueError("Strange URL syntax detected. \
Wrong URL input or parsing for this page has not been implemented.")
        
        # Process job based on newly assigned processor
        sleep(pause_between_jobs)
        return processor.process_job(url)


    def _process_salary(self, salary_tag: Tag):
        """
        Parse salary tag into integer salary range (in million VND).
        Detects USD and convert to million VND.
        """
        salary_str = salary_tag.text.strip("\n")

        if salary_str == "Thoả thuận":      # Default string for no salary info
            min, max = (None, None)
        else:
            # Remove , thousand separators
            salary_arr = list(map(lambda x: x.replace(",", ""), salary_str.split(" ")))
            if salary_arr[1] == "-":        # Normal range (<min> - <max> <unit>)
                min, max = map(int, (salary_arr[0], salary_arr[2]))
            elif salary_arr[0] == "Trên":   # Min only (Trên <min> <unit>)
                min, max = int(salary_arr[1]), None
            elif salary_arr[0] == "Tới":    # Max only (Tới <max> <unit>)
                min, max = None, int(salary_arr[1])
        
            # Convert USD to million VND
            if salary_arr[-1] == "USD":
                min, max = map(
                    lambda x: int(x) * USD_TO_VND / 10**6 if x != None else None,
                    (min, max)
                )

        return min, max
    
    def _process_xp(self, xp_tag: Tag):
        # Returns min & max required experience (years)
        xp_str = xp_tag.text.strip("\n")
        xp_arr = xp_str.split(" ")

        if xp_str == "Không yêu cầu kinh nghiệm":
            min, max = 0, 0
        elif xp_arr[0].isnumeric(): # <xp> năm
            min, max = map(int, (xp_arr[0], xp_arr[0]))
        elif xp_arr[1].isnumeric(): # Trên/Dưới <xp> năm
            if xp_arr[0] == "Trên":
                min, max = int(xp_arr[1]), None
            if xp_arr[0] == "Dưới":
                min, max = None, int(xp_arr[1])
        else:
            min, max = None, None
        
        return min, max


class _NormalJobProcessor(JobProcessor):
    """
    Used for processing job detail pages with ./viec-lam/... subdirectories
    """
    @override
    def process_job(self, url: str):
        # Send request, instantiate BS object and define necessary tags
        response = send_request("get", url)
        soup = BeautifulSoup(response.content, "html.parser")
        detail_tags = soup.find_all("div", 
            class_ = "job-detail__info--section-content-value"
        )   # [salary_tag, city_tag, yrs_of_exp_tag]
        
        title_tag = soup.find("h1", class_ = "job-detail__info--title")
        company_tag = soup \
            .find("h2", class_ = "company-name-label").find("a")
        salary_tag = detail_tags[0]
        xp_tag = detail_tags[2]
        city_tag = detail_tags[1]
        due_tag = soup.find("div", class_ = "job-detail__info--deadline")
        jd_tag = soup.find("div", class_ = "job-description__item--content")

        # Process field values
        job_id = int(url.split("/")[-1].split(".")[0])
        job_title = title_tag.text.strip("\n")
        company = company_tag.text.strip("\n")
        salary_min, salary_max = self._process_salary(salary_tag)
        yrs_of_exp_min, yrs_of_exp_max = self._process_xp(xp_tag)
        job_city = city_tag.text.strip("\n")
        date_str = due_tag.text.split(" ")[-1].strip("\n")
        due_date = datetime.strptime(date_str, "%d/%m/%Y")
        jd = jd_tag.text.strip("\n")

        return {
            "job_id": job_id,
            "job_title": job_title,
            "company": company,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "yrs_of_exp_min": yrs_of_exp_min,
            "yrs_of_exp_max": yrs_of_exp_max,
            "job_city": job_city,
            "due_date": due_date,
            "jd": jd
        }


class _BrandJobProcessor(JobProcessor):
    """
    Used for processing job detail pages with ./brand/... subdirectories.
    - Template for diamond companies
    - Premium template

    Note: There are multiple templates for this subdirectory. Therefore, the class
    recognize template based on some tags and parse data based on it.  
    """
    @override
    def process_job(self, url: str):
        # Send request, instantiate BS object
        response = send_request("get", url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Recognize template and select appropriate strategy
        if soup.find("div", id = "premium-job"):
            job_item = self._process_job_premium(soup, url)
        else:
            job_item = self._process_job_diamond(soup, url)
        return job_item

    def _process_job_diamond(self, soup: BeautifulSoup, url: str):
        # Define necessary tags
        box_infos = soup.find_all("div", class_ = "box-info", limit = 2)
        item_tags = box_infos[0] \
            .find("div", class_ = "box-main") \
            .find_all("div", class_ = "box-item")
        
        title_tag = soup \
            .find("div", class_ = "box-header") \
            .find("h2", class_ = "title")
        company_tag = soup.find("div", class_ = "footer-info-company-name")
        salary_tag = item_tags[0].find("span")
        xp_tag = item_tags[-1].find("span")
        city_tag = soup \
            .find("div", class_ = "box-address") \
            .find("div") # Type 1 syntax
        due_tag = soup.find("span", class_ = "deadline").find("strong")
        jd_tag = box_infos[1].find("div", class_ = "content-tab")

        # Get job detail values
        job_id = int(url.split("/")[-1].split(".")[0].split("-")[-1][1:])
        job_title = title_tag.text.strip("\n")
        company = company_tag.text.strip("\n")
        salary_min, salary_max = self._process_salary(salary_tag)
        yrs_of_exp_min, yrs_of_exp_max = self._process_xp(xp_tag)
        job_city = city_tag.text[2:(city_tag.text.index(":") - 1)]
        days_remaining = int(due_tag.text)
        due_date = (date.today() + timedelta(days = days_remaining))
        jd = jd_tag.text.strip("\n")
        
        return {
            "job_id": job_id,
            "job_title": job_title,
            "company": company,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "yrs_of_exp_min": yrs_of_exp_min,
            "yrs_of_exp_max": yrs_of_exp_max,
            "job_city": job_city,
            "due_date": due_date,
            "jd": jd
        }

    def _process_job_premium(self, soup: BeautifulSoup, url: str):
        # Define necessary tags
        detail_tags = soup.find_all(
            "div", 
            class_ = "basic-information-item__data--value"
        )

        title_tag = soup.find("h2", "premium-job-basic-information__content--title")
        company_tag = soup.find("h1", "company-content__title--name")
        salary_tag = detail_tags[0]
        xp_tag = detail_tags[-1]
        city_tag = detail_tags[1]
        due_tag = soup.find_all("div", class_ = "general-information-data__value")[-1]
        jd_tag = soup.find("div", class_ = "premium-job-description__box--content")

        # Get job detail values
        job_id = int(url.split("/")[-1].split(".")[0].split("-")[-1][1:])
        job_title = title_tag.text.strip("\n")
        company = company_tag.text.strip("\n")
        salary_min, salary_max = self._process_salary(salary_tag)
        yrs_of_exp_min, yrs_of_exp_max = self._process_xp(xp_tag)
        job_city = city_tag.text.strip("\n")
        date_str = due_tag.text.split(" ")[-1].strip("\n")
        due_date = datetime.strptime(date_str, "%d/%m/%Y")
        jd = jd_tag.text.strip("\n")
        
        return {
            "job_id": job_id,
            "job_title": job_title,
            "company": company,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "yrs_of_exp_min": yrs_of_exp_min,
            "yrs_of_exp_max": yrs_of_exp_max,
            "job_city": job_city,
            "due_date": due_date,
            "jd": jd
        }
    