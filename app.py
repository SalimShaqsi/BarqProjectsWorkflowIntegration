from datetime import datetime, timedelta

from flask import Flask
import os
import requests

app = Flask(__name__)

token = os.environ['TOKEN']
headers = {'Authorization': f'Token {token}'}


@app.route('/')
def hello_world():
    # get the approved lists
    response = requests.get('https://www.barqprojects.com/api/approved_lists/', headers=headers)
    approved_lists = response.json()

    # extract approved companies as a set of ids
    approved_companies = set()
    for l in approved_lists:
        approved_companies = approved_companies.union({c.split('/')[-2] for c in l['approved_companies']})

    # get applications
    response = requests.get('https://www.barqprojects.com/api/company_applications/', headers=headers)
    apps = response.json()

    # filter apps to include only ones submitted / approved within the last year

    apps = [
        a for a in apps if a['status'] in ['2', '3']
        and datetime.strptime(a['updated_on'][:10], '%Y-%m-%d') + timedelta(
            days=365) > datetime.now()
    ]

    # get the filtered approved companies
    excluded_companies = {a['owner'].split('/')[-2] for a in apps}
    expired_approved_companies = approved_companies.difference(excluded_companies)

    # get all companies (not efficient at all, but works)
    response = requests.get('https://www.barqprojects.com/api/companies/', headers=headers)
    all_companies = response.json()

    # get manager emails
    emails = {c['manager']['email'] for c in all_companies
              if c['verified'] and not c['dummy'] and str(c['id']) in expired_approved_companies}

    return str(list(emails))


if __name__ == '__main__':
    app.run()
