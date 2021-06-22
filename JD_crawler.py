import requests
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
from random import random
import os
import json

head = 'https://ca.indeed.com'
newest_ds = 'https://ca.indeed.com/jobs?q=data+scientist&sort=date'

def get_soup(url):
    t = 1 + 2 * random()
    time.sleep(t)
    try:
        page = requests.get(url, headers={'User-Agent': 'Resistance is futile'})
    except:
        return None
    else:
        return BeautifulSoup(page.text, 'lxml')


def find_job_cards(soup):
    return soup.find_all('div', class_="jobsearch-SerpJobCard unifiedRow row result")

class Job_Card():
    def __init__(self, job_card):
        self.job = job_card
        self.summary = {}


    def get_job_title(self):
        try:
            self.summary['title'] = self.job.find('h2', class_='title').a.get_text().strip()
        except:
            self.summary['title'] = None

    def get_company(self):
        try:
            self.summary['company'] = self.job.find('span', class_='company').get_text().strip()
        except:
            self.summary['company'] = None

    def get_company_rating(self):
        try:
            self.summary['rating'] = self.job.find('span', class_='ratingsDisplay').get_text().strip()
        except:
            self.summary['rating'] = None

    def get_job_loc(self):
        try:
            self.summary['loc'] = self.job.find('div', class_='recJobLoc').get('data-rc-loc')
        except:
            self.summary['loc'] = None

    def get_job_remote(self):
        try:
            self.summary['remote'] = self.job.find('span', class_='remote').get_text().strip()
        except:
            self.summary['remote'] = None

    def get_salary(self):
        try:
            self.summary['salary'] = self.job.find('span', class_='salaryText').get_text().strip()
        except:
            self.summary['salary'] = None

    def get_info_page(self):
        try:
            self.summary['info_page'] = head + self.job.find('h2', class_='title').a.get('href')
        except:
            self.summary['info_page'] = None

    def get_job_Description(self):
        info_soup = get_soup(self.summary['info_page'])
        try:
            jd_all = info_soup.find('div', id='jobDescriptionText')
        except:
            self.summary['job_description'] = None
        else:
            self.summary['job_description'] = '\n'.join([p for p in jd_all.descendants if isinstance(p, str)])


def get_newest_jd(url):
    soup = get_soup(url)
    job_cards = find_job_cards(soup)
    job_sum = []
    for job_card in job_cards:
        job = Job_Card(job_card)
        job.get_job_title()
        job.get_company()
        job.get_company_rating()
        job.get_job_loc()
        job.get_job_remote()
        job.get_salary()
        job.get_info_page()
        job.get_job_Description()
        job_sum.append(job.summary)

    return pd.DataFrame(job_sum)

def get_multiple_pages_jd(start_url, n):
    jobs_page1 = get_newest_jd(start_url)
    jobs_all = [jobs_page1]
    for i in range(1, n):
        tail = f'&start={i}0'
        url = start_url + tail
        jobs_all.append(get_newest_jd(url))
    
    return jobs_all

if __name__ == "__main__":
    dfs = get_multiple_pages_jd(newest_ds, 8)
    df = pd.concat(dfs, ignore_index=True) 
    df.to_excel('newest_ds_job.xlsx', index=False)