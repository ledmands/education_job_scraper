# Todo: Add error handling and link to main website url in email body

import extract, send, os
from scrape import Scrape
from send import Send
from datetime import datetime, timedelta

script_dir = os.path.abspath(os.path.dirname(__file__))
db_file = os.path.join(script_dir, "EducationJobPostings.db")

Scrape.num_chronicle_pages = 10
Scrape.default_ajo_cutoff = "20250301"
Scrape.date_script_ran = datetime.now().strftime("%B %d, %Y")

# Extract_cutoff_date should be last 7 days, i.e. date script ran - 7
Scrape.extract_cutoff_date = datetime.strptime(Scrape.date_script_ran, "%B %d, %Y") - timedelta(days=7)

with open(f"{script_dir}/credentials.txt", "r") as file:
    Send.password = file.read()
with open(f"{script_dir}/sender_email.txt", "r") as file:
    Send.sender_email = file.read()
with open(f"{script_dir}/receiver_email.txt", "r") as file:
    Send.receiver_email = file.read()

def main():
    
    Scrape.scrape_all_sites(db_file)
    print("scrape.py done")
    extract.extract_all_tables(db_file, extract_cutoff_date, date_script_ran)
    print("extract.py done")
    Send.send_all_extracts()
    print("send.py done")

    return 0

if __name__ == "main":
    main()
    
main()