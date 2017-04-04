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
from config import config_store
import os


__version__ = '0.2'

# load config file
def load_config():
    ''' base config file loader,  if no flags are specified this will load,
    or if one does not yet exist, prompt the user to create a config file'''
    config_store()
    try:
        with open(os.path.expanduser("~/.trellogd/config.json"), 'r') as c:
            auth = json.load(c)
            return auth
    except FileNotFoundError:
        print('\nConfig file not found.  Entering setup\n')
        from config import main as cfmain
        cfmain()
        print('Configuration complete. Populating your board...\n')
        with open(os.path.expanduser("~/.trellogd/config.json"), 'r') as c:
            auth = json.load(c)
            return auth




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


def populate_board(url, target=None, update=False):
    '''takes a URL for a glass door posting, and creates a trello list with helpful job hunt items '''
    if target:
        auth = ret_labels(target)
        if update == True:
            auth = update_config(target)
    else:
        auth = load_config()
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
    new_list = board.add_list(name=list_name, pos=None)
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


def update_config(board_id):
    '''when the -u or --update flag is used this will call ret_labels,
    and re-write the config file to permanently target that board''' 
    auth = ret_labels(board_id)
    with open(os.path.expanduser("~/.trellogd/config.json"), 'w') as uc:
        json.dump(auth, uc)
    return auth


def ret_labels(board_id):
    ''' when the -t or --target flag are used, this will open
    the config file, target the requested, get the necessary
    supporting labels on that board, and return a modified config dict'''
    auth = load_config()
    client = TrelloClient(
        api_key=auth['key'],
        token=auth['token'])
    board = client.get_board(board_id=board_id)
    labels = board.get_labels()
    bld = {}
    for i in labels:
        if i.name == 'Links':
            bld['link_l'] = i.id
        if i.name == 'Description':
            bld['desc_l'] = i.id
        if i.name == 'To Do':
            bld['check_l'] = i.id
    auth['link_l'] = bld['link_l']
    auth['desc_l'] = bld['desc_l']
    auth['check_l'] = bld['check_l']
    auth['board_id'] = board_id
    return auth


def parse_args():
    '''Takes arguments from cli and parses them'''
    parser = argparse.ArgumentParser()
    parser.add_argument('url', type=str, 
                        help='add a glassdoor job url to your trello board')
    parser.add_argument('--target_board', dest='target_board',type=str, default=None, 
                        help='Target a board not in your config.json')
    parser.add_argument('-t', dest='target',type=str, default=None, 
                        help='Target a board not in your config.json')
    parser.add_argument('-u', dest='update', default=False, action='store_true', 
                        help='re-configure to always target this board, requires target board')
    parser.add_argument('--update', dest='update', default=False, action='store_true', 
                        help='re-configure to always target this board')
    args = parser.parse_args()
    return args


def shell():
    '''gets necessary args and populates them, 
    calls the populate function, split out for error handeling'''
    args = parse_args()
    populate_board(url=args.url,target=args.target,update=args.update )


def main():
    try:
        shell()
    except KeyboardInterrupt:
        print_('\nCancelling...')


if __name__ == '__main__':
    main()