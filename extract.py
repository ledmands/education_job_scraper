# This should have functions to pull data from each table and write to files
import sqlite3, os
from datetime import datetime


def extract_academic_jobs_online(db_file, cutoff_date, date_script_ran):
    directory = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(directory, "extracts/ajo_postings.txt")
    formatted_cutoff = datetime.strftime(cutoff_date, "%Y%m%d")

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    records = cursor.execute(f"select * from AcademicJobsOnlineJobs where PostedDate > {formatted_cutoff} order by PostedDate desc").fetchall()

    with open(filename, "w", encoding="utf-8") as file:
        file.write("Academic Jobs Online Postings\n")
        file.write(f"Postings as of {date_script_ran}\n")
        file.write(f"Postings listed since: {cutoff_date.strftime('%B %d, %Y')}\n")
        file.write("------------\n\n")

    for i in records:
        li = list(i)
        if li[3] == "": # Don't think I need this for this table, but cya doesn't hurt
            continue
        else:
            li[3] = datetime.strptime(str(li[3]), "%Y%m%d").strftime("%B %d, %Y")

        with open(filename, "a", encoding="utf-8") as file:
            for j in li:
                # Some fields could be blank here (like department), so skip if they are
                if j == "":
                    continue
                file.write(j + "\n")
            file.write("\n")
    
    return 0

def extract_chronicle_higher_education(db_file, cutoff_date, date_script_ran):
    
    directory = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(directory, "extracts/chronicle_postings.txt")
    formatted_cutoff = datetime.strftime(cutoff_date, "%Y%m%d")

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    records = cursor.execute(f"select * from ChronicleHigherEducationJobs where PostedDate > {formatted_cutoff} order by PostedDate desc").fetchall()

    with open(filename, "w", encoding="utf-8") as file:
        file.write("Chronicle Higher Education Job Postings\n")
        file.write(f"Postings as of {date_script_ran}\n")
        file.write(f"Postings listed since: {cutoff_date.strftime('%B %d, %Y')}\n")
        file.write("------------\n\n")

    for i in records:
        li = list(i)
        li[4] = datetime.strptime(str(li[4]), "%Y%m%d").strftime("%B %d, %Y")

        with open(filename, "a", encoding="utf-8") as file:
            for j in li:
                file.write(j + "\n")
            file.write("\n")
            
    return 0

def extract_naaee(db_file, cutoff_date, date_script_ran):
    
    directory = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(directory, "extracts/naaee_postings.txt")
    formatted_cutoff = datetime.strftime(cutoff_date, "%Y%m%d")

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    records = cursor.execute(f"select * from NaaeeJobs where PostedDate > {formatted_cutoff} order by PostedDate desc").fetchall()

    with open(filename, "w", encoding="utf-8") as file:
        file.write("NAAEE Job Postings\n")
        file.write(f"Postings as of {date_script_ran}\n")
        file.write(f"Postings listed since: {cutoff_date.strftime('%B %d, %Y')}\n")
        file.write("------------\n\n")

    for i in records:
        li = list(i)
        if li[6] == "":
            continue
        else:
            li[6] = datetime.strptime(str(li[6]), "%Y%m%d").strftime("%B %d, %Y")

        with open(filename, "a", encoding="utf-8") as file:
            for j in li:
                file.write(j + "\n")
            file.write("\n")
    
    return 0

def extract_all_tables(db_file, cutoff_date, date_script_ran):
    extract_naaee(db_file, cutoff_date, date_script_ran)
    extract_chronicle_higher_education(db_file, cutoff_date, date_script_ran)
    extract_academic_jobs_online(db_file, cutoff_date, date_script_ran)
    return 0

if __name__ == "main":
    extract_all_tables()