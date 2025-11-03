"""
Enhanced Web Scraper with Content Extraction
Scrapes destination pages to extract title, meta description, and first 200 words
"""
import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Optional
from urllib.parse import urlparse

class EnhancedScraper:
    """Enhanced scraper that extracts page content for AI script generation"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_page_content(self, url: str) -> Dict[str, Optional[str]]:
        """
        Scrape a page and extract title, meta description, and first 200 words
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dictionary with keys: title, meta_description, preview_text, full_content
        """
        result = {
            'title': None,
            'meta_description': None,
            'preview_text': None,
            'full_content': None
        }
        
        try:
            # Fetch the page
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title_tag = soup.find('title')
            if title_tag:
                result['title'] = title_tag.get_text().strip()
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if not meta_desc:
                meta_desc = soup.find('meta', property='og:description')
            if meta_desc:
                result['meta_description'] = meta_desc.get('content', '').strip()
            
            # Extract main text content
            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'header', 'footer']):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Store full content
            result['full_content'] = text
            
            # Extract first 200 words
            words = text.split()
            if len(words) > 200:
                preview_words = words[:200]
                result['preview_text'] = ' '.join(preview_words) + '...'
            else:
                result['preview_text'] = text
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Error scraping {url}: {e}")
            return result
        except Exception as e:
            print(f"Unexpected error scraping {url}: {e}")
            return result
    
    def identify_link_type(self, url: str, content: Dict[str, Optional[str]]) -> str:
        """
        Identify the type of link based on URL and content
        
        Returns one of: course, coaching, product, newsletter, blog, video, social, website
        """
        url_lower = url.lower()
        title = (content.get('title') or '').lower()
        description = (content.get('meta_description') or '').lower()
        preview = (content.get('preview_text') or '').lower()
        
        combined = f"{url_lower} {title} {description} {preview}"
        
        # Check for specific patterns
        if any(word in combined for word in ['course', 'learn', 'lesson', 'module', 'curriculum', 'training']):
            return 'course'
        
        if any(word in combined for word in ['coaching', 'mentorship', '1-on-1', 'one-on-one', 'consultation']):
            return 'coaching'
        
        if any(word in combined for word in ['product', 'buy', 'shop', 'store', 'purchase', 'price', '$', 'cart']):
            return 'product'
        
        if any(word in combined for word in ['newsletter', 'subscribe', 'email list', 'weekly digest']):
            return 'newsletter'
        
        if any(word in combined for word in ['blog', 'article', 'post', 'read']):
            return 'blog'
        
        if 'youtube.com' in url_lower or 'vimeo.com' in url_lower or 'video' in combined:
            return 'video'
        
        # Check for social media platforms
        social_platforms = ['instagram', 'twitter', 'facebook', 'linkedin', 'tiktok', 'youtube']
        for platform in social_platforms:
            if platform in url_lower:
                return 'social'
        
        return 'website'
    
    def create_context_summary(self, content: Dict[str, Optional[str]], link_type: str) -> str:
        """
        Create a concise summary for AI script generation
        """
        parts = []
        
        if content.get('title'):
            parts.append(f"Title: {content['title']}")
        
        if content.get('meta_description'):
            parts.append(f"Description: {content['meta_description']}")
        
        parts.append(f"Link Type: {link_type}")
        
        if content.get('preview_text'):
            # Limit preview to 100 words for context
            words = content['preview_text'].split()[:100]
            preview = ' '.join(words)
            parts.append(f"Preview: {preview}")
        
        return '\n'.join(parts)

def scrape_link_content(url: str) -> Dict[str, Optional[str]]:
    """
    Convenience function to scrape a link and return all extracted content
    """
    scraper = EnhancedScraper()
    content = scraper.scrape_page_content(url)
    link_type = scraper.identify_link_type(url, content)
    content['link_type'] = link_type
    content['context_summary'] = scraper.create_context_summary(content, link_type)
    return content

if __name__ == "__main__":
    # Test the scraper
    test_url = "https://www.example.com"
    print(f"Testing scraper with: {test_url}")
    result = scrape_link_content(test_url)
    print(f"\nTitle: {result['title']}")
    print(f"Meta Description: {result['meta_description']}")
    print(f"Link Type: {result['link_type']}")
    print(f"\nPreview (first 200 words):\n{result['preview_text'][:200]}...")
