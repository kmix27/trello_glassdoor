import requests
import lxml
from bs4 import BeautifulSoup
try:
    from trello import TrelloClient
except(ImportError):
    print('Please run: \npip install py-trello')
    exit()
try:
    from fake_useragent import UserAgent
except(ImportError):
    print('Please run: \npip install fake-useragent')
    exit()
from datetime import datetime, timedelta
import argparse
import json
import html2text

# load config file
with open('config.json', 'r') as c:
    auth = json.load(c)


def pull_data(url):
    '''helper function to scrape data and return a dict'''
    ua = UserAgent()
    head = ua.random
    resp = requests.get(url, headers={'User-Agent': head})
    soup = BeautifulSoup(resp.text, 'lxml')
    hcell = soup.find(class_='header cell info')
    job_title = hcell.find(class_='noMargTop margBotSm strong')
    job = job_title.text
    dept = ''
    if len(job.split(', ')) > 1:
        dept = job.split(',')[-1].strip()
    if len(job.split('-')) > 1:
        dept = job.split('-')[-1].strip()
    company = hcell.find(class_='ib').text.strip()
    city = hcell.find(class_='subtle ib').text.replace(' – ', '').split(',')[0]
    url = soup.find(class_='empLinks tbl').find('a')['href']
    ap_type = soup.find(class_='empLinks tbl').find('a').text
    descHtml = soup.find(class_='jobDescriptionContent desc')
    h = html2text.HTML2Text()
    desc = h.handle(str(descHtml))
    data = dict(job=job, url=url, ap_type=ap_type, desc=desc,
                descHtml=descHtml, company=company, city=city, dept=dept)
    return data


def populate_board(url):
    '''takes a URL for a glass door posting, and creates a trello list with helpful job hunt items '''
    client = TrelloClient(
        api_key=auth['key'],
        token=auth['token'])
    board = client.get_board(board_id=auth['board_id'])
    link_l = client.get_label(auth['link_l'], auth['board_id'])
    desc_l = client.get_label(auth['desc_l'], auth['board_id'])
    check_l = client.get_label(auth['check_l'], auth['board_id'])
    # scrapes GD for job info
    data = pull_data(url)
    data['gd_url'] = url
    list_name = data['company'] + ':\n' + data['job'] + '\n\nAdded: ' + str(datetime.now())
    j_title = data['company'] + ': ' + data['job']
    # create list object
    new_list = board.add_list(name=list_name,pos=None)
    # add cards to list object
    description = new_list.add_card(name='{} \nDetails:'.format(j_title), desc=data['desc'])
    attachCard = new_list.add_card(name='{} \nLinks:'.format(j_title))
    attachCard.attach(name=data['ap_type'], url=data['url'])
    attachCard.attach(name='GlassDoor posting', url=data['gd_url'])
    # attempts to build a direct search link for linkedin which targets company and department if available
    if data['dept'] != '':
        attachCard.attach(name='Linkedin search, Company + Department',
            url='https://www.linkedin.com/search/results/people/?keywords=' + data['company'].replace(' ','%20') + '%20' + data['dept'].replace(' ', '%20'))
    else:
        attachCard.attach(name='Linkedin search, Company',
            url='https://www.linkedin.com/search/results/people/?keywords=' + data['company'].replace(' ', '%20'))
    dt = datetime.now() + timedelta(days=3)
    cl = ['Research Hiring manager', 'Polish Resume',
          'Craft Cover Letter', 'Attempt to make contact on personal level',
          'Complete application', 'Send application',
          'Wait three days: {}'.format(str(dt.date())), 'Send follow up email']
    clCard = new_list.add_card('To Do List')
    clCard.add_checklist(title='To Do!\n\n{}'.format(j_title), items=cl)
    # add color coded labels to cards
    attachCard.add_label(link_l)
    description.add_label(desc_l)
    clCard.add_label(check_l)
    print('\n' + 'Success! \n\nAdded {} to you board'.format(j_title) + '\n\nCheck it out here:\nhttps://trello.com/b/{}'.format(auth['board_id'] + '\n'))


# command line functionality
parser = argparse.ArgumentParser()
parser.add_argument('url', type=str, help='add a glassdoor job url to your trello board')
args = parser.parse_args()

populate_board(args.url)
