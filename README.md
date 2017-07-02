# fund-scraper

Simple web scraper intended to fetch data from the [ASB](https://www.asb.co.nz/) "Unit Prices" page, so I could get a bit more historical data on some ASB funds than was provided in their prepared documentation.
The raw data is available publicly per-day via https://www.asb.co.nz/investment-advice/unit-prices.html, this is just a little Python tool that saves it as a CSV.

Script is written in Python 3, the only external dependency is [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/).

It's a fairly straightforward script, and certainly has room for improvement.
When it's run, it queries the ASB server for data subsequent to the last logged date, parses the results, and puts them in the log file.
I've included a log file that's pre-filled between the beginning of 2010 and this weekend.

The script is MIT licensed - do what you want with it (however, let's not spam too much, else this sort of thing gets harder for everyone).
It won't take much of a change on ASB's site before this stops working, there's a good chance I won't update the script in that case, and there is absolutely no verification or validation going on.

The whole thing is at your own risk, enjoy!
