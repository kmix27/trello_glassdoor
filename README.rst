### Trello + GlassDoor job search tool  

I have been using Trello to organize my job search.  I wanted a quick command line tool that would allow me to populate a list on my job search board automatically with the action items I find relevant.  A strong caveat before you use this:  I haven't polished this up too much, so it's kinda hacky.  

#### Setup:  
Before you begin you'll need several things:  
* A Trello [account](https://trello.com/)  
* Your Trello [API key](https://trello.com/app-key)  
* An authorization token which can be generated below where you find your key  

```bash  
pip install trellogd
```  


####Usage:  
Usage is relatively simple,  You should now have a command line tool called tgd. To add a job to your board you'll need a direct link to that job listing on glassdoor.  You are after the flavor that doesn't have a bunch of other job listings in a navbar on the left, you want just the listing you are interested in.  You'll probably need to right click and open a job link in a new tab.  You should see the path "glassdoor.com/job-listing/..."   

```bash
tgd [url for glassdoor job]
```  
Is the basic usage of the tool.  The first time you use it you will be prompted to input your API key and token.  
This will generate a config.json file in your directory, and you'll get an empty board within trello where your lists will populate.  Starting with the first url you input.  

You should now have a new list with three cards on your board.  Those cards will have everything that I find relevant when applying for that particular job.  Add more if the spirit so moves you.  

Some further options are available:  
If you need to add to a diffrent board than the one specified in your config the options -t or --target are available.  

```bash
tgd [url for job] -t [board ID you would like to add to]
```  

if you would like to update your config file so that all future posts go directly there the options -u or --update can be used:  

```bash
tgd [url for job] -t [board ID to change to] -u
```  
That's all I've got so far.  

####Caveate  
Glassdoor doesn't like web scrapers. This obviously isn't aimed at pulling down their data en mass, however, if you fire it off on too many posts too quickly you will get an error and need to cool off for a bit, maybe try applying for some of those jobs.  This will happen to you from a web browser as well, so no surprises.  

I hope you find this useful!  


####To Do:
* Expand function to work with 'jobs/jobs.htm' path on GD   
* Add other job search sites, control via options flags  
* Automator app