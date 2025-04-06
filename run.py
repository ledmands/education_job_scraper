# Todo: Add error handling and link to main website url in email body

import scrape, extract, send, os
from datetime import datetime, timedelta

script_dir = os.path.abspath(os.path.dirname(__file__))
db_file = os.path.join(script_dir, "EducationJobPostings.db")

num_chronicle_pages = 10
default_ajo_cutoff = "20250301"
date_script_ran = datetime.now().strftime("%B %d, %Y")
# Extract_cutoff_date should be last 7 days, i.e. date script ran - 7
extract_cutoff_date = datetime.strptime(date_script_ran, "%B %d, %Y") - timedelta(days=7)

receiver_email = ""
sender_email = ""
subject_prefix = "Job Postings From "
password = ""
with open(f"{script_dir}/credentials.txt", "r") as file:
    password = file.read()
with open(f"{script_dir}/sender_email.txt", "r") as file:
    sender_email = file.read()
with open(f"{script_dir}/receiver_email.txt", "r") as file:
    receiver_email = file.read()
port = 465
host = "smtp.gmail.com"

def main():
    
    scrape.scrape_all_sites(db_file, num_chronicle_pages, default_ajo_cutoff)
    print("scrape.py done")
    extract.extract_all_tables(db_file, extract_cutoff_date, date_script_ran)
    print("extract.py done")
    send.send_all_extracts(sender_email, password, receiver_email, subject_prefix, host, port)
    print("send.py done")

    return 0

if __name__ == "main":
    main()
    
main()