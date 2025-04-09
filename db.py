# News + Tweet + Image logic

import requests
import urllib.parse


# 1. Get news
def get_news(niche="",pageSize=5, NEWS_API_KEY=""):
    """Rate Limit: 1 request / 3 sec per IP address
    Args:
        niche (str, optional): niche of news. Defaults to "".
        pageSize (int, optional): number of news to return. Defaults to 5.
        NEWS_API_KEY (str, optional): API key. Defaults to "".  
    """
    try:
        news_url = f"https://newsapi.org/v2/top-headlines?q={niche}&pageSize={pageSize}&apiKey={NEWS_API_KEY}"
        response = requests.get(news_url)
        news_data = response.json()
        if response.json()['totalResults']==0:
            return {}
        tweets = {index:row["title"] +" "+row['description'] for index,row in enumerate(news_data["articles"])}
        return tweets
    except Exception as e:
        print(e)

# 2. Generate Tweet
def get_tweet(top_headline=""):
    """1 req/3 sec means ~20 tweets/min max"""
    pollinations_url = "https://text.pollinations.ai/openai"
    payload = {
        "model": "openai",
        "messages": [
            {"role": "system", "content": "You are a social media expert. Rewrite the given news into a tweet (max 260 characters) with 2-3 relevant hashtags."},
            {"role": "user", "content": top_headline }
        ]
    }
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(pollinations_url, headers=headers, json=payload)
        tweet = response.json()["choices"][0]["message"]["content"]
        if tweet == "":
            tweet = top_headline
        if len(tweet)>260:
            tweet = tweet[:260]
        return tweet
    except Exception as e:
        print(e)

# 3. Generate Image (Image API)
def get_tweet_image(top_headline="blank"):
    pollinations_image_url = "https://image.pollinations.ai/prompt/"
    encoded_prompt = urllib.parse.quote(top_headline)  # Use headline as image prompt
    image_params = {
        "model": "flux",  # Default, can test others
        "width": 512,     # Smaller for speed, adjust as needed
        "height": 512,
        "nologo": "true", # No watermark
        "seed": 42        # Consistent results (optional)
    }

    image_url = f"{pollinations_image_url}{encoded_prompt}"
    try:
        image_response = requests.get(image_url, params=image_params)
        if image_response.status_code == 200 and 'image' in image_response.headers.get('Content-Type', ''):
            with open("news_image.jpg", "wb") as f:
                f.write(image_response.content)
            return "news_image.jpg"
        else:
            print(f"Image generation failed: {image_response.text}")
    except Exception as e:
        print(e)
