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
import re


__version__ = '0.2.4'

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




def pull_data_gd(url):
    '''helper function to scrape data from glassdoor post and return a dict'''
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
#     apply url
    ap_url = soup.find(class_='empLinks tbl').find('a')['href']
    ap_type = soup.find(class_='empLinks tbl').find('a').text
    # removing this, it's unneeded
    # descHtml = soup.find(class_='jobDescriptionContent desc')
    referer = 'GlassDoor' 
    h = html2text.HTML2Text()
    desc = h.handle(str(descHtml))
    data = dict(job=job, ap_url=ap_url, ap_type=ap_type, desc=desc,
                referer=referer, company=company, city=city, dept=dept)
    return data


def pull_data_gh(url):
    ''' Helper function to scrape a Greenhouse posting returns a dict'''
    ua = UserAgent()
    head = ua.random
    resp = requests.get(url, headers={'User-Agent': head})
    soup = BeautifulSoup(resp.text, 'lxml')
#     job title
    job = soup.find(id='header').find(class_='app-title').text
#     app link
    ap_url = url + '#app'
    ap_type = 'Greenhouse'
    # content
    cont = soup.find(id = 'content')
    h = html2text.HTML2Text()
    desc = h.handle(str(cont))
#     don't need deschtml, should probably get rid everywhere
#     company
    co_name = soup.find(id='header').find(class_='company-name')
    company = list(co_name.stripped_strings)[0].strip('at ')
    city = soup.find(id='header').find(class_='location')
    city = list(city.stripped_strings)[0]
    dept = ''
    referer='GreenHouse'
    data = dict(job=job, ap_url=ap_url, ap_type=ap_type, desc=desc,
                referer=referer, company=company, city=city, dept=dept)
    return data


def pull_data_lev(url):
    '''Helper function to scrape a lever.io listing and return a dict'''
    ua = UserAgent()
    head = ua.random
    resp = requests.get(url, headers={'User-Agent': head})
    soup = BeautifulSoup(resp.text, 'lxml')
    lev_head = soup.find(class_ ='section-wrapper accent-section page-full-width')
    job = lev_head.find(class_ = 'posting-headline').find('h2').text
    ap_url = lev_head.find(class_="postings-btn-wrapper").find('a')['href']
    lev_con = soup.find(class_='content')
    h = html2text.HTML2Text()
    desc = h.handle(str(lev_con))
    ap_type = referer = 'Lever.io'
    company = url.strip('https://jobs.lever.co').split('/')[0]
    cats = lev_head.find(class_ = 'posting-headline').find(class_='posting-categories')
    city = cats.find(class_='sort-by-time posting-category medium-category-label').text
    dept = cats.find(class_="sort-by-team posting-category medium-category-label").text
    data = dict(job=job, ap_url=ap_url, ap_type=ap_type, desc=desc,
                referer=referer, company=company, city=city, dept=dept)
    return data


def pull_data_li(url):
    '''Helper function to scrape a linkedin listing and return a dict'''
    ua = UserAgent()
    head = ua.random
    resp = requests.get(url, headers={'User-Agent': head})
    soup = BeautifulSoup(resp.text, 'lxml')
    ap_url = url
    referer = ap_type = 'Linkedin'
    pat = re.compile(r'(?=\bat\b)[\s\w]*(?<=\bin\b)')
    title_ = soup.find('title').text
    company = re.findall(pat,title_)[0].strip('at ').strip(' in')
    city = title_.split(' in ')[-1].split(' | ')[0].strip()
    job = title_.split(' at ')[0].strip(' Job')
    con_ = soup.find(property="og:description")['content']
    desc = con_.replace('\n','\n \n').replace('· ', '\n\n· ').replace('&nbsp;&nbsp;','\n\n').replace('&nbsp;','')  
    dept = ''
    data = dict(job=job, ap_url=ap_url, ap_type=ap_type, desc=desc,
                referer=referer, company=company, city=city, dept=dept)
    return data


