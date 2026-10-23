



import os
import sys
import requests
import random

ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.environ.get("INSTAGRAM_ACCOUNT_ID")

if not ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
    print("❌ ERROR: Missing required GitHub Secrets!")
    print(f"-> INSTAGRAM_ACCESS_TOKEN: {'Found' if ACCESS_TOKEN else 'MISSING'}")
    print(f"-> INSTAGRAM_ACCOUNT_ID: {'Found' if INSTAGRAM_ACCOUNT_ID else 'MISSING'}")
    sys.exit(1)

def generate_local_ai_reply(username, comment_text):
    """
    Queries your local Ollama instance running inside the 
    GitHub Action runner to query the Qwen model architecture.
    """
    print(f"🤖 Querying local Ollama server for @{username}...")
    ollama_url = "http://localhost:11434/api/generate"
    
    prompt = (
        f"A viewer named @{username} left this comment on your post: '{comment_text}'. "
        f"Write a creative, playful, and engaging reply (15-50 characters). "
        f"Use casual Instagram language with abbreviations like 'ur', 'u', 'bb', 'rn', 'fr'. "
        f"Make it feel genuine and conversational. "
        f"You can optionally add 1-2 emojis at the end, but prioritize TEXT over emojis. "
        f"\n\nExamples of good replies:\n"
        f"- Right back at ya girl 💕\n"
        f"- You're making me blush 😊\n"
        f"- This is why ur my fav 💖\n"
        f"- Says you! 🙈\n"
        f"- Look at u! \n"
        f"- That means the world coming from you 🥹\n"
        f"- You just leveled up my day \n"
        f"- Shh don't gas me 😂\n"
        f"- I'll take that compliment 💅\n"
        f"- Coming from you? 💕💕\n"
        f"- You know the vibes! ✨\n"
        f"- This comment hit different 🔥\n"
        f"- Very mindful, very demure 💅\n"
        f"- You're the real MVP \n"
        f"- Energy on 1000, thanks to u! ⚡\n"
        f"- Keep that energy coming! 💫\n"
        f"- Big shoutout to u! 🙌\n"
        f"- You get it! 💯\n"
        f"- Now we're talking! 🔥\n"
        f"- Feeling the love, appreciate u! 💕\n"
        f"- You're out here making my day! 😊\n"
        f"- Say it louder! 📢\n"
        f"- I love me too 😂\n"
        f"- Acting fine like wine 🍷\n"
        f"- Get a mirror! 🪞\n"
        f"- Says u pretty! 💖\n"
        f"- Shush ur perf! ✨\n"
        f"- Um no ur gorgeous! 😍\n"
        f"- Ur an angel! 👼\n"
        f"- Ur the best! 💯\n"
        f"- BRB crying 😭\n"
        f"- Uno reverse 🔄\n"
        f"- It's just the light ✨\n"
        f"- Don't boost my ego like that 😂\n"
        f"- I knew that already 💅\n"
        f"- No more than u are! 💕\n"
        f"- Learned from you! \n"
        f"- Trying my best! 💪\n"
        f"- I'm glad u love it! \n"
        f"- Awwh stooop it! \n"
        f"- I'll pick u up at 8 😂\n"
        f"\nWrite ONE reply that matches this vibe. Be creative and avoid generic 'thank you' responses."
    )
    
    payload = {
        "model": "qwen2.5:1.5b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 60,
            "temperature": 0.8,
            "top_p": 0.9
        }
    }
    
    try:
        response = requests.post(ollama_url, json=payload, timeout=30)
        if response.status_code == 200:
            ai_text = response.json().get("response", "").strip()
            # Remove quotes if present
            if ai_text.startswith('"') and ai_text.endswith('"'):
                ai_text = ai_text[1:-1]
            # Clean up newlines and extra spaces
            ai_text = ' '.join(ai_text.split())
            # Ensure it's not just emojis
            emoji_only = all(ord(c) > 127 or c.isspace() for c in ai_text if not c.isalnum())
            if emoji_only and len(ai_text) < 15:
                # Fallback to a text-based response
                fallbacks = [
                    "Right back at ya! 💕",
                    "You're the best! ",
                    "This means so much! 😊",
                    "Says you! 🙈",
                    "You get it! 💯",
                    "You know the vibes! ✨",
                    "Appreciate u! 💖",
                    "Ur amazing! 🌟"
                ]
                ai_text = random.choice(fallbacks)
            return ai_text
    except Exception as e:
        print(f"⚠️ Local Ollama inference failed ({e}). Falling back to baseline response.")
        
    # Better fallback with actual text
    fallbacks = [
        "Right back at ya! 💕",
        "You're making me blush! 😊",
        "This means the world! 🥹",
        "Says you! 🙈",
        "You get it! 💯",
        "You know the vibes! ✨",
        "Appreciate u! 💖",
        "Ur the best! 🌟"
    ]
    return random.choice(fallbacks)

def get_latest_media():
    """
    Tries the primary account media endpoint first. If it encounters a 404 or redirect,
    it automatically falls back to the universal 'me/media' node mapping.
    """
    url = f"https://graph.facebook.com/v20.0/{INSTAGRAM_ACCOUNT_ID}/media?fields=id,comments_count,permalink&access_token={ACCESS_TOKEN}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get('data', [])
            if data:
                latest = data[0]
                print(f"📸 Target Post Found ID: {latest['id']}")
                print(f"🔗 Post Permalink: {latest.get('permalink', 'N/A')}")
                print(f"📊 Meta Reports Comment Count: {latest.get('comments_count', 'Unknown')}")
                return latest
    except Exception as e:
        print(f"⚠️ Primary endpoint failed: {e}")

    print("⚠️ Primary endpoint failed or returned no data. Activating automatic universal fallback route...")
    
    fallback_url = f"https://graph.facebook.com/v20.0/me/media?fields=id,comments_count,permalink&access_token={ACCESS_TOKEN}"
    try:
        response = requests.get(fallback_url)
        response.raise_for_status()
        data = response.json().get('data', [])
        if data:
            latest = data[0]
            print(f"📸 Target Post Found ID (Fallback): {latest['id']}")
            print(f"📊 Meta Reports Comment Count: {latest.get('comments_count', 'Unknown')}")
            return latest
    except Exception as e:
        print(f"❌ Critical Error: All media discovery paths failed: {e}")
    return None

def reply_to_public_comment(comment_id, message_text):
    """
    Posts a public reply to a specific Instagram comment.
    """
    url = f"https://graph.facebook.com/v20.0/{comment_id}/replies"
    payload = {
        'message': message_text,
        'access_token': ACCESS_TOKEN
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print(f"✅ Replied to comment {comment_id}")
    except Exception as e:
        print(f"⚠️ Failed to reply to comment {comment_id}: {e}")

def has_bot_replied_to_this_comment(comment_id):
    """
    Checks the live sub-replies of this specific comment ID.
    Returns True only if our own account ID has already responded to it.
    """
    url = f"https://graph.facebook.com/v20.0/{comment_id}/replies?fields=from&access_token={ACCESS_TOKEN}"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            replies = res.json().get('data', [])
            for reply in replies:
                author = reply.get('from', {})
                if str(author.get('id')) == str(INSTAGRAM_ACCOUNT_ID):
                    return True
    except Exception:
        pass
    return False

def process_all_comments(media_id):
    """
    Fetches all comments for a given media ID and processes them.
    """
    url = f"https://graph.facebook.com/v20.0/{media_id}/comments?fields=id,text,from,hidden&access_token={ACCESS_TOKEN}"
    try:
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"❌ API Error Fetching Comments: HTTP {response.status_code}")
            print(f"🔍 Raw Response: {response.text}")
            return
            
        response.raise_for_status()
        response_json = response.json()
        comments = response_json.get('data', [])
        
        print(f"💬 Found {len(comments)} total comments to evaluate.")
        
        if len(comments) == 0:
            print(f"🔍 Raw API Response for Comments: {response_json}")
            if "error" in response_json:
                print(f"⚠️ Meta API Error Detected: {response_json['error'].get('message')}")
                print("👉 ACTION REQUIRED: Check your Access Token permissions in Meta App Dashboard.")
                print("   Required permissions: instagram_basic, instagram_manage_comments, pages_read_engagement")
            return
        
        for comment in comments:
            comment_id = comment.get('id')
            comment_text = comment.get('text', '')
            commenter = comment.get('from')
            
            if commenter:
                instagram_user_id = commenter.get('id')
                username = commenter.get('username', 'there')
                
                # Prevent the bot from talking to itself
                if str(instagram_user_id) == str(INSTAGRAM_ACCOUNT_ID):
                    continue
                
                # Deduplication Filter
                if has_bot_replied_to_this_comment(comment_id):
                    print(f"⏭️ Skipping comment ID {comment_id} from @{username} (Already replied).")
                    continue
                
                print(f"🚀 Processing comment from @{username}...")
                
                # Generate AI reply
                custom_ai_reply = generate_local_ai_reply(username, comment_text)
                print(f"✨ AI Reply Generated: {custom_ai_reply}")
                
                # Post public comment reply powered by local Qwen
                reply_to_public_comment(comment_id, custom_ai_reply)
                
    except Exception as e:
        print(f"❌ Error processing comments: {e}")

if __name__ == "__main__":
    print("🚀 Starting Instagram Comment Reply Bot...")
    latest_post = get_latest_media()
    if latest_post:
        process_all_comments(latest_post['id'])
    else:
        print("🤷 No recent posts found or API error occurred.")
