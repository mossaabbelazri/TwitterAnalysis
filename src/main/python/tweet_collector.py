import requests
import pandas as pd
from datetime import datetime
import os
import json
import time

def get_last_cursor(username, output_dir):
    """Get the last cursor from the existing CSV file"""
    filename = os.path.join(output_dir, f"{username}_tweets.csv")
    if os.path.exists(filename):
        try:
            # Read the last cursor from a separate file
            cursor_file = os.path.join(output_dir, f"{username}_last_cursor.txt")
            if os.path.exists(cursor_file):
                with open(cursor_file, 'r') as f:
                    return f.read().strip()
        except Exception as e:
            print(f"Error reading cursor file: {str(e)}")
    return None

def save_last_cursor(username, output_dir, cursor):
    """Save the last cursor to a file"""
    try:
        cursor_file = os.path.join(output_dir, f"{username}_last_cursor.txt")
        with open(cursor_file, 'w') as f:
            f.write(cursor)
    except Exception as e:
        print(f"Error saving cursor: {str(e)}")

def save_tweets_to_csv(tweets_data, username, output_dir, append=True):
    """Save tweets to CSV file, either appending or creating new file"""
    try:
        filename = os.path.join(output_dir, f"{username}_tweets.csv")
        df = pd.DataFrame(tweets_data)
        
        if append and os.path.exists(filename):
            # Read existing data
            existing_df = pd.read_csv(filename, dtype={'tweet_id': str})
            # Combine with new data
            combined_df = pd.concat([df, existing_df], ignore_index=True)
            # Sort by tweet_id in descending order (newest first)
            combined_df = combined_df.sort_values('tweet_id', ascending=False)
            # Remove duplicates
            combined_df = combined_df.drop_duplicates(subset=['tweet_id'])
            # Save back to file
            combined_df.to_csv(filename, index=False, encoding='utf-8')
            print(f"Appended {len(df)} new tweets to existing file")
        else:
            # Save new data
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"Created new file with {len(df)} tweets")
            
        return True
    except Exception as e:
        print(f"Error saving tweets to CSV: {str(e)}")
        return False

