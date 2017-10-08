# tutuka-trial-python

Project Title: Tutuka Trial Project
This is a Transaction matching/reconciliation project i created in Flask(a Python micro-framework).
How it works:
    - upload 2 csv files
    - ajax request is formed and processed in backend [app.py]
    - 2 files are checked for extension validity and saved on server
    - duplicates records are removed, because they are redundant
    - count of total records is made
    - common records(based on Date/Amount/Identifier/Narrative) are found and written to tmp file, and count made
    - count of uncommon/unmatched records is made from difference of original 2 files and tmp file(common records)
    - response is sent back via ajax, from different templates and loaded on page without refresh
    - unmatched records are displayed as reports in front-end and in logs for analysis

Getting Started:
    These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.
    See deployment for notes on how to deploy the project on a live system.

Prerequisites:
    Python 2.7.12
    Flask

Installing locally:
    - install python 2.7.12
    - install pip, or easy_install (for linux based systems)
    - install virtualenv
    - install Flask

Running app:
    python app.py
    Open browser, navigate to: http://127.0.0.1:5000/

Deployment:

Built With:
    -Flask -  A web framework built in Python
    -JQuery - Frontend js library used
    -HTML/CSS - for layout and styling

