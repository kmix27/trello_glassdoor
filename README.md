### Trello + GlassDoor job search tool  

I have been using Trello to organize my job search.  I wanted a quick command line tool that would allow me to populate a list on my job search board automatically with the action items I find relevant.  A strong caveat before you use this:  I haven't polished this up much, so it's kinda hacky.  You might run into issues,  and you'll need to manually check dependancies because reasons.  It's working for me on an anaconda install of 3.5.1.  I hope it works for you too!  


#### Setup:  
Before you begin you'll need several things:  
* A clone of this repo  
* A Trello [account](https://trello.com/)  
* Your Trello [API key](https://trello.com/app-key)  
* An authorization token which can be generated below where you find your key  

  
Check the [requirements.txt](https://github.com/kmix27/trello_glassdoor/blob/master/requirements.txt) to confirm you have the necessary libraries installed.  I'll automate this later.  

From a fresh terminal cd into the directory and run:  

```bash  
python config.py "your api key" "your api token" "Name for your board"
```  

This should create config.json in your directory, and you'll get an empty board within trello where your lists will populate.  You only need to run config prior to your first use.  


####Usage:  
To add a job to your board you'll need a direct link to that job listing on glassdoor.  You are after the flavor that doesn't have a bunch of other job listings in a navbar on the left, you want just the listing you are interested in.  You'll probably need to right click and open a job link in a new tab.  You should see the path "glassdoor.com/job-listing/..."  Once you have that direct URL, you'll run the following from the repo directory:  

```bash
python trellogd.py "url to the job i'm interested in"
```  

You should now have a new list with three cards on your board.  Those cards will have everything that I find relevant when applying for that particular job.  Add more if the spirit so moves you.

Glassdoor doesn't like web scrapers, and while this isn't aimed at pulling down their data en mass,  if you fire it off on too many posts too quickly you will get an error and need to cool off for a bit, maybe try applying for some of those jobs.  

I hope you find this useful!  


####To Do:
* Repackage into a direct command line tool using [click](http://click.pocoo.org/5/)  
* Automate install via pip  
* Expand function to work with 'jobs/jobs.htm' path on GD   
* Add other job search sites, control via options flags  
* browser extension?



