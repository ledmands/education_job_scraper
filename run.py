# Todo: Add error handling and link to main website url in email body

import os
from scrape import Scrape
from send import Send
from extract import Extract
from datetime import datetime, timedelta

script_dir = os.path.abspath(os.path.dirname(__file__))
db_file = os.path.join(script_dir, "EducationJobPostings.db")
formatted_now = datetime.now().strftime("%B %d, %Y")

Scrape.num_chronicle_pages = 10
Scrape.default_ajo_cutoff = "20250301"
Scrape.date_script_ran = formatted_now

# Extract_cutoff_date should be last 7 days, i.e. date script ran - 7
Extract.cutoff_date = datetime.strptime(formatted_now, "%B %d, %Y") - timedelta(days=7)
Extract.date_script_ran = formatted_now

with open(f"{script_dir}/credentials.txt", "r") as file:
    Send.password = file.read()
with open(f"{script_dir}/sender_email.txt", "r") as file:
    Send.sender_email = file.read()
with open(f"{script_dir}/receiver_email.txt", "r") as file:
    Send.receiver_email = file.read()

def main():
    
    Scrape.scrape_all_sites(db_file)
    print("scrape.py done")
    Extract.extract_all_tables(db_file)
    print("extract.py done")
    Send.send_all_extracts()
    print("send.py done")

    return 0

if __name__ == "main":
    main()
    
main()