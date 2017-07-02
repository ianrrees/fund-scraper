#!/usr/local/bin/python3
# A quick tool for saving ASB Kiwisaver fund prices from their public website
# Copyright Ian Rees July 2017, see LICENSE for details

from collections import OrderedDict
from urllib import parse
from urllib import request
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
import os.path

sourceUrl = "https://www.asb.co.nz/iFrames/latest_unit_prices.asp"
dataFileName = "fund_data.csv"

class FundLogger():
    def __init__(self, fileName):

        # Maps from section to a list of funds within that section
        # Note we use these as column headers in the csv, so don't reorganise.
        self.knownFunds = OrderedDict()
        self.knownFunds["ASB Investment Funds"] = [
                "Balanced Fund",
                "Conservative Fund",
                "Conservative Plus Fund",
                "Global Property Shares Fund",
                "Growth Fund",
                "Moderate Fund",
                "World Fixed Interest Fund",
                "World Shares Fund",
                ]
        self.knownFunds["ASB KiwiSaver Scheme"] = [
                "Balanced Fund",
                "Conservative Fund",
                "Growth Fund",
                "Moderate Fund",
                "NZ Cash Fund",
                ]
        self.knownFunds["ASB Superannuation Master Trust"] = [
                "ASB Australasian Shares Fund",
                "ASB Balanced Fund",
                "ASB Global Property Shares Fund",
                "ASB Growth Fund",
                "ASB Moderate Fund",
                "ASB NZ Cash Fund",
                "ASB NZ Fixed Interest Fund",
                "ASB World Fixed Interest Fund",
                "ASB World Shares Fund",
                ]

        self.fileName = fileName

        if not os.path.isfile(fileName):
            self.fileHandle = open(self.fileName, "w")
            self.fileHandle.write('"Date",')
            for section in self.knownFunds:
                for fund in self.knownFunds[section]:
                    self.fileHandle.write('"%s - %s",' % (section, fund))

            self.fileHandle.write('\n')

        else:
            self.fileHandle = open(self.fileName, "a")

    def logRow(self, quoteDate, quoteDict):
        "Takes a dict with string tuple keys (section, fund name)"

        for quote in quoteDict:
            if ( quote[0] not in self.knownFunds or 
                 quote[1] not in self.knownFunds[quote[0]] ):
                print("Got an unknown fund name: " + " - ".join(quote))

        self.fileHandle.write(str(quoteDate) + ',')

        for section in self.knownFunds:
            for fund in self.knownFunds[section]:
                if (section, fund) in quoteDict:
                    quoteValue = quoteDict[(section, fund)]
                    self.fileHandle.write("%f," % quoteValue)
                else:
                    self.fileHandle.write('"",')

        self.fileHandle.write('\n')

def getDataForDate(queryDate = None):
    if queryDate is None:
        data = None
    else:
        args = {
                "currentDay" : queryDate.day,
                "currentMonth" : queryDate.month,
                "currentYear" : queryDate.year,
                }
        data = parse.urlencode(args).encode("UTF-8")

    req = request.urlopen(sourceUrl, data)
    return req.read()

def extractQuotes(rawData):
    "Yields tuples of (section, quoteName, quoteDate.date(), quoteValue)"
    section = None
    for row in BeautifulSoup(rawData, "html.parser").find_all("tr"):
        quoteName = None
        quoteDate = None
        quoteValue = None

        for col in row.children:
            div = col.find("div")
            if div is None or div == -1 or div.string is None:
                continue

            try:
                quoteValue = float(div.string)
                continue
            except ValueError:
                pass

            try:
                quoteDate = datetime.strptime(div.string, "%d %b %Y")
                continue
            except:
                pass

            if len(div.string) > 0:
                quoteName = div.string
                continue

        if quoteName and quoteDate and quoteValue:
            # Regular data row
            yield (section, quoteName, quoteDate.date(), quoteValue)
        else:
            # Beginning of new section
            div = col.find("div")
            if div is None or div == -1 or div.string is None:
                continue
            section = div.string

def processDate(queryDate, logger):
    rawData = getDataForDate(queryDate)
    thisDate = None
    rowDict = {}
    for row in extractQuotes(rawData):
        # row is a tuple of (section, quoteName, quoteDate.date(), quoteValue)
        if thisDate is None:
            thisDate = row[2]
            if thisDate != queryDate:
                return False
        else:
            if thisDate != row[2]:
                print('Got incongruent dates for "%s" - discarding' % row[1])
                continue
        rowDict[(row[0], row[1])] = row[3]

    if thisDate is not None:
        logger.logRow(thisDate, rowDict)
        return True

####### Execution starts ########

try: # to figure out the last day we have data for...
    with open(dataFileName, "r") as datafile:
        lastLine = None
        for line in datafile.readlines():
            if len(line.strip()) > 1:
                lastLine = line

        lastDateStr = lastLine.split(",")[0] 
        lastDate = datetime.strptime( lastDateStr, "%Y-%m-%d" ).date()

except FileNotFoundError:
    # Default date to start records from
    lastDate = date(2016, 12, 31)

queryDate = lastDate + timedelta(days = 1) # start date
endDate = datetime.now().date() # end date

logger = FundLogger(dataFileName)

while queryDate <= endDate:
    if queryDate.weekday() <= 4: # Skip weekends - no point
        # print("Fetching", queryDate)
        processDate(queryDate, logger)

    queryDate += timedelta(days = 1)

