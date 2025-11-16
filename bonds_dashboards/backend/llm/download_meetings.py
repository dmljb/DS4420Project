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
        
    def get_fomc_meetings(self, years=[2018, 2019, 2020, 2021, 2022, 2023, 2024]):
        """Get FOMC meeting data with PDF links for specified years"""
        all_meetings = {
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
            2018: [
                {'date': 'January 30-31, 2018', 'decision': 'hold', 'rate': 1.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20180131.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20180131a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20180131.pdf'},
                {'date': 'March 20-21, 2018', 'decision': 'hike', 'rate': 1.75, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20180321.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20180321a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20180321.pdf'},
                {'date': 'May 1-2, 2018', 'decision': 'hold', 'rate': 1.75, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20180502.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20180502a1.pdf', 'presser_pdf': None},
                {'date': 'June 12-13, 2018', 'decision': 'hike', 'rate': 2.00, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20180613.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20180613a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20180613.pdf'},
                {'date': 'July 31-August 1, 2018', 'decision': 'hold', 'rate': 2.00, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20180801.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20180801a1.pdf', 'presser_pdf': None},
                {'date': 'September 25-26, 2018', 'decision': 'hike', 'rate': 2.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20180926.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20180926a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20180926.pdf'},
                {'date': 'November 7-8, 2018', 'decision': 'hold', 'rate': 2.25, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20181108.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20181108a1.pdf', 'presser_pdf': None},
                {'date': 'December 18-19, 2018', 'decision': 'hike', 'rate': 2.50, 'minutes_pdf': '/monetarypolicy/files/fomcminutes20181219.pdf', 'statement_pdf': '/monetarypolicy/files/monetary20181219a1.pdf', 'presser_pdf': '/mediacenter/files/FOMCpresconf20181219.pdf'}
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