def pull_data_js(url):
    '''helper function to scrape data from jobscore post and return a dict'''
    ua = UserAgent()
    head = ua.random
    resp = requests.get(url, headers={'User-Agent': head})
    soup = BeautifulSoup(resp.text, 'lxml')
    ap_type = referer = 'JobScore'
    job = soup.find(class_='js-title').text
    company = url.strip('https://careers.jobscore.com/careers/').split('/')[0]
    dept = soup.find(class_='js-subtitle').text.split(' | ')[0]
    city = soup.find(class_='js-subtitle').text.split(' | ')[1]
    cont = soup.find(class_='js-area-container js-section-job-description')
    h = html2text.HTML2Text()
    desc = h.handle(str(cont))
    href = soup.find(class_='js-btn js-btn-block js-btn-apply')['href']
    base = 'https://careers.jobscore.com'
    ap_url = base + href
    data = dict(job=job, ap_url=ap_url, ap_type=ap_type, desc=desc,
                referer=referer, company=company, city=city, dept=dept)
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
    # gets board Labels
    board = client.get_board(board_id=auth['board_id'])
    link_l = client.get_label(auth['link_l'], auth['board_id'])
    desc_l = client.get_label(auth['desc_l'], auth['board_id'])
    check_l = client.get_label(auth['check_l'], auth['board_id'])
    # check URL for type
    url_clean = url.strip('https://').split('/')
    if url_clean[0] == 'www.glassdoor.com':
        url_type = '/'.join(url_clean[:2])
    if url_clean[0] == 'www.linkedin.com':
        url_type = '/'.join(url_clean[:3])
    else:
        url_type = url_clean[0]
    # use url type to call scrape function
    if url_type == 'www.glassdoor.com/job-listing':
        # scrapes GD for job info
        data = pull_data_gd(url)
    elif url_type == 'boards.greenhouse.io':
        data = pull_data_gh(url)
    elif url_type == 'jobs.lever.co':
        data = pull_data_lev(url)
    elif url_type == 'www.linkedin.com/jobs/view':
        data = pull_data_li(url)
    elif url_type == 'careers.jobscore.com':
        data = pull_data_js(url)
    else:
        print("Sorry, either {} isn't supported yet, or something unexpectedly changed\n".format(url_clean[0]))
        print("Feel free to implement and send a PR, or email: Kyle@KyleMix.com")
        return None
    data['post_url'] = url
    list_name = data['company'] + ':\n' + data['job'] + '\n\nAdded: ' + str(datetime.now())
    j_title = data['company'] + ': ' + data['job']
    # create list object
    new_list = board.add_list(name=list_name, pos=None)
    # add cards to list object
    description = new_list.add_card(name='{} \nDetails:'.format(j_title), desc=data['desc'])
    attachCard = new_list.add_card(name='{} \nLinks:'.format(j_title))
    attachCard.attach(name=data['ap_type'], url=data['ap_url'])
    attachCard.attach(name='Original posting', url=data['post_url'])
    # attempts to build a direct search link for linkedin which targets company and department if available
    if data['dept'] != '':
        li_url = 'https://www.linkedin.com/search/results/people/?keywords=' + data['company'].replace(' ','%20') + '%20' + data['dept'].replace(' ', '%20')
        attachCard.attach(name='Linkedin search, Company + Department',
            url= li_url) 
    else:
        li_url = 'https://www.linkedin.com/search/results/people/?keywords=' + data['company'].replace(' ', '%20')
        attachCard.attach(name='Linkedin search, Company',
            url=li_url)
    goog_base = 'https://www.google.com/#safe=off&q='
    goog_company = goog_base+data['company'].replace(' ','+')
    attachCard.attach(name='Google search, Company',url=goog_company)
    gd_search_hack = 'https://www.glassdoor.com/Reviews/{}-reviews-SRCH_KE0,{}.htm'.format(data['company'], len(data['company']))
    dt = datetime.now() + timedelta(days=3)
    cl = ['Research Hiring manager [Linkedin]({})'.format(li_url), 'Research company, [glassdoor]({}), [google]({})'.format(gd_search_hack, goog_company),
          'Polish Resume [creddle](https://resume.creddle.io/)',
          'Craft Cover Letter, [Drive](https://drive.google.com)', 'Attempt to make contact on personal level [Linkedin]({})'.format(li_url),
          'Complete application [Application link]({})'.format(data['ap_url']), 'Send application',
          'Wait three days: {}'.format(str(dt.date())), 'Send follow up email']
    clCard = new_list.add_card('To Do List')
    clCard.add_checklist(title='To Do!\n\n{}'.format(j_title), items=cl)
    clCard.set_due(dt.date())
    notes_card = new_list.add_card(name='Notes')
    notes_card.comment('Added Via tgd on: {}\n Refered through {}'.format(datetime.now(), data['referer']))
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