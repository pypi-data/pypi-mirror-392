"""
Yahoo Finance web scraper (no API, direct HTML parsing)
"""
from typing import Optional, List
from datetime import datetime
import random
import time

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None

from .base import BaseProvider
from ..models import Quote, HistoricalData
from ..core import ProviderRateLimiter
from ..config import Config


class YahooScraperProvider(BaseProvider):
    """Yahoo Finance web scraper provider"""
    
    def __init__(self, rate_limiter: Optional[ProviderRateLimiter] = None):
        super().__init__("yahoo_scraper")
        self.rate_limiter = rate_limiter
        self.session = None
        
        if requests is None or BeautifulSoup is None:
            self._available = False
            self._last_error = "requests or beautifulsoup4 not installed"
        else:
            self._init_session()
    
    def _init_session(self):
        """Initialize requests session with headers"""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": random.choice(Config.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })
    
    def _rotate_user_agent(self):
        """Rotate user agent to avoid detection"""
        self.session.headers["User-Agent"] = random.choice(Config.USER_AGENTS)
    
    def get_quote(self, symbol: str) -> Optional[Quote]:
        """Get real-time quote by scraping Yahoo Finance"""
        if not self._available:
            return None
        
        try:
            if self.rate_limiter:
                self.rate_limiter.wait_if_needed("yahoo_scraper")
            
            self._rotate_user_agent()
            
            url = f"https://finance.yahoo.com/quote/{symbol}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract price - Yahoo's structure changes often, try multiple selectors
            price = None
            price_selectors = [
                'fin-streamer[data-symbol="{}"][data-field="regularMarketPrice"]',
                'span[data-reactid*="regularMarketPrice"]',
                'div[data-test="qsp-price"] span',
            ]
            
            for selector in price_selectors:
                try:
                    elem = soup.select_one(selector.format(symbol))
                    if elem:
                        price_text = elem.get('value') or elem.text.strip()
                        price = float(price_text.replace(',', ''))
                        break
                except:
                    continue
            
            if not price:
                return None
            
            # Try to extract additional data
            quote = Quote(
                symbol=symbol,
                timestamp=datetime.now(),
                price=price,
                source="yahoo_scraper"
            )
            
            # Try to get more data from the page
            try:
                # Previous close
                prev_close_elem = soup.select_one('td[data-test="PREV_CLOSE-value"]')
                if prev_close_elem:
                    quote.previous_close = float(prev_close_elem.text.replace(',', ''))
                
                # Open
                open_elem = soup.select_one('td[data-test="OPEN-value"]')
                if open_elem:
                    quote.open = float(open_elem.text.replace(',', ''))
                
                # Day range
                range_elem = soup.select_one('td[data-test="DAYS_RANGE-value"]')
                if range_elem:
                    range_text = range_elem.text
                    if ' - ' in range_text:
                        low, high = range_text.split(' - ')
                        quote.low = float(low.replace(',', ''))
                        quote.high = float(high.replace(',', ''))
                
                # Volume
                volume_elem = soup.select_one('td[data-test="TD_VOLUME-value"]')
                if volume_elem:
                    volume_text = volume_elem.text.replace(',', '')
                    # Handle M, B suffixes
                    if 'M' in volume_text:
                        quote.volume = int(float(volume_text.replace('M', '')) * 1_000_000)
                    elif 'B' in volume_text:
                        quote.volume = int(float(volume_text.replace('B', '')) * 1_000_000_000)
                    else:
                        quote.volume = int(volume_text)
                
                # Market cap
                mcap_elem = soup.select_one('td[data-test="MARKET_CAP-value"]')
                if mcap_elem:
                    mcap_text = mcap_elem.text.replace(',', '')
                    if 'T' in mcap_text:
                        quote.market_cap = float(mcap_text.replace('T', '')) * 1_000_000_000_000
                    elif 'B' in mcap_text:
                        quote.market_cap = float(mcap_text.replace('B', '')) * 1_000_000_000
                    elif 'M' in mcap_text:
                        quote.market_cap = float(mcap_text.replace('M', '')) * 1_000_000
                
            except Exception as e:
                # If we got the price, continue with partial data
                pass
            
            return quote
            
        except Exception as e:
            self._handle_error(e, f"get_quote({symbol})")
            return None
    
    def get_historical(self,
                      symbol: str,
                      start: datetime,
                      end: datetime,
                      interval: str = "1d") -> Optional[HistoricalData]:
        """Get historical data - scraping historical data is complex, not implemented"""
        # For historical data, better to use API providers
        self._last_error = "Historical scraping not implemented, use API providers"
        return None
    
    def get_multiple_quotes(self, symbols: List[str]) -> List[Quote]:
        """Get quotes for multiple symbols"""
        quotes = []
        
        for symbol in symbols:
            quote = self.get_quote(symbol)
            if quote:
                quotes.append(quote)
            # Add small delay between requests
            time.sleep(random.uniform(0.5, 1.5))
        
        return quotes
