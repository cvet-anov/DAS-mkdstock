import aiohttp
import asyncio
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
import time


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MSEScraper:
    def __init__(self):
        self.base_url = "https://www.mse.mk/en/stats/symbolhistory"
        self.companies_url = "https://www.mse.mk/en/stats/symbolhistory/alk"
        self.output_file = "mse_data.csv"  

    async def create_session(self):
        return aiohttp.ClientSession(headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    async def fetch_companies(self, session):
        try:
            async with session.get(self.companies_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                companies = []
                
                for option in soup.select("#Code > option"):
                    code = option.text.strip()
                    if code and not any(char.isdigit() for char in code):
                        companies.append(code)
                
                logger.info(f"Found {len(companies)} companies")
                return companies
        except Exception as e:
            logger.error(f"Error fetching companies: {e}")
            return []

    def get_date_ranges(self, years=10):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * years)
        
        ranges = []
        current_date = start_date
        
        while current_date < end_date:
            next_date = min(current_date + timedelta(days=365), end_date)
            ranges.append((
                current_date.strftime("%m/%d/%Y"),
                next_date.strftime("%m/%d/%Y")
            ))
            current_date = next_date + timedelta(days=1)
            
        return ranges

    async def fetch_company_data(self, session, company, date_range):
        try:
            params = {
                'FromDate': date_range[0],
                'ToDate': date_range[1],
                'Code': company,
            }
            
            async with session.get(f"{self.base_url}/{company}", params=params) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                rows = []
                
                for row in soup.select("#resultsTable tbody tr"):
                    cols = row.select("td")
                    if len(cols) >= 9:
                        try:
                            row_data = {
                                "Date": datetime.strptime(cols[0].text.strip(), "%m/%d/%Y").strftime("%Y-%m-%d"),
                                "Company": company,
                                "Last_Price": self._clean_number(cols[1].text),
                                "High": self._clean_number(cols[2].text),
                                "Low": self._clean_number(cols[3].text),
                                "Average": self._clean_number(cols[4].text),
                                "Change_Pct": self._clean_number(cols[5].text),
                                "Volume": self._clean_number(cols[6].text),
                                "Turnover": self._clean_number(cols[7].text),
                                "Total_Turnover": self._clean_number(cols[8].text)
                            }
                            rows.append(row_data)
                        except Exception as e:
                            continue
                
                return rows
        except Exception as e:
            logger.error(f"Error fetching data for {company}: {e}")
            return []

    @staticmethod
    def _clean_number(value):
        try:
            return float(value.strip().replace(',', ''))
        except (ValueError, AttributeError):
            return 0.0

    async def process_company(self, session, company, date_ranges):
        all_data = []
        for date_range in date_ranges:
            data = await self.fetch_company_data(session, company, date_range)
            all_data.extend(data)
        return all_data

    def save_to_csv(self, data):
        df = pd.DataFrame(data)
        df.to_csv(self.output_file, index=False)
        logger.info(f"Saved {len(df)} records to {self.output_file}")

    async def run(self):
        start_time = time.time()
        
        async with await self.create_session() as session:

            companies = await self.fetch_companies(session)
            if not companies:
                return
            
            date_ranges = self.get_date_ranges()
            all_data = []
            tasks = []
            
            for company in companies:
                task = self.process_company(session, company, date_ranges)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            for company_data in results:
                all_data.extend(company_data)
            
            self.save_to_csv(all_data)
            
            elapsed_time = time.time() - start_time
            logger.info(f"Completed in {elapsed_time:.2f} seconds")

def main():
    scraper = MSEScraper()
    asyncio.run(scraper.run())

if __name__ == "__main__":
    main()
