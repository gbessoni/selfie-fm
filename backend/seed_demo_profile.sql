-- Seed script to create demo beauty influencer profile
-- Run with: sqlite3 voicetree.db < seed_demo_profile.sql

-- Delete existing demo user if exists
DELETE FROM link_clicks WHERE link_id IN (SELECT id FROM links WHERE user_id = (SELECT id FROM users WHERE username = 'beautybyluna'));
DELETE FROM profile_views WHERE user_id = (SELECT id FROM users WHERE username = 'beautybyluna');
DELETE FROM voice_messages WHERE user_id = (SELECT id FROM users WHERE username = 'beautybyluna');
DELETE FROM links WHERE user_id = (SELECT id FROM users WHERE username = 'beautybyluna');
DELETE FROM users WHERE username = 'beautybyluna';

-- Create demo user
-- Password is 'demo123' hashed with bcrypt
INSERT INTO users (
    username,
    email,
    password_hash,
    display_name,
    bio,
    avatar_url,
    banner_url,
    is_published,
    imported_from_linktree,
    voice_clone_id,
    voice_sample_path,
    welcome_message_text,
    welcome_message_audio,
    welcome_message_type,
    profile_views,
    total_link_clicks,
    voice_message_plays,
    auto_approve_voice,
    last_login,
    created_at,
    updated_at
) VALUES (
    'beautybyluna',
    'luna@beautybyluna.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5koiyZvVn3eHi', -- demo123
    'Luna Martinez',
    'Beauty creator | Skincare obsessed | Sharing my journey to glowing skin ✨',
    NULL,
    NULL,
    1,
    0,
    'demo_voice_id_placeholder',
    NULL,
    'Hey! Welcome to my beauty world. I''m so excited to share my favorite products and tips with you!',
    NULL,
    'static',
    247,
    89,
    156,
    1,
    datetime('now'),
    datetime('now'),
    datetime('now')
);

-- Create links with voice messages
INSERT INTO links (user_id, title, url, description, platform, voice_message_text, voice_message_audio, is_active, "order", click_count, created_at, updated_at)
VALUES
    (
        (SELECT id FROM users WHERE username = 'beautybyluna'),
        '📸 Instagram (@beautybyluna)',
        'https://instagram.com/beautybyluna',
        'Follow for daily skincare tips',
        'instagram',
        'Follow me on Instagram for daily skincare tips and real, unfiltered reviews of products I actually use',
        NULL,
        1,
        1,
        34,
        datetime('now'),
        datetime('now')
    ),
    (
        (SELECT id FROM users WHERE username = 'beautybyluna'),
        '🎥 YouTube Channel',
        'https://youtube.com/@beautybyluna',
        'In-depth tutorials and reviews',
        'youtube',
        'Subscribe to my YouTube for in-depth tutorials and my honest thoughts on trending beauty products',
        NULL,
        1,
        2,
        28,
        datetime('now'),
        datetime('now')
    ),
    (
        (SELECT id FROM users WHERE username = 'beautybyluna'),
        '💄 Amazon Storefront',
        'https://amazon.com/shop/beautybyluna',
        'My curated favorites',
        'amazon',
        'Check out my curated Amazon favorites - these are products I genuinely love and recommend',
        NULL,
        1,
        3,
        15,
        datetime('now'),
        datetime('now')
    ),
    (
        (SELECT id FROM users WHERE username = 'beautybyluna'),
        '✉️ Newsletter',
        'https://beautybyluna.substack.com',
        'Weekly beauty secrets',
        'substack',
        'Join my weekly newsletter where I share my current routines and insider beauty secrets',
        NULL,
        1,
        4,
        8,
        datetime('now'),
        datetime('now')
    ),
    (
        (SELECT id FROM users WHERE username = 'beautybyluna'),
        '🎙️ Podcast - "Glow Up Stories"',
        'https://podcasts.apple.com/glowupstories',
        'Beauty expert interviews',
        'podcast',
        'Listen to my podcast where I interview beauty experts and share real stories about self-confidence',
        NULL,
        1,
        5,
        3,
        datetime('now'),
        datetime('now')
    ),
    (
        (SELECT id FROM users WHERE username = 'beautybyluna'),
        '🛍️ Shop My Favorites',
        'https://shopmy.us/beautybyluna',
        'All my favorite products',
        'shopmy',
        'Browse my shop for all the products that have transformed my skin and makeup routine',
        NULL,
        1,
        6,
        1,
        datetime('now'),
        datetime('now')
    );

-- Verify the data was inserted
SELECT 'Demo profile created successfully!' as message;
SELECT 'Username: beautybyluna' as info;
SELECT 'Password: demo123' as info;
SELECT 'Profile URL: http://localhost:8000/beautybyluna' as info;
SELECT 'Login URL: http://localhost:8000/login' as info;
SELECT COUNT(*) || ' links created' as info FROM links WHERE user_id = (SELECT id FROM users WHERE username = 'beautybyluna');
