from bs4 import BeautifulSoup
import requests
import csv
from datetime import datetime

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.47'
}

def job_salary(card):
    svg_snippet = card.find('div', class_='attribute_snippet')
    if svg_snippet:
        return svg_snippet.text

def job_location(card):
    return card.find('div', class_='companyLocation').text

def job_title(card):
    for span_row in card.find_all('span'):
        title = span_row.get('title')
        if title:
            return title

def get_job_record(card):
    company_name = card.find_all('span', class_="companyName")[0].text
    title = job_title(card)
    location = job_location(card)
    salary = job_salary(card)
    
    return (company_name, title, location, salary)

def get_page_records(cards, job_list, url_set):
    for card in cards:
        record = get_job_record(card)
        
        # add if job title exists and not duplicate
        if record[0] and record[-1] not in url_set:
            job_list.append(record)
            url_set.add(record[-1])

def get_url(position, location, page=0):
        template = 'https://www.indeed.com/jobs?q={}&l={}'
        position = position.replace(' ', '+')
        location = location.replace(' ', '+')
        if page == 0:
            return template.format(position, location)
        else:
            return template.format(position, location) + '&start={}'.format(int(page*10))
    
def get_page_html(url):
    response = requests.get(url,headers=headers)
    return response.content

def save_data_to_file(records):
    with open('results.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Company', 'JobTitle', 'Location', 'Salary'])
        writer.writerows(records)


def main(position, location):
    scraped_jobs = []
    scraped_urls = set()
    
    # right now set up to index over the number of pages 
    page=1
    
    url = get_url(position, location)
    webpage = get_page_html(url)
    soup = BeautifulSoup(webpage, 'html.parser')

    while page:
        # print(url)
        cards = soup.find_all('div', class_='job_seen_beacon')
        # print(len(cards))

        get_page_records(cards, scraped_jobs, scraped_urls)
        page+=1
        try:
            url = get_url(position, location, page)
        except:
            break
        webpage = get_page_html(url)
        soup = BeautifulSoup(webpage, features="html.parser")
        
    save_data_to_file(scraped_jobs)

main('software engineer', 'denver co')   