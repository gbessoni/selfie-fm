"""
AI Script Writer for selfie.fm
Generates sales scripts for links using AI (OpenAI or Anthropic)
"""
import os
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import logging
import re

logger = logging.getLogger(__name__)


class ScriptWriter:
    """AI-powered script writer for link pitches"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Use whichever API key is available
        if self.openai_api_key:
            self.provider = 'openai'
            logger.info("Using OpenAI for script generation")
        elif self.anthropic_api_key:
            self.provider = 'anthropic'
            logger.info("Using Anthropic for script generation")
        else:
            self.provider = None
            logger.warning("No AI API key configured. Script generation will not work.")
    
    def scrape_link_content(self, url: str) -> Dict[str, str]:
        """
        Scrape and analyze a link destination to extract key information
        
        Args:
            url: The destination URL to analyze
            
        Returns:
            Dict containing title, description, headings, and key text
        """
        try:
            logger.info(f"Scraping link content from: {url}")
            
            # Set up headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            # Fetch the page with timeout
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = ""
            if soup.title:
                title = soup.title.get_text().strip()
            
            # Extract meta description
            description = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'}) or \
                       soup.find('meta', property='og:description')
            if meta_desc:
                description = meta_desc.get('content', '').strip()
            
            # Extract headings (h1, h2)
            headings = []
            for tag in soup.find_all(['h1', 'h2'], limit=5):
                text = tag.get_text().strip()
                if text and len(text) > 3:
                    headings.append(text)
            
            # Extract key paragraphs
            paragraphs = []
            for p in soup.find_all('p', limit=10):
                text = p.get_text().strip()
                if text and len(text) > 20:
                    paragraphs.append(text)
            
            # Build scraped content summary
            content_parts = []
            if title:
                content_parts.append(f"Title: {title}")
            if description:
                content_parts.append(f"Description: {description}")
            if headings:
                content_parts.append(f"Key Headings: {' | '.join(headings[:3])}")
            if paragraphs:
                # Take first 2 paragraphs, limit length
                key_text = ' '.join(paragraphs[:2])[:500]
                content_parts.append(f"Content: {key_text}")
            
            scraped_content = '\n'.join(content_parts)
            
            logger.info(f"Successfully scraped content from {url}")
            logger.debug(f"Scraped content: {scraped_content[:200]}...")
            
            return {
                'title': title,
                'description': description,
                'headings': headings,
                'paragraphs': paragraphs[:3],
                'scraped_content': scraped_content
            }
            
        except requests.Timeout:
            logger.warning(f"Timeout scraping {url}")
            return {'scraped_content': 'Content could not be loaded (timeout)'}
        except requests.RequestException as e:
            logger.warning(f"Error scraping {url}: {e}")
            return {'scraped_content': 'Content could not be loaded'}
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}", exc_info=True)
            return {'scraped_content': 'Content could not be loaded'}
    
    def generate_pitch_script(
        self,
        link_url: str,
        link_title: str,
        scraped_content: str,
        user_business_context: Optional[str] = None
    ) -> str:
        """
        Generate a 10-second sales script for a link using AI
        
        Args:
            link_url: The destination URL
            link_title: User-provided link title
            scraped_content: Content scraped from the destination
            user_business_context: Optional context about user's business
            
        Returns:
            Generated script text (50 words max)
        """
        if not self.provider:
            raise ValueError("No AI API key configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY.")
        
        # Build the prompt
        prompt = self._build_prompt(link_url, link_title, scraped_content, user_business_context)
        
        # Generate with appropriate provider
        if self.provider == 'openai':
            return self._generate_with_openai(prompt)
        elif self.provider == 'anthropic':
            return self._generate_with_anthropic(prompt)
        else:
            raise ValueError("Invalid AI provider")
    
    def _build_prompt(
        self,
        link_url: str,
        link_title: str,
        scraped_content: str,
        user_business_context: Optional[str]
    ) -> str:
        """Build the AI prompt for script generation"""
        
        business_context = user_business_context or "No specific business context provided"
        
        prompt = f"""You are a master copywriter who writes direct, human, authentic copy - no hype, just clear value.

