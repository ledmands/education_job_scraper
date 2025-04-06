from bs4 import BeautifulSoup as bs
from datetime import datetime
import requests, sqlite3, os

dir_path = os.path.abspath(os.path.dirname(__file__))
ERROR_LOG = os.path.join(dir_path, "/logs/error_log.txt")

def scrape_academic_jobs_online(db_file, default_ajo_cutoff):
    table = "AcademicJobsOnlineJobs"
    url = "https://academicjobsonline.org/ajo?joblist-0-0-0-0---0-p--"
    headers = { "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        with open(ERROR_LOG, "a", encoding="utf-8") as file:
            file.write(f"----- ERROR IN {__file__}.{__name__} -----\n")
            file.write(f"Unable to reach website at {url}\n")
            file.write(f"response.status_code: {response.status_code}\n")
            file.write(f"Error occurred at: {datetime.now()}\n\n")
        return
    
    soup = bs(response.content, "html.parser")
    raw_postings = soup.find_all("div", "clr")
    print("Scraping " + url)

    # If we can't find the DB, don't scrape anything, just break out of the function
    try:
        connection = sqlite3.connect(db_file)
    except:
        with open(ERROR_LOG, "a", encoding="utf-8") as file:
            file.write(f"----- ERROR IN {__file__}.{__name__} -----\n")
            file.write(f"Could not connect to database {db_file}\n")
            file.write(f"Error occurred at: {datetime.now()}\n\n")
        return
    
    cursor = connection.cursor()
    
    try:
        urls_in_db = cursor.execute(f"select Url from {table}").fetchall()
    except:
        with open(ERROR_LOG, "a", encoding="utf-8") as file:
            file.write(f"----- ERROR IN {__file__}.{__name__} -----\n")
            file.write(f"Error fetching from {db_file}.{table}.Url\n")
            file.write(f"Closing database and aborting scrape of {url}\n")
            file.write(f"Error occurred at: {datetime.now()}\n\n")
        connection.close()
        return
    
    urls_list = []
    for i in urls_in_db:
        j = str(i[0])
        urls_list.append(j)

    # Set the cutoff date to the most recent date in the db
    # If this returns null, just use the default date defined in run.py
    cutoff_date = cursor.execute(f"select PostedDate from {table} order by PostedDate desc").fetchone()
    if cutoff_date is None:
        cutoff_date = default_ajo_cutoff
    else:
        cutoff_date = str(cutoff_date)
        
    cutoff_date = cutoff_date[1:9]
    cutoff_date = datetime.strptime(cutoff_date, "%Y%m%d")
    
    is_done = False
    for post in raw_postings:
        output = []
        
        try:
            institution = post.find("h3", "x1").find_all("a")

            # Need loop here because they put a comma between the institution and the department
            for i in institution:
                output.append(i.text)
            
            # for each post, get the ol object and iterate through each li in it
            postings_at_institution = post.find("ol").find_all("li")
            
            for item in postings_at_institution:
                
                # If there are multiple jobs at one place, reset the output before trying to insert
                if len(postings_at_institution) > 1:
                    # Pop all elements except for the first 2
                    for i in range(len(output) - 2):
                        output.pop()
                        
                title = item.find("a").next_sibling
                output.append(str(title).strip(']').lstrip())

                posted_date = item.find("span", "purplesml")
                output.append(posted_date.text)

                link = item.find("a")
                link_url = "academicjobsonline.org" + link["href"]
                output.append(link_url)
            
                posted_date = datetime.strptime(posted_date.text[-11:-1], "%Y/%m/%d")
                if posted_date < cutoff_date:
                    is_done = True
                    break
                
                # Before we insert, check for dupes based on url
                if link_url in urls_list:
                    return
                
                if len(output) == 4:
                    output[2] = posted_date.strftime("%Y%m%d")
                    output[2] = int(output[2])
                    try:
                        cursor.execute(f"INSERT INTO {table} VALUES(?,?,?,?,?)", (output[0],"",output[1],output[2],output[3]) )
                        connection.commit()
                    except:
                        with open(ERROR_LOG, "a", encoding="utf-8") as file:
                            file.write(f"----- ERROR IN {__file__}.{__name__} -----\n")
                            file.write(f"Unable to insert to table {db_file}.{table}\nValues:\n")
                            for j in output:
                                file.write(f"output[{j}]: {output[j]}\n")
                            file.write(f"Nothing committed to database.\n")
                            file.write(f"Error occurred at: {datetime.now()}\n\n")
                elif len(output) == 5:
                    output[3] = posted_date.strftime("%Y%m%d")
                    output[3] = int(output[3])
                    try:
                        cursor.execute(f"INSERT INTO {table} VALUES(?,?,?,?,?)", (output[0],output[1],output[2],output[3],output[4]) )
                        connection.commit()
                    except:
                        with open(ERROR_LOG, "a", encoding="utf-8") as file:
                            file.write(f"----- ERROR IN {__file__}.{__name__} -----\n")
                            file.write(f"Unable to insert to table {db_file}.{table}\nValues:\n")
                            for j in output:
                                file.write(f"output[{j}]: {output[j]}\n")
                            file.write(f"Nothing committed to database.\n")
                            file.write(f"Error occurred at: {datetime.now()}\n\n")
                            
        except:
            with open(ERROR_LOG, "a", encoding="utf-8") as file:
                file.write(f"----- ERROR IN {__file__}.{__name__} -----\n")
                file.write(f"Error with tags in element: {post}.\nSkipping element.\n")
                for j in output:
                    file.write(f"output[{j}]: {output[j]}\n")
                file.write(f"Error occurred at: {datetime.now()}\n\n")
            continue
        
        if is_done == True:
            break

    
    connection.close()
    return 0

def scrape_chronicle_higher_education(db_file, num_chronicle_pages):
    table = "ChronicleHigherEducationJobs"
    url = "https://jobs.chronicle.com/jobs/education/"
    headers = { "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}
    
    # If we can't find the DB, don't scrape anything, just break out of the function
    try:
        connection = sqlite3.connect(db_file)
    except:
        with open(ERROR_LOG, "a", encoding="utf-8") as file:
            file.write(f"----- ERROR IN {__file__}.{__name__} -----\n")
            file.write(f"Could not connect to database {db_file}\n")
            file.write(f"Error occurred at: {datetime.now()}\n\n")
        return
        
    cursor = connection.cursor()
    
    try:
        urls_in_db = cursor.execute(f"select Url from {table}").fetchall()
    except:
        with open(ERROR_LOG, "a", encoding="utf-8") as file:
            file.write(f"----- ERROR IN {__file__}.{__name__} -----\n")
            file.write(f"Error fetching from {db_file}.{table}.Url\n")
            file.write(f"Closing database and aborting scrape of {url}\n")
            file.write(f"Error occurred at: {datetime.now()}\n\n")
        connection.close()
        return
    
    urls_list = []
    for i in urls_in_db:
        j = str(i[0])
        urls_list.append(j)
    
    for i in range(num_chronicle_pages):
        print("Scraping " + url)
        response = requests.get(url, headers=headers)

        # If the page doesn't exist or there's a problem, don't scrape it
        if response.status_code != 200:
            with open(ERROR_LOG, "a", encoding="utf-8") as file:
                file.write(f"----- ERROR IN {__file__}.{__name__} -----\n")
                file.write(f"Unable to reach website at {url}\n")
                file.write(f"response.status_code: {response.status_code}\n")
                file.write(f"Error occurred at: {datetime.now()}\n\n")
            continue
        
        soup = bs(response.content, "html.parser")
        
        listings_grid = soup.find("ul", id="listing")
        all_listings = listings_grid.find_all("li", "lister__item") #, class_="lister__item cf lister__item--display-logo-on-listing lister__item--display-logo-on-listing")
        
        # Also need to jump past all the sponsored postings
        for listing in all_listings:
            # If a listing is a premium listing, skip it. Best I can tell, the "LinkSource" is a common denominator for sponsored listings
            link_to_listing = listing.find("a")["href"].strip()
            if "LinkSource" in link_to_listing:
                continue      

            listing_link = listing.find("a")["href"].strip()
            listing_url = "https://jobs.chronicle.com" + listing_link
            listing_response = requests.get(listing_url, headers=headers)
            
            # If the page doesn't exist or there's a problem, don't scrape it
            if response.status_code != 200:
                with open(ERROR_LOG, "a", encoding="utf-8") as file:
                    file.write(f"----- ERROR IN {__file__}.{__name__} -----\n")
                    file.write(f"Unable to reach website at {url}\n")
                    file.write(f"response.status_code: {response.status_code}\n")
                    file.write(f"Error occurred at: {datetime.now()}\n\n")
                continue

            listing_soup = bs(listing_response.content, "html.parser")
            title_element = listing_soup.find("h1", "mds-font-s6")
            
            output = []
            
            try:
                # Get job title from page, start here and work through DOM to get each object since they're less uniquely named
                title = title_element.text.strip()
                output.append(title)
                
                current_element = title_element.find_next("dd")
                
                # The other information that might be helpful isn't always listed, like Position Type or Employment Type.
                # ToDo: get the optional information in the accordian dropdown
                for _ in range(4):
                    output.append(current_element.text.strip())
                    current_element = current_element.find_next("dd") # The last current element here will be the date
                    
                output.append(listing_url)
                
                # Format: Mar 28, 2025, convert to 20250328
                output[4] = output[4].replace(",", "")
                output[4] = datetime.strptime(output[4], "%b %d %Y").strftime("%Y%m%d")
                output[4] = int(output[4])
            except:
                with open(ERROR_LOG, "a", encoding="utf-8") as file:
                    file.write(f"----- ERROR IN {__file__}.{__name__} -----\n")
                    file.write(f"Unable to scrape {listing_link}\n")
                    file.write(f"Error occurred at: {datetime.now()}\n\n")
            
            # Before we insert, check for dupes based on url
            if listing_url in urls_list:
                return
            try:
                cursor.execute(f"INSERT INTO {table} VALUES(?,?,?,?,?,?)", (output[0],output[1],output[2],output[3],output[4],output[5]) )
                connection.commit()
            except:
                with open(ERROR_LOG, "a", encoding="utf-8") as file:
                    file.write(f"----- ERROR IN {__file__}.{__name__} -----\n")
                    file.write(f"Unable insert to database {db_file}.{table}\nAttempted to insert values:\n")
                    for i in output:
                        file.write(f"output[{i}]: {output[i]}\n")
                    file.write(f"Nothing committed to database.\n")
                    file.write(f"Error occurred at: {datetime.now()}\n\n")
                    
        # Strip out any appended pages and append i + 2
        url = url[0:42]
        url = url + str(i + 2)
                
    connection.close()
    
    return 0

def scrape_naaee(db_file):
    table = "NaaeeJobs"
    try:
        connection = sqlite3.connect(db_file)
    except:
        with open(ERROR_LOG, "a", encoding="utf-8") as file:
            file.write(f"----- ERROR IN {__file__}.{__name__} -----\n")
            file.write(f"Could not connect to database {db_file}\n")
            file.write(f"Error occurred at: {datetime.now()}\n\n")
        return
    
    cursor = connection.cursor()
    
    try:
        urls_in_db = cursor.execute(f"select Url from {table}").fetchall()
    except:
        with open(ERROR_LOG, "a", encoding="utf-8") as file:
            file.write(f"----- ERROR IN {__file__}.{__name__} -----\n")
            file.write(f"Error fetching from {db_file}.{table}.Url\n")
            file.write(f"Closing database and aborting scrape of {url}\n")
            file.write(f"Error occurred at: {datetime.now()}\n\n")
        connection.close()
        return
    
    urls_list = []
    for i in urls_in_db:
        j = str(i[0])
        urls_list.append(j)
    
    page = 0
    while True:
        # Filters: Job, Fellowship, Americorps, Contractor, Other 
        url = "https://jobs.naaee.org/jobs?search_api_fulltext=&field_tag_job_category%5B%5D=5&field_tag_job_category%5B%5D=3&field_tag_job_category%5B%5D=30&field_tag_job_category%5B%5D=31&field_tag_job_category%5B%5D=7&created=-30+days&page="
        url = url + str(page) # append the page number
        page = page + 1
        headers = { "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}
        response = requests.get(url, headers=headers)
        print("Scraping " + url)

        # If the page doesn't exist or there's a problem, don't scrape it
        if response.status_code != 200:
            with open(ERROR_LOG, "a", encoding="utf-8") as file:
                file.write(f"----- ERROR IN {__file__}.{__name__} -----\n")
                file.write(f"Unable to reach website at {url}")
                file.write(f"response.status_code: {response.status_code}\n")
                file.write(f"Error occurred at: {datetime.now()}\n\n")
            break
        soup = bs(response.content, "html.parser")
        
        postings_grid = soup.find("div", "grid-container") #id="block-views-block-search-api-block-2")
        # If we're on a page that doesn't exist (i.e. no more postings), we're done
        if postings_grid is None:
            break
        posting_cards = postings_grid.find_all("a", "job-teaser-tile")
        
        for job in posting_cards:
            output = []
            
            title = job.find("h3", "job-title").text
            organization = job.find("div", "job-org-name").text
            location = job.find("div", "job-address").text
            link = "https://jobs.naaee.org/" + job["href"]
            status = ""
            category = ""
            job_type = ""
            date_posted = ""
            try:
                status = job.find("span", "tag--job-status").text
                category = job.find("span", "tag--category").text
                job_type = job.find("span", "tag--type").text
                date_posted = job.find("span", "tag--posted").text
                date_posted = datetime.strptime(date_posted, "%B %d, %Y").strftime("%Y%m%d")
                date_posted = int(date_posted)
            except:
                with open(ERROR_LOG, "a", encoding="utf-8") as file:
                    file.write(f"----- ERROR IN {__file__}.{__name__} -----\n")
                    file.write(f"Unable to find an element tag for link: {link}.\n")
                    file.write(f"status:      {status}\n")
                    file.write(f"category:    {category}\n")
                    file.write(f"job_type:    {job_type}\n")
                    file.write(f"date_posted: {date_posted}\n")
                    file.write(f"Error occurred at: {datetime.now()}\n\n")
                                
            output.append(title)
            output.append(organization)
            output.append(location)
            output.append(status)
            output.append(category)
            output.append(job_type)
            output.append(date_posted)
            output.append(link)
            
            # Check for dupes 
            # Before we insert, check for dupes based on url
            if link in urls_list:
                return
            try:
                cursor.execute(f"INSERT INTO {table} VALUES(?,?,?,?,?,?,?,?)", (output[0],output[1],output[2],output[3],output[4],output[5],output[6],output[7]) )
                connection.commit()
            except:
                with open(ERROR_LOG, "a", encoding="utf-8") as file:
                    file.write(f"----- ERROR IN {__file__}.{__name__} -----\n")
                    file.write(f"Unable insert to database {db_file}.{table}\nAttempted to insert values:\n")
                    for i in output:
                        file.write(f"output[{i}]: {output[i]}\n")
                    file.write("Nothing committed to database.\n")
                    file.write(f"Error occurred at: {datetime.now()}\n\n")
        
    
    connection.close()
    
    return 0

def scrape_all_sites(db_file, num_chronicle_pages, default_ajo_cutoff):
    scrape_academic_jobs_online(db_file, default_ajo_cutoff)
    scrape_chronicle_higher_education(db_file, num_chronicle_pages)
    scrape_naaee(db_file)
    return 0

if __name__ == "main":
    scrape_all_sites()