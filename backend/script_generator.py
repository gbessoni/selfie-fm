import os
from anthropic import Anthropic

def generate_scripts(link_title, link_url, scraped_content):
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    system_prompt = "You are a professional copywriter and voice coach for creators. Your job is to write compelling 10-second voice intros that convert listeners into clickers. You write in a conversational, spoken tone. You focus on specific benefits, building trust, and creating urgency—all in 10 seconds. You never use corporate jargon. You never make false promises. You make the creator sound like a real person, not a robot. Every script you write should feel authentic and natural when spoken aloud."
    
    user_prompt = f"""You are writing a 10-second voice intro.

What they're sharing: {link_title}
Where it goes: {link_url}
Page content: {scraped_content[:500] if scraped_content else "No content available"}

Write 3 variations (50-70 words each):
1. Direct & Benefit-Focused - Lead with the value
2. Story/Personal - Make it relatable and human  
3. Urgent/FOMO - Create desire to click now

Each script must:
- Open with a hook
- State specific benefit
- Build trust
- End with clear CTA
- Sound natural when spoken

Output ONLY the 3 scripts separated by "---", no labels."""
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    
    scripts = response.content[0].text.split("---")
    return {
        "brief": scripts[0].strip() if len(scripts) > 0 else "",
        "standard": scripts[1].strip() if len(scripts) > 1 else "",
        "conversational": scripts[2].strip() if len(scripts) > 2 else ""
    }

def generate_link_scripts(url, title, description, preview_text, link_type, user_name):
    """
    Generate 3 script variations for a link
    Returns dict with brief, standard, conversational and their word counts
    """
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    system_prompt = "You are a professional copywriter and voice coach for creators. Your job is to write compelling 10-second voice intros that convert listeners into clickers. You write in a conversational, spoken tone. You focus on specific benefits, building trust, and creating urgency—all in 10 seconds. You never use corporate jargon. You never make false promises. You make the creator sound like a real person, not a robot. Every script you write should feel authentic and natural when spoken aloud."
    
    # Build context from available data
    context_parts = []
    if title:
        context_parts.append(f"Link title: {title}")
    if description:
        context_parts.append(f"Description: {description}")
    if preview_text:
        context_parts.append(f"Content preview: {preview_text[:300]}")
    if link_type:
        context_parts.append(f"Type: {link_type}")
    
    context = "\n".join(context_parts) if context_parts else "No additional context available"
    
    user_prompt = f"""You are {user_name} writing a 10-second voice intro for this link.

URL: {url}
{context}

Write 3 variations (50-70 words each):
1. Direct & Benefit-Focused - Lead with the value, what's in it for them
2. Story/Personal - Make it relatable and human, share a personal angle
3. Urgent/FOMO - Create desire to click now, limited time or opportunity

Each script must:
- Open with an attention-grabbing hook
- State the specific benefit or value
- Build trust and credibility
- End with a clear call-to-action
- Sound natural and conversational when spoken aloud
- Be exactly 50-70 words (aim for 10 seconds when spoken)

Output ONLY the 3 scripts separated by "---", no labels, no explanations."""
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    
    scripts_text = response.content[0].text.split("---")
    
    # Helper to count words
    def count_words(text):
        return len(text.strip().split())
    
    brief = scripts_text[0].strip() if len(scripts_text) > 0 else ""
    standard = scripts_text[1].strip() if len(scripts_text) > 1 else ""
    conversational = scripts_text[2].strip() if len(scripts_text) > 2 else ""
    
    return {
        "brief": brief,
        "brief_word_count": count_words(brief),
        "standard": standard,
        "standard_word_count": count_words(standard),
        "conversational": conversational,
        "conversational_word_count": count_words(conversational)
    }