Write a 10-second voice script (50 words max) for this link.

Link: {link_title}
Destination: {link_url}
Page content: {scraped_content}
Business context: {business_context}

The script must:
- Address a specific pain point or desire
- Show urgency, social proof, or scarcity (if relevant)
- End with clear call-to-action
- Sound natural when spoken aloud
- Be conversational and authentic
- Be exactly 50 words or less

Write ONLY the script, no explanations or meta-commentary."""
        
        return prompt
    
    def _generate_with_openai(self, prompt: str) -> str:
        """Generate script using OpenAI API"""
        try:
            logger.info("Generating script with OpenAI")
            
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-4o-mini',
                'messages': [
                    {'role': 'system', 'content': 'You are an expert copywriter who creates authentic, direct sales scripts.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.7,
                'max_tokens': 150
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            script = result['choices'][0]['message']['content'].strip()
            
            # Clean up the script
            script = self._clean_script(script)
            
            logger.info(f"Generated script: {script}")
            return script
            
        except requests.RequestException as e:
            logger.error(f"OpenAI API error: {e}")
            raise ValueError(f"Failed to generate script with OpenAI: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating script: {e}", exc_info=True)
            raise ValueError(f"Failed to generate script: {str(e)}")
    
    def _generate_with_anthropic(self, prompt: str) -> str:
        """Generate script using Anthropic Claude API"""
        try:
            logger.info("Generating script with Anthropic Claude")
            
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                'x-api-key': self.anthropic_api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            }
            
            data = {
                'model': 'claude-3-5-sonnet-20240620',
                'max_tokens': 150,
                'messages': [
                    {'role': 'user', 'content': prompt}
                ]
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            script = result['content'][0]['text'].strip()
            
            # Clean up the script
            script = self._clean_script(script)
            
            logger.info(f"Generated script: {script}")
            return script
            
        except requests.RequestException as e:
            logger.error(f"Anthropic API error: {e}")
            raise ValueError(f"Failed to generate script with Anthropic: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating script: {e}", exc_info=True)
            raise ValueError(f"Failed to generate script: {str(e)}")
    
    def _clean_script(self, script: str) -> str:
        """Clean up generated script"""
        # Remove quotes if present
        script = script.strip('"\'')
        
        # Remove any meta-commentary
        lines = script.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # Skip lines that look like meta-commentary
            if line and not line.startswith(('Here', 'Note:', 'Script:', 'Remember')):
                cleaned_lines.append(line)
        
        script = ' '.join(cleaned_lines)
        
        # Limit to approximately 50 words
        words = script.split()
        if len(words) > 55:
            script = ' '.join(words[:50]) + '...'
        
        return script
    
    def generate_pitch_scripts(
        self,
        link_url: str,
        link_title: str,
        scraped_content: str,
        user_business_context: Optional[str] = None,
        num_options: int = 3
    ) -> list:
        """
        Generate multiple pitch script options for a link using AI
        
        Args:
            link_url: The destination URL
            link_title: User-provided link title
            scraped_content: Content scraped from the destination
            user_business_context: Optional context about user's business
            num_options: Number of script options to generate (default 3)
            
        Returns:
            List of dicts with 'script' and 'word_count' keys
        """
        if not self.provider:
            raise ValueError("No AI API key configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY.")
        
        # Build the prompt for multiple options
        prompt = self._build_multiple_scripts_prompt(
            link_url, link_title, scraped_content, user_business_context, num_options
        )
        
        # Generate with appropriate provider
        if self.provider == 'openai':
            scripts_text = self._generate_with_openai_multi(prompt)
        elif self.provider == 'anthropic':
            scripts_text = self._generate_with_anthropic_multi(prompt)
        else:
            raise ValueError("Invalid AI provider")
        
        # Parse the response into separate scripts
        scripts = self._parse_multiple_scripts(scripts_text, num_options)
        
        return scripts
    
    def _build_multiple_scripts_prompt(
        self,
        link_url: str,
        link_title: str,
        scraped_content: str,
        user_business_context: Optional[str],
        num_options: int
    ) -> str:
        """Build the AI prompt for generating multiple script options"""
        
        business_context = user_business_context or "No specific business context provided"
        
        prompt = f"""You are a master copywriter in the style of Seth Godin - direct, authentic, no hype.

