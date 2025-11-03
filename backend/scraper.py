"""
Linktree scraper module for VoiceTree
Scrapes Linktree pages to extract user information and links
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, List
import re
import logging

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LinktreeScraper:
    """Scraper for Linktree profiles"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def extract_username_from_url(self, url: str) -> str:
        """Extract username from Linktree URL"""
        url = url.strip().rstrip('/')
        url = re.sub(r'^https?://', '', url)
        url = re.sub(r'^www\.', '', url)
        
        if 'linktr.ee/' in url:
            username = url.split('linktr.ee/')[-1]
        else:
            username = url.split('/')[-1]
        
        logger.info(f"Extracted username: {username}")
        return username.lower()
    
    def scrape_linktree(self, url: str) -> Dict:
        """
        Scrape a Linktree page and extract profile information and links
        
        Args:
            url: Linktree profile URL
            
        Returns:
            Dict containing username, display_name, bio, and links
        """
        try:
            logger.info(f"Starting to scrape Linktree URL: {url}")
            
            # Normalize URL
            if not url.startswith('http'):
                url = f'https://linktr.ee/{url}'
            
            logger.info(f"Normalized URL: {url}")
            
            # Extract username
            username = self.extract_username_from_url(url)
            
            # Fetch the page
            logger.info("Fetching page...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response length: {len(response.text)} characters")
            
            # Parse HTML
            logger.info("=" * 80)
            logger.info("PARSING HTML CONTENT")
            logger.info("=" * 80)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Log HTML structure overview
            logger.info(f"HTML Structure Overview:")
            logger.info(f"  - Total elements: {len(soup.find_all())}")
            logger.info(f"  - Total <a> tags: {len(soup.find_all('a'))}")
            logger.info(f"  - Total <div> tags: {len(soup.find_all('div'))}")
            logger.info(f"  - Total <script> tags: {len(soup.find_all('script'))}")
            
            # Log sample of HTML structure (first 1000 chars of body)
            body = soup.find('body')
            if body:
                body_preview = str(body)[:1000]
                logger.info(f"Body HTML Preview (first 1000 chars):\n{body_preview}")
            else:
                logger.warning("No <body> tag found in HTML!")
            
            # Debug: Save HTML to file for inspection
            try:
                with open('/tmp/linktree_debug.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                logger.info("Saved HTML to /tmp/linktree_debug.html for inspection")
            except Exception as e:
                logger.warning(f"Could not save debug HTML: {e}")
            
            # Extract display name
            display_name = username
            title_tag = soup.find('title')
            if title_tag:
                title_text = title_tag.get_text()
                logger.info(f"Found title: {title_text}")
                if '|' in title_text:
                    display_name = title_text.split('|')[0].strip()
                elif 'Linktree' in title_text:
                    display_name = title_text.replace('Linktree', '').strip()
            
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                display_name = og_title['content']
                logger.info(f"Found og:title: {display_name}")
            
            # Extract bio
            bio = ""
            og_description = soup.find('meta', property='og:description')
            if og_description and og_description.get('content'):
                bio = og_description['content']
                logger.info(f"Found bio: {bio}")
            
            # Debug: Log all meta tags
            meta_tags = soup.find_all('meta')
            logger.info(f"Found {len(meta_tags)} meta tags")
            for meta in meta_tags[:10]:  # Log first 10
                logger.debug(f"Meta tag: {meta}")
            
            # Extract links - try multiple strategies
            links = []
            
            logger.info("=" * 80)
            logger.info("EXTRACTING LINKS - TRYING MULTIPLE STRATEGIES")
            logger.info("=" * 80)
            
            # Strategy 1: Look for data-testid attributes
            logger.info("\n>>> STRATEGY 1: data-testid attributes")
            logger.info("Selector: a[data-testid*=\"link\"]")
            link_elements = soup.select('a[data-testid*="link"]')
            logger.info(f"Result: Found {len(link_elements)} links with data-testid")
            if link_elements:
                for idx, elem in enumerate(link_elements[:3]):
                    logger.info(f"  Sample link {idx+1}: {elem.get('href', 'NO HREF')} - {elem.get_text(strip=True)[:50]}")
            
            # Strategy 2: Look for common Linktree class names
            if not link_elements:
                logger.info("\n>>> STRATEGY 2: class-based selectors")
                selectors = [
                    'a[class*="Link"]',
                    'a[class*="link"]',
                    'div[class*="LinkButton"] a',
                    'div[id*="link"] a'
                ]
                for selector in selectors:
                    logger.info(f"  Trying selector: '{selector}'")
                    link_elements = soup.select(selector)
                    logger.info(f"  Result: Found {len(link_elements)} elements")
                    if link_elements:
                        logger.info(f"  ✓ SUCCESS with selector: '{selector}'")
                        for idx, elem in enumerate(link_elements[:3]):
                            logger.info(f"    Sample link {idx+1}: {elem.get('href', 'NO HREF')} - {elem.get_text(strip=True)[:50]}")
                        break
                    else:
                        logger.info(f"  ✗ No matches")
            
            # Strategy 3: Look in script tags for JSON data
            if not link_elements:
                logger.info("\n>>> STRATEGY 3: JSON data in script tags")
                script_tags = soup.find_all('script', type='application/ld+json')
                logger.info(f"  JSON-LD scripts: {len(script_tags)}")
                for idx, script in enumerate(script_tags):
                    preview = script.string[:200] if script.string else 'None'
                    logger.info(f"  Script {idx+1} preview: {preview}")
                
                # Look for __NEXT_DATA__ which Linktree often uses
                next_data_scripts = soup.find_all('script', id='__NEXT_DATA__')
                logger.info(f"  __NEXT_DATA__ scripts: {len(next_data_scripts)}")
                if next_data_scripts:
                    import json
                    try:
                        logger.info("  Attempting to parse __NEXT_DATA__...")
                        data = json.loads(next_data_scripts[0].string)
                        logger.info("  ✓ Successfully parsed __NEXT_DATA__")
                        logger.info(f"  Top-level keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
                        
                        # Try to extract links from the data structure
                        if 'props' in data and 'pageProps' in data['props']:
                            page_props = data['props']['pageProps']
                            logger.info(f"  pageProps keys: {list(page_props.keys())}")
                            if 'account' in page_props:
                                account = page_props['account']
                                logger.info(f"  ✓ Found account data")
                                logger.info(f"  Account keys: {list(account.keys()) if isinstance(account, dict) else 'not a dict'}")
                                
                                # Extract display name
                                if 'profilePictureUrl' in account or 'username' in account:
                                    display_name = account.get('pageTitle') or account.get('username') or username
                                    bio = account.get('description', bio)
                                    logger.info(f"  Extracted from JSON - Display name: {display_name}, Bio: {bio[:50] if bio else 'None'}")
                                
                                # Extract links
                                if 'links' in account:
                                    logger.info(f"  ✓ Found {len(account['links'])} links in JSON data")
                                    for idx, link_data in enumerate(account['links']):
                                        if isinstance(link_data, dict):
                                            link_url = link_data.get('url', '')
                                            link_title = link_data.get('title', '')
                                            logger.info(f"    Link {idx+1}: {link_title} -> {link_url}")
                                            if link_url and link_title:
                                                links.append({
                                                    'title': link_title,
                                                    'url': link_url
                                                })
                                else:
                                    logger.warning("  ✗ No 'links' key in account data")
                            else:
                                logger.warning("  ✗ No 'account' key in pageProps")
                        else:
                            logger.warning("  ✗ No 'props.pageProps' structure in __NEXT_DATA__")
                    except json.JSONDecodeError as e:
                        logger.error(f"  ✗ Failed to parse JSON data: {e}")
                    except Exception as e:
                        logger.error(f"  ✗ Error extracting data from __NEXT_DATA__: {e}", exc_info=True)
            
            # Strategy 4: Generic link extraction as fallback
            if not links and not link_elements:
                logger.info("\n>>> STRATEGY 4: generic link extraction (fallback)")
                logger.info("Selector: a[href]:not([href^=\"#\"]):not([href^=\"javascript\"])")
                link_elements = soup.select('a[href]:not([href^="#"]):not([href^="javascript"])')
                logger.info(f"Result: Found {len(link_elements)} generic links")
                if link_elements:
                    for idx, elem in enumerate(link_elements[:5]):
                        logger.info(f"  Link {idx+1}: {elem.get('href', 'NO HREF')} - {elem.get_text(strip=True)[:50]}")
            
            # Process link elements if we have any
            if link_elements and not links:
                logger.info("=" * 80)
                logger.info(f"PROCESSING {len(link_elements)} LINK ELEMENTS")
                logger.info("=" * 80)
                for idx, link in enumerate(link_elements):
                    href = link.get('href', '')
                    title = link.get_text(strip=True)
                    
                    logger.info(f"Link {idx+1}/{len(link_elements)}: title='{title}', href='{href}'")
                    
                    if not href or not title or len(title) < 2:
                        logger.debug(f"  ✗ Skipped - invalid href or title")
                        continue
                    
                    # Skip common non-content links
                    skip_keywords = ['cookie', 'privacy', 'terms', 'report', 'about', 'help']
                    if any(keyword in title.lower() for keyword in skip_keywords):
                        logger.debug(f"  ✗ Skipped - matches skip keyword: {title}")
                        continue
                    
                    if href.startswith('http') or href.startswith('//'):
                        if href.startswith('//'):
                            href = 'https:' + href
                        
                        # Skip Linktree's own URLs
                        if 'linktr.ee' in href or 'linktree.com' in href:
                            logger.debug(f"  ✗ Skipped - Linktree URL")
                            continue
                        
                        if not any(l['url'] == href for l in links):
                            links.append({
                                'title': title,
                                'url': href
                            })
                            logger.info(f"  ✓ Added link: {title}")
                        else:
                            logger.debug(f"  ✗ Duplicate link")
            
            logger.info("=" * 80)
            logger.info("SCRAPING RESULTS")
            logger.info("=" * 80)
            logger.info(f"Username: {username}")
            logger.info(f"Display Name: {display_name or username}")
            logger.info(f"Bio: {bio[:100] if bio else 'None'}")
            logger.info(f"Total links found: {len(links)}")
            logger.info("\nAll extracted links:")
            for idx, link in enumerate(links):
                logger.info(f"  {idx+1}. {link['title']} -> {link['url']}")
            
            result = {
                'username': username,
                'display_name': display_name or username,
                'bio': bio,
                'links': links[:20]
            }
            
            logger.info("=" * 80)
            logger.info(f"✓ SCRAPING COMPLETED SUCCESSFULLY - {len(links)} links extracted")
            logger.info("=" * 80)
            return result
            
        except requests.Timeout as e:
            logger.error(f"Timeout error while fetching {url}: {str(e)}")
            raise Exception(f"Request timeout: The Linktree page took too long to respond. Please try again.")
        except requests.ConnectionError as e:
            logger.error(f"Connection error while fetching {url}: {str(e)}")
            raise Exception(f"Connection error: Unable to reach Linktree. Please check your internet connection.")
        except requests.HTTPError as e:
            logger.error(f"HTTP error while fetching {url}: {e.response.status_code} - {str(e)}")
            if e.response.status_code == 404:
                raise Exception(f"Profile not found: The Linktree profile '{username}' does not exist.")
            elif e.response.status_code == 403:
                raise Exception(f"Access forbidden: Unable to access this Linktree profile.")
            elif e.response.status_code >= 500:
                raise Exception(f"Linktree server error: The Linktree service is currently unavailable. Please try again later.")
            else:
                raise Exception(f"HTTP error {e.response.status_code}: Unable to fetch the Linktree page.")
        except requests.RequestException as e:
            logger.error(f"Request error while fetching {url}: {str(e)}", exc_info=True)
            raise Exception(f"Failed to fetch Linktree page: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}", exc_info=True)
            raise Exception(f"Error parsing Linktree data: The page structure may have changed.")
        except Exception as e:
            logger.error(f"Unexpected error while scraping {url}: {str(e)}", exc_info=True)
            raise Exception(f"Error scraping Linktree: {str(e)}")


scraper = LinktreeScraper()
