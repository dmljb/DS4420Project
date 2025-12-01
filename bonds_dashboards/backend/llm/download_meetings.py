import requests
import pandas as pd
from bs4 import BeautifulSoup
import PyPDF2
from io import BytesIO
import re
from datetime import datetime
import os
import time

class FOMCMinutesScraper:
    def __init__(self, base_url="https://www.federalreserve.gov"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_fomc_meetings(self, years=list(range(2010, 2026))):
        """Get FOMC meeting data with PDF links for specified years"""
        all_meetings = {
            2010: [
                {'date': 'January 26-27, 2010', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20100127.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20100127a1.pdf', 'presser_pdf': None},
                {'date': 'March 16, 2010', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20100316.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20100316a1.pdf', 'presser_pdf': None},
                {'date': 'April 27-28, 2010', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20100428.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20100428a1.pdf', 'presser_pdf': None},
                {'date': 'June 22-23, 2010', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20100623.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20100623a1.pdf', 'presser_pdf': None},
                {'date': 'August 10, 2010', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20100810.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20100810a1.pdf', 'presser_pdf': None},
                {'date': 'September 21, 2010', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20100921.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20100921a1.pdf', 'presser_pdf': None},
                {'date': 'November 2-3, 2010', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20101103.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20101103a1.pdf', 'presser_pdf': None},
                {'date': 'December 14, 2010', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20101214.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20101214a1.pdf', 'presser_pdf': None}
            ],
            2011: [
                {'date': 'January 25-26, 2011', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20110126.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20110126a1.pdf', 'presser_pdf': None},
                {'date': 'March 15, 2011', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20110315.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20110315a1.pdf', 'presser_pdf': None},
                {'date': 'April 26-27, 2011', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20110427.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20110427a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20110427.pdf'},
                {'date': 'June 21-22, 2011', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20110622.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20110622a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20110622.pdf'},
                {'date': 'August 9, 2011', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20110809.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20110809a1.pdf', 'presser_pdf': None},
                {'date': 'September 20-21, 2011', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20110921.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20110921a1.pdf', 'presser_pdf': None},
                {'date': 'November 1-2, 2011', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20111102.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20111102a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20111102.pdf'},
                {'date': 'December 13, 2011', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20111213.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20111213a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20111213.pdf'}
            ],
            2012: [
                {'date': 'January 24-25, 2012', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20120125.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20120125a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20120125.pdf'},
                {'date': 'March 13, 2012', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20120313.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20120313a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20120313.pdf'},
                {'date': 'April 24-25, 2012', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20120425.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20120425a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20120425.pdf'},
                {'date': 'June 19-20, 2012', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20120620.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20120620a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20120620.pdf'},
                {'date': 'July 31-August 1, 2012', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20120801.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20120801a1.pdf', 'presser_pdf': None},
                {'date': 'September 12-13, 2012', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20120913.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20120913a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20120913.pdf'},
                {'date': 'October 23-24, 2012', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20121024.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20121024a1.pdf', 'presser_pdf': None},
                {'date': 'December 11-12, 2012', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20121212.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20121212a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20121212.pdf'}
            ],
            2013: [
                {'date': 'January 29-30, 2013', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20130130.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20130130a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20130130.pdf'},
                {'date': 'March 19-20, 2013', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20130320.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20130320a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20130320.pdf'},
                {'date': 'April 30-May 1, 2013', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20130501.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20130501a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20130501.pdf'},
                {'date': 'June 18-19, 2013', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20130619.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20130619a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20130619.pdf'},
                {'date': 'July 30-31, 2013', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20130731.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20130731a1.pdf', 'presser_pdf': None},
                {'date': 'September 17-18, 2013', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20130918.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20130918a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20130918.pdf'},
                {'date': 'October 29-30, 2013', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20131030.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20131030a1.pdf', 'presser_pdf': None},
                {'date': 'December 17-18, 2013', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20131218.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20131218a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20131218.pdf'}
            ],
            2014: [
                {'date': 'January 28-29, 2014', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20140129.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20140129a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20140129.pdf'},
                {'date': 'March 18-19, 2014', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20140319.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20140319a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20140319.pdf'},
                {'date': 'April 29-30, 2014', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20140430.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20140430a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20140430.pdf'},
                {'date': 'June 17-18, 2014', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20140618.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20140618a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20140618.pdf'},
                {'date': 'July 29-30, 2014', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20140730.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20140730a1.pdf', 'presser_pdf': None},
                {'date': 'September 16-17, 2014', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20140917.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20140917a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20140917.pdf'},
                {'date': 'October 28-29, 2014', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20141029.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20141029a1.pdf', 'presser_pdf': None},
                {'date': 'December 16-17, 2014', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20141217.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20141217a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20141217.pdf'}
            ],
            2015: [
                {'date': 'January 27-28, 2015', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20150128.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20150128a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20150128.pdf'},
                {'date': 'March 17-18, 2015', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20150318.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20150318a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20150318.pdf'},
                {'date': 'April 28-29, 2015', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20150429.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20150429a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20150429.pdf'},
                {'date': 'June 16-17, 2015', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20150617.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20150617a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20150617.pdf'},
                {'date': 'July 28-29, 2015', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20150729.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20150729a1.pdf', 'presser_pdf': None},
                {'date': 'September 16-17, 2015', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20150917.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20150917a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20150917.pdf'},
                {'date': 'October 27-28, 2015', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20151028.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20151028a1.pdf', 'presser_pdf': None},
                {'date': 'December 15-16, 2015', 'decision': 'hike', 'rate': 0.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20151216.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20151216a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20151216.pdf'}
            ],
            2016: [
                {'date': 'January 26-27, 2016', 'decision': 'hold', 'rate': 0.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20160127.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20160127a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20160127.pdf'},
                {'date': 'March 15-16, 2016', 'decision': 'hold', 'rate': 0.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20160316.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20160316a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20160316.pdf'},
                {'date': 'April 26-27, 2016', 'decision': 'hold', 'rate': 0.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20160427.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20160427a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20160427.pdf'},
                {'date': 'June 14-15, 2016', 'decision': 'hold', 'rate': 0.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20160615.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20160615a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20160615.pdf'},
                {'date': 'July 26-27, 2016', 'decision': 'hold', 'rate': 0.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20160727.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20160727a1.pdf', 'presser_pdf': None},
                {'date': 'September 20-21, 2016', 'decision': 'hold', 'rate': 0.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20160921.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20160921a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20160921.pdf'},
                {'date': 'November 1-2, 2016', 'decision': 'hold', 'rate': 0.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20161102.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20161102a1.pdf', 'presser_pdf': None},
                {'date': 'December 13-14, 2016', 'decision': 'hike', 'rate': 0.75, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20161214.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20161214a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20161214.pdf'}
            ],
            2017: [
                {'date': 'January 31-February 1, 2017', 'decision': 'hold', 'rate': 0.75, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20170201.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20170201a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20170201.pdf'},
                {'date': 'March 14-15, 2017', 'decision': 'hike', 'rate': 1.00, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20170315.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20170315a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20170315.pdf'},
                {'date': 'May 2-3, 2017', 'decision': 'hold', 'rate': 1.00, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20170503.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20170503a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20170503.pdf'},
                {'date': 'June 13-14, 2017', 'decision': 'hike', 'rate': 1.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20170614.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20170614a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20170614.pdf'},
                {'date': 'July 25-26, 2017', 'decision': 'hold', 'rate': 1.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20170726.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20170726a1.pdf', 'presser_pdf': None},
                {'date': 'September 19-20, 2017', 'decision': 'hold', 'rate': 1.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20170920.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20170920a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20170920.pdf'},
                {'date': 'October 31-November 1, 2017', 'decision': 'hold', 'rate': 1.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20171101.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20171101a1.pdf', 'presser_pdf': None},
                {'date': 'December 12-13, 2017', 'decision': 'hike', 'rate': 1.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20171213.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20171213a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20171213.pdf'}
            ],
            2018: [
                {'date': 'January 30-31, 2018', 'decision': 'hold', 'rate': 1.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20180131.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20180131a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20180131.pdf'},
                {'date': 'March 20-21, 2018', 'decision': 'hike', 'rate': 1.75, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20180321.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20180321a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20180321.pdf'},
                {'date': 'May 1-2, 2018', 'decision': 'hold', 'rate': 1.75, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20180502.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20180502a1.pdf', 'presser_pdf': None},
                {'date': 'June 12-13, 2018', 'decision': 'hike', 'rate': 2.00, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20180613.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20180613a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20180613.pdf'},
                {'date': 'July 31-August 1, 2018', 'decision': 'hold', 'rate': 2.00, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20180801.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20180801a1.pdf', 'presser_pdf': None},
                {'date': 'September 25-26, 2018', 'decision': 'hike', 'rate': 2.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20180926.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20180926a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20180926.pdf'},
                {'date': 'November 7-8, 2018', 'decision': 'hold', 'rate': 2.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20181108.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20181108a1.pdf', 'presser_pdf': None},
                {'date': 'December 18-19, 2018', 'decision': 'hike', 'rate': 2.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20181219.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20181219a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20181219.pdf'}
            ],
            2019: [
                {'date': 'January 29-30, 2019', 'decision': 'hold', 'rate': 2.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20190130.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20190130a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20190130.pdf'},
                {'date': 'March 19-20, 2019', 'decision': 'hold', 'rate': 2.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20190320.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20190320a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20190320.pdf'},
                {'date': 'April 30-May 1, 2019', 'decision': 'hold', 'rate': 2.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20190501.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20190501a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20190501.pdf'},
                {'date': 'June 18-19, 2019', 'decision': 'hold', 'rate': 2.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20190619.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20190619a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20190619.pdf'},
                {'date': 'July 30-31, 2019', 'decision': 'cut', 'rate': 2.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20190731.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20190731a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20190731.pdf'},
                {'date': 'September 17-18, 2019', 'decision': 'cut', 'rate': 2.00, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20190918.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20190918a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20190918.pdf'},
                {'date': 'October 29-30, 2019', 'decision': 'cut', 'rate': 1.75, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20191030.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20191030a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20191030.pdf'},
                {'date': 'December 10-11, 2019', 'decision': 'hold', 'rate': 1.75, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20191211.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20191211a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20191211.pdf'}
            ],
            2020: [
                {'date': 'January 28-29, 2020', 'decision': 'hold', 'rate': 1.75, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20200129.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20200129a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20200129.pdf'},
                {'date': 'March 3, 2020', 'decision': 'cut', 'rate': 1.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20200303.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20200303a1.pdf', 'presser_pdf': None},
                {'date': 'March 15, 2020', 'decision': 'cut', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20200315.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20200315a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20200315.pdf'},
                {'date': 'April 28-29, 2020', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20200429.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20200429a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20200429.pdf'},
                {'date': 'June 9-10, 2020', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20200610.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20200610a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20200610.pdf'},
                {'date': 'July 28-29, 2020', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20200729.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20200729a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20200729.pdf'},
                {'date': 'September 15-16, 2020', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20200916.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20200916a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20200916.pdf'},
                {'date': 'November 4-5, 2020', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20201105.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20201105a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20201105.pdf'},
                {'date': 'December 15-16, 2020', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20201216.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20201216a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20201216.pdf'}
            ],
            2021: [
                {'date': 'January 26-27, 2021', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20210127.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20210127a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20210127.pdf'},
                {'date': 'March 16-17, 2021', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20210317.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20210317a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20210317.pdf'},
                {'date': 'April 27-28, 2021', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20210428.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20210428a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20210428.pdf'},
                {'date': 'June 15-16, 2021', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20210616.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20210616a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20210616.pdf'},
                {'date': 'July 27-28, 2021', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20210728.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20210728a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20210728.pdf'},
                {'date': 'September 21-22, 2021', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20210922.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20210922a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20210922.pdf'},
                {'date': 'November 2-3, 2021', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20211103.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20211103a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20211103.pdf'},
                {'date': 'December 14-15, 2021', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20211215.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20211215a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20211215.pdf'}
            ],
            2022: [
                {'date': 'January 25-26, 2022', 'decision': 'hold', 'rate': 0.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20220126.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20220126a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20220126.pdf'},
                {'date': 'March 15-16, 2022', 'decision': 'hike', 'rate': 0.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20220316.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20220316a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20220316.pdf'},
                {'date': 'May 3-4, 2022', 'decision': 'hike', 'rate': 1.00, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20220504.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20220504a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20220504.pdf'},
                {'date': 'June 14-15, 2022', 'decision': 'hike', 'rate': 1.75, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20220615.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20220615a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20220615.pdf'},
                {'date': 'July 26-27, 2022', 'decision': 'hike', 'rate': 2.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20220727.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20220727a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20220727.pdf'},
                {'date': 'September 20-21, 2022', 'decision': 'hike', 'rate': 3.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20220921.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20220921a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20220921.pdf'},
                {'date': 'November 1-2, 2022', 'decision': 'hike', 'rate': 4.00, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20221102.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20221102a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20221102.pdf'},
                {'date': 'December 13-14, 2022', 'decision': 'hike', 'rate': 4.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20221214.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20221214a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20221214.pdf'}
            ],
            2023: [
                {'date': 'January 31-February 1, 2023', 'decision': 'hike', 'rate': 4.75, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20230201.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20230201a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20230201.pdf'},
                {'date': 'March 21-22, 2023', 'decision': 'hike', 'rate': 5.00, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20230322.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20230322a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20230322.pdf'},
                {'date': 'May 2-3, 2023', 'decision': 'hike', 'rate': 5.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20230503.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20230503a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20230503.pdf'},
                {'date': 'June 13-14, 2023', 'decision': 'hold', 'rate': 5.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20230614.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20230614a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20230614.pdf'},
                {'date': 'July 25-26, 2023', 'decision': 'hike', 'rate': 5.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20230726.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20230726a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20230726.pdf'},
                {'date': 'September 19-20, 2023', 'decision': 'hold', 'rate': 5.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20230920.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20230920a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20230920.pdf'},
                {'date': 'October 31-November 1, 2023', 'decision': 'hold', 'rate': 5.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20231101.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20231101a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20231101.pdf'},
                {'date': 'December 12-13, 2023', 'decision': 'hold', 'rate': 5.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20231213.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20231213a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20231213.pdf'}
            ],
            2024: [
                {'date': 'January 30-31, 2024', 'decision': 'hold', 'rate': 5.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20240131.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20240131a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20240131.pdf'},
                {'date': 'March 19-20, 2024', 'decision': 'hold', 'rate': 5.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20240320.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20240320a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20240320.pdf'},
                {'date': 'April 30-May 1, 2024', 'decision': 'hold', 'rate': 5.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20240501.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20240501a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20240501.pdf'},
                {'date': 'June 11-12, 2024', 'decision': 'hold', 'rate': 5.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20240612.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20240612a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20240612.pdf'},
                {'date': 'July 30-31, 2024', 'decision': 'hold', 'rate': 5.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20240731.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20240731a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20240731.pdf'},
                {'date': 'September 17-18, 2024', 'decision': 'cut', 'rate': 4.75, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20240918.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20240918a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20240918.pdf'},
                {'date': 'November 6-7, 2024', 'decision': 'cut', 'rate': 4.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20241107.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20241107a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20241107.pdf'},
                {'date': 'December 17-18, 2024', 'decision': 'cut', 'rate': 4.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20241218.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20241218a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20241218.pdf'}
            ],
            2025: [
                {'date': 'January 28-29, 2025', 'decision': 'hold', 'rate': 4.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20250129.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20250129a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20250129.pdf'},
                {'date': 'March 18-19, 2025', 'decision': 'hold', 'rate': 4.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20250319.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20250319a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20250319.pdf'},
                {'date': 'April 29-30, 2025', 'decision': 'hold', 'rate': 4.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20250430.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20250430a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20250430.pdf'},
                {'date': 'June 17-18, 2025', 'decision': 'hold', 'rate': 4.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20250618.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20250618a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20250618.pdf'},
                {'date': 'July 29-30, 2025', 'decision': 'hold', 'rate': 4.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20250730.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20250730a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20250730.pdf'},
                {'date': 'September 16-17, 2025', 'decision': 'cut', 'rate': 4.00, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20250917.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20250917a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20250917.pdf'},
                {'date': 'October 28-29, 2025', 'decision': 'cut', 'rate': 3.75, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20251029.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20251029a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20251029.pdf'},
                # December meeting hasn't happened yet (scheduled for Dec 16-17, 2025)
            ]
        }
        
        # Combine requested years
        selected_meetings = []
        for year in years:
            if year in all_meetings:
                selected_meetings.extend(all_meetings[year])
        
        return selected_meetings
    
    def download_pdf(self, pdf_path, save_dir="fomc_data"):
        """Download PDF from Fed website"""
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        url = self.base_url + pdf_path
        filename = pdf_path.split('/')[-1]
        filepath = os.path.join(save_dir, filename)
        
        # Skip if already downloaded
        if os.path.exists(filepath):
            print(f"Already exists: {filename}")
            return filepath
            
        try:
            print(f"Downloading: {filename}")
            response = self.session.get(url)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            time.sleep(1)  # Be nice to Fed servers
            return filepath
            
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
            return None
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                return self.clean_text(text)
                
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return None
    
    def clean_text(self, text):
        """Clean extracted PDF text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers
        text = re.sub(r'Page \d+ of \d+', '', text)
        text = re.sub(r'FEDERAL RESERVE BOARD', '', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
        
        return text.strip()
    
    def extract_key_sections(self, text):
        """Extract key sections from FOMC minutes"""
        sections = {}
        
        # Look for common section headers
        patterns = {
            'economic_outlook': r'(Economic Outlook|Staff Review|Economic Conditions)',
            'policy_discussion': r'(Committee Policy Action|Policy Discussion|Monetary Policy)',
            'risks_concerns': r'(Risk Assessment|Risks|Concerns|Uncertainties)',
            'future_guidance': r'(Forward Guidance|Future Policy|Outlook for Policy)'
        }
        
        for section, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Extract ~500 words after the section header
                start = match.end()
                section_text = text[start:start+3000]  # ~500 words
                sections[section] = section_text.strip()
        
        return sections
    
    def create_training_dataset(self):
        """Create complete training dataset with labels"""
        meetings = self.get_fomc_meetings()
        dataset = []
        
        print("Starting FOMC data collection...")
        
        for meeting in meetings:
            print(f"\nProcessing: {meeting['date']}")
            
            # Download minutes PDF
            minutes_path = self.download_pdf(meeting['minutes_pdf'])
            if not minutes_path:
                continue
                
            # Extract text
            minutes_text = self.extract_text_from_pdf(minutes_path)
            if not minutes_text:
                continue
                
            # Extract key sections
            sections = self.extract_key_sections(minutes_text)
            
            # Create training record
            record = {
                'date': meeting['date'],
                'decision': meeting['decision'],
                'fed_funds_rate': meeting['rate'],
                'full_text': minutes_text,
                'text_length': len(minutes_text),
                **sections  # Add extracted sections
            }
            
            dataset.append(record)
        
        # Convert to DataFrame
        df = pd.DataFrame(dataset)
        
        # Save to files
        df.to_csv('fomc_training_data.csv', index=False)
        df.to_json('fomc_training_data.json', orient='records', indent=2)
        
        print(f"\nDataset created with {len(df)} meetings")
        print("Files saved: fomc_training_data.csv, fomc_training_data.json")
        
        return df

def main():
    """Run the scraper for comprehensive dataset"""
    scraper = FOMCMinutesScraper()
    
    # Get comprehensive dataset (7 years, ~56 meetings)
    dataset = scraper.create_training_dataset()
    
    # Display summary
    print("\n" + "="*50)
    print("COMPREHENSIVE DATASET SUMMARY")
    print("="*50)
    print(f"Total meetings: {len(dataset)}")
    print("\nDecision distribution:")
    decision_counts = dataset['decision'].value_counts()
    for decision, count in decision_counts.items():
        percentage = (count / len(dataset)) * 100
        print(f"  {decision}: {count} meetings ({percentage:.1f}%)")
    
    print(f"\nText statistics:")
    print(f"  Average length: {dataset['text_length'].mean():.0f} characters")
    print(f"  Min length: {dataset['text_length'].min():,} characters")
    print(f"  Max length: {dataset['text_length'].max():,} characters")
    
    print(f"\nRate range: {dataset['fed_funds_rate'].min():.2f}% to {dataset['fed_funds_rate'].max():.2f}%")
    print(f"Files saved: fomc_training_data_full.csv, fomc_training_data_full.json")
    
    return dataset

if __name__ == "__main__":
    # Install required packages first:
    # pip install requests beautifulsoup4 PyPDF2 pandas
    
    dataset = main()