## This is a job board scraper written to find education and academic jobs and email them to a specified recipient.

### Running run.py should do three things:
<ol>
<li>Scrape the websites specified in scrape.py and insert the data into an SQLite database.</li>
<li>Extract data from the database using extract.py and write it to a file for each website scraped. Extract files are located in the extracts subdirectory.</li>
<li>Send the data from the extract files using send.py to a recipient as a plain text email.</li>
</ol>

### The SQLite database and tables should be initialized prior to running the scripts. 

From the project directory, you can create the SQLite database EducationJobPostings.db by running the following Python code:

<code>>>> import sqlite3</code><br>
<code>>>> connection = sqlite3.connect("EducationJobPostings.db")</code><br>
<code>>>> cursor = connection.cursor()</code><br>
<code>>>> cursor.execute(CREATE TABLE AcademicJobsOnlineJobs(Institution, Department, JobTitle, PostedDate, Url))</code><br>
<code>>>> cursor.execute(CREATE TABLE ChronicleHigherEducationJobs(JobTitle, Organization, Location, Compensation, PostedDate, Url))</code><br>
<code>>>> cursor.execute(CREATE TABLE NaaeeJobs(JobTitle, Organization, Location, Status, Category, Type, PostedDate, Url))</code><br>
<code>>>> connection.commit()</code><br>
<code>>>> connection.close()</code><br>