def collect_tweets(username, max_tweets=3000, start_cursor=None):
    """
    Collect tweets using TwitterAPI.io endpoint and save them to CSV
    Args:
        username: Twitter username
        max_tweets: Maximum number of tweets to collect
        start_cursor: Optional cursor to start from (for continuing collection)
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src', 'tweets','new1')
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Collecting tweets from {username}...")
        print("This might take a few minutes...")
        
        # TwitterAPI.io credentials
        API_KEY = "b3ac82fa626d40758252b02da6536eeb"
        
        # Headers for TwitterAPI.io requests
        headers = {
            "X-API-Key": API_KEY
        }
        
        # Get tweets using TwitterAPI.io
        tweets_url = "https://api.twitterapi.io/twitter/user/last_tweets"
        tweets_data = []
        seen_tweets = set()  # To track unique tweets
        retry_count = 0
        max_retries = 20
        base_delay = 5  # Base delay in seconds
        consecutive_rate_limits = 0
        max_consecutive_rate_limits = 10

        next_cursor = start_cursor
        has_next_page = True

        while has_next_page and len(tweets_data) < max_tweets:
            # Get tweets
            tweets_params = {
                "userId": "330262748",  # Fabrizio Romano's Twitter user ID
                "count": 30  # Request 30 tweets per batch
            }
            
            if next_cursor:
                tweets_params["cursor"] = next_cursor
                print(f"Continuing from cursor: {next_cursor}")
            
            print(f"Fetching tweets... (collected {len(tweets_data)} so far, target: {max_tweets})")
            
            try:
                # Add delay before request
                time.sleep(5)  # Wait 5 seconds before request
                tweets_response = requests.get(tweets_url, headers=headers, params=tweets_params)
                
                if tweets_response.status_code == 429:  # Rate limit hit
                    consecutive_rate_limits += 1
                    if consecutive_rate_limits >= max_consecutive_rate_limits:
                        print("Too many consecutive rate limits. Saving progress and stopping.")
                        break
                        
                    retry_count += 1
                    if retry_count > max_retries:
                        print("Max retries reached. Saving progress and stopping.")
                        break
                    
                    # Calculate delay with exponential backoff
                    delay = base_delay * (2 ** (retry_count - 1))
                    print(f"Rate limit hit. Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                    continue
                
                # Reset rate limit counters on successful request
                consecutive_rate_limits = 0
                retry_count = 0
                
                if tweets_response.status_code != 200:
                    print(f"Error: Failed to fetch tweets (status code: {tweets_response.status_code})")
                    print(f"Response: {tweets_response.text[:500]}")
                    break
                
                response_data = tweets_response.json()
                
                # Debug print the response structure
                print("\nResponse structure:")
                print(json.dumps(response_data, indent=2)[:1000])  # Print first 1000 chars of response
                
                if response_data.get('status') != 'success':
                    print(f"Error in API response: {response_data.get('msg', 'Unknown error')}")
                    break
                
                # Process pinned tweet if it exists and we haven't seen it before
                pinned_tweet = response_data.get('data', {}).get('pin_tweet')
                if pinned_tweet and pinned_tweet.get('id') not in seen_tweets:
                    tweet_id = str(pinned_tweet.get('id', ''))
                    seen_tweets.add(tweet_id)
                    tweet_data = {
                        'tweet_id': tweet_id,
                        'user': username,
                        'tweet': pinned_tweet.get('text', ''),
                        'date': pinned_tweet.get('createdAt', ''),
                        'likes': pinned_tweet.get('likeCount', 0),
                        'comments': pinned_tweet.get('replyCount', 0),
                        'repost': pinned_tweet.get('retweetCount', 0),
                        'views': pinned_tweet.get('viewCount', 0),
                        'quotes': pinned_tweet.get('quoteCount', 0),
                        'bookmarks': pinned_tweet.get('bookmarkCount', 0),
                        'is_pinned': True,
                        'is_retweet': False,
                        'is_reply': pinned_tweet.get('isReply', False),
                        'has_media': bool(pinned_tweet.get('extendedEntities', {}).get('media', [])),
                        'language': pinned_tweet.get('lang', ''),
                        'source': pinned_tweet.get('source', '')
                    }
                    tweets_data.append(tweet_data)
                    print(f"Collected pinned tweet {tweet_id}")
                
                # Process tweets from the timeline
                tweets = response_data.get('data', {}).get('tweets', [])
                if not tweets:
                    print("No tweets found in response")
                    break
                
                for tweet in tweets:
                    try:
                        tweet_id = str(tweet.get('id', ''))  # Convert to string
                        
                        if tweet_id and tweet_id not in seen_tweets:
                            seen_tweets.add(tweet_id)
                            tweet_info = {
                                'tweet_id': tweet_id,
                                'user': username,
                                'tweet': tweet.get('text', ''),
                                'date': tweet.get('createdAt', ''),
                                'likes': tweet.get('likeCount', 0),
                                'comments': tweet.get('replyCount', 0),
                                'repost': tweet.get('retweetCount', 0),
                                'views': tweet.get('viewCount', 0),
                                'quotes': tweet.get('quoteCount', 0),
                                'bookmarks': tweet.get('bookmarkCount', 0),
                                'is_pinned': False,
                                'is_retweet': False,
                                'is_reply': tweet.get('isReply', False),
                                'has_media': bool(tweet.get('extendedEntities', {}).get('media', [])),
                                'language': tweet.get('lang', ''),
                                'source': tweet.get('source', '')
                            }
                            tweets_data.append(tweet_info)
                            print(f"Collected tweet {tweet_id}")
                            
                            if len(tweets_data) >= max_tweets:
                                break
                    except Exception as e:
                        print(f"Error processing tweet: {str(e)}")
                        continue
                
                # Get next cursor for pagination
                has_next_page = response_data.get('has_next_page', False)
                next_cursor = response_data.get('next_cursor')
                
                print(f"\nPagination info:")
                print(f"Has next page: {has_next_page}")
                print(f"Next cursor: {next_cursor}")
                
                # Save the cursor for future use
                if next_cursor:
                    save_last_cursor(username, output_dir, next_cursor)
                
                if not has_next_page or not next_cursor:
                    print("No more pages available")
                    break
                
                # Save progress every 100 tweets
                if len(tweets_data) % 100 == 0 and tweets_data:
                    print(f"Saving progress... ({len(tweets_data)} tweets collected)")
                    save_tweets_to_csv(tweets_data, username, output_dir, append=True)
                
            except Exception as e:
                print(f"Error fetching tweets: {str(e)}")
                break
        
        if not tweets_data:
            print("No new tweets found")
            return None
        
        # Save final results
        save_tweets_to_csv(tweets_data, username, output_dir, append=True)
        
        print(f"\nCollected {len(tweets_data)} tweets")
        
        return pd.DataFrame(tweets_data)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    # Collect tweets
    username = "FabrizioRomano"
    
    # Start from the specific cursor
    start_cursor = "DAADDAABCgABGsdWZ0yXYJEKAAIZsMMlBdtBXQAIAAIAAAACCAADAAAAAAgABAAAAW8KAAUax1j-wwAnEAoABhrHWP7Cx9kAAAA"
    print(f"Starting from cursor: {start_cursor}")
    tweets_df = collect_tweets(username, max_tweets=3000, start_cursor=start_cursor)

    if tweets_df is not None:
        print("\nFirst few tweets:")
        print(tweets_df.head()) 