Generate {num_options} different 10-second voice scripts (45-50 words each) for this link.

Link: {link_title}
Destination: {link_url}
Page content: {scraped_content}
Business context: {business_context}

Each script must:
- Address a specific pain point or desire
- Show urgency, social proof, or scarcity (if relevant)
- End with clear call-to-action
- Sound natural when spoken aloud
- Be conversational and authentic
- Be 45-50 words

Create {num_options} DIFFERENT approaches:
1. First script: Focus on emotional benefit/transformation
2. Second script: Focus on practical value/problem-solving
3. Third script: Focus on urgency/exclusivity

Format your response EXACTLY like this:

SCRIPT 1:
[script text here]

SCRIPT 2:
[script text here]

SCRIPT 3:
[script text here]

Write ONLY the scripts in this format, no explanations."""
        
        return prompt
    
    def _generate_with_openai_multi(self, prompt: str) -> str:
        """Generate multiple scripts using OpenAI API"""
        try:
            logger.info("Generating multiple scripts with OpenAI")
            
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-4o-mini',
                'messages': [
                    {'role': 'system', 'content': 'You are an expert copywriter who creates authentic, direct sales scripts in the style of Seth Godin.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.8,
                'max_tokens': 500
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            scripts_text = result['choices'][0]['message']['content'].strip()
            
            logger.info(f"Generated scripts response: {scripts_text[:200]}...")
            return scripts_text
            
        except requests.RequestException as e:
            logger.error(f"OpenAI API error: {e}")
            raise ValueError(f"Failed to generate scripts with OpenAI: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating scripts: {e}", exc_info=True)
            raise ValueError(f"Failed to generate scripts: {str(e)}")
    
    def _generate_with_anthropic_multi(self, prompt: str) -> str:
        """Generate multiple scripts using Anthropic Claude API"""
        try:
            logger.info("Generating multiple scripts with Anthropic Claude")
            
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                'x-api-key': self.anthropic_api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            }
            
            data = {
                'model': 'claude-3-5-sonnet-20240620',
                'max_tokens': 500,
                'temperature': 0.8,
                'messages': [
                    {'role': 'user', 'content': prompt}
                ]
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            scripts_text = result['content'][0]['text'].strip()
            
            logger.info(f"Generated scripts response: {scripts_text[:200]}...")
            return scripts_text
            
        except requests.RequestException as e:
            logger.error(f"Anthropic API error: {e}")
            raise ValueError(f"Failed to generate scripts with Anthropic: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating scripts: {e}", exc_info=True)
            raise ValueError(f"Failed to generate scripts: {str(e)}")
    
    def _parse_multiple_scripts(self, scripts_text: str, expected_count: int) -> list:
        """Parse the AI response into separate script objects"""
        scripts = []
        
        # Try to split by SCRIPT markers
        parts = re.split(r'SCRIPT\s+\d+:', scripts_text, flags=re.IGNORECASE)
        
        # Remove empty first element if present
        parts = [p.strip() for p in parts if p.strip()]
        
        # If we didn't get the expected format, try line breaks
        if len(parts) < expected_count:
            parts = [p.strip() for p in scripts_text.split('\n\n') if p.strip()]
        
        for i, script_text in enumerate(parts[:expected_count]):
            # Clean the script
            script = self._clean_script(script_text)
            
            # Count words
            word_count = len(script.split())
            
            scripts.append({
                'script': script,
                'word_count': word_count
            })
        
        # If we still don't have enough scripts, generate fallback
        while len(scripts) < expected_count:
            scripts.append({
                'script': f"Check out {parts[0][:50] if parts else 'this amazing offer'}... Click to learn more!",
                'word_count': 10
            })
        
        logger.info(f"Parsed {len(scripts)} scripts successfully")
        return scripts


# Global instance
script_writer = ScriptWriter()
