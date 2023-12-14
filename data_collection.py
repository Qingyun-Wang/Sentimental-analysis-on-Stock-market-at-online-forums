# Reddit
import praw
from datetime import datetime, timedelta
import pandas as pd
import time
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
import re

nltk.download('wordnet')

#### set up token and test

# Authentication, I should have hide these in the environmental variable, but since this is just a study case, I will leave them here for easy use.
reddit = praw.Reddit(
    client_id="bOUU3GVPswoqHAeWY-WB5g",
    client_secret="65G2ItcdbqJZU9pmGBC6303fYV-QJg",
    user_agent="script:sentimental_analysis:v1.0 (by /u/Legal_Advertising127)"
  #  username=''
)
subreddit = reddit.subreddit("python")


#### collect data
def rate_limited_request(subreddits, companies, effective_period, post_limit=50, comment_limit=20):
    data = []
    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        for company in companies:
            retry_wait = 20  # Initial wait time for 10 seconds
            while True:
                try:
                    count_post = 0
                    for post in subreddit.search(str(company), time_filter=effective_period):
                        post_time = datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d')
                        data.append([post.title + "\n" + post.selftext, post_time, company])
                        count_post += 1
                        count_comment = 0

                        try:
                            post.comments.replace_more(limit=0)
                            for comment in post.comments:
                                comment_time = datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d')
                                data.append([comment.body, comment_time, company])
                                count_comment += 1
                                if count_comment > comment_limit:
                                    break
                        except praw.exceptions.RedditAPIException as e:
                            print(f"Error fetching comments: {e}")
                            time.sleep(retry_wait)
                            retry_wait *= 2  # Exponential backoff

                        if count_post > post_limit:
                            break
                    break  # Break the while loop if no exception occurred
                except praw.exceptions.RedditAPIException as e:
                    print(f"Rate limit exceeded: {e}")
                    time.sleep(retry_wait)
                    retry_wait *= 2  # Exponential backoff
    return data


def collect_data_reddit(companies, effective_preriod):
    # List of stock market-related subreddits
    subreddits = ["stocks", "investing", "wallstreetbets", "StockMarket", "options", "SecurityAnalysis", "Daytrading"]
    data = rate_limited_request(subreddits, companies, effective_preriod)
    return data


# Function to get wordnet POS tag
def get_wordnet_pos(word):
    """Map POS tag to first character lemmatize() accepts"""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)


def clean_text(text):
    # Initialize the lemmatizer
    lemmatizer = WordNetLemmatizer()
    # Tokenize the text
    tokens = word_tokenize(text)
    # Get English stop words
    stop_words = set(stopwords.words('english'))
    # Filter out the stop words, non-letter tokens, and lemmatize
    filtered_text = [lemmatizer.lemmatize(word, get_wordnet_pos(word)) for word in tokens if word.isalpha() and word.lower() not in stop_words]
    # Rejoin filtered text
    filtered_sentence = ' '.join(filtered_text)
    return filtered_sentence


def save_to_csv_reddit(data, file_name):
    df = pd.DataFrame(data, columns=["Text", "Date", "Company"])
    df['Text'] = df['Text'].apply(clean_text)
    df = df.groupby(['Company','Date']).agg({"Text": lambda x: ' '.join(x.astype(str))}).reset_index()
    df = df[df['Text']!=""]
    save_file_name = 'data/reddit_'+file_name+'.csv'
    df.to_csv(save_file_name)
    return df


def clean_company_name(text):
    terms = ['Inc\.', 'Corporation', 'Company', 'plc', 'Limited', ',', 'and', '\.com', 'A/S', 'PLC', "'s"]
    pattern = r'(?:' + '|'.join(terms) + ')'
    text=text.strip()
    # Replace the matched terms with an empty string
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text


def generate_top_100_company_name(path):
    companies_100 = pd.read_csv(path, index_col=0)
    companies_100['Company'] = companies_100['Company Name'].apply(clean_company_name).apply(lambda x: x.strip())
    companies = list(companies_100['Company'].values)
    return companies


def source_company_post_to_csv_TOP100(path_to_100, period):

    companies = generate_top_100_company_name(path_to_100)
    data1 = collect_data_reddit(companies[:20], period)
    data2 = collect_data_reddit(companies[20:40], period)
    time.sleep(300)
    data3 = collect_data_reddit(companies[40:60], period)
    data4 = collect_data_reddit(companies[40:80], period)
    time.sleep(300)
    data5 = collect_data_reddit(companies[80:100], period)
    data = data1+data2+data3+data4+data5
    save_to_csv_reddit(data,"fetched_post_top_100")
    

def source_company_post_to_csv(companies, period, output_path="fetched_post"):
    company_post = collect_data_reddit(companies, period)
    save_to_csv_reddit(company_post, output_path)
    
    

def update_today_post_top100(previous_post_path, path_to_100):
    """
    update with the new post from last update
    """
    previous_data = pd.read_csv(previous_post_path, index_col=0)
    last_date_string = previous_data["Date"].max()
    last_date_time = datetime.strptime(last_date_string, '%Y-%m-%d')
    today_time = datetime.today()
    day_diff = (today_time - last_date_time).days
    if day_diff>0:
        if day_diff <=1:
            update_period = "day"
            sleep_time = 60
            #date_one_days_ago = today_time - timedelta(days=1)
            # Convert the date back to a string
            today_time_string = today_time.strftime('%Y-%m-%d')
            previous_data_correted = previous_data[previous_data['Date']< today_time_string]

        elif day_diff <= 7 and day_diff > 1:
            update_period = "week"
            sleep_time = 120
            # Subtract 7 days
            date_seven_days_ago = today_time - timedelta(days=7)
            # Convert the date back to a string
            date_seven_days_ago_str = date_seven_days_ago.strftime('%Y-%m-%d')
            previous_data_correted = previous_data[previous_data['Date']< date_seven_days_ago_str]

        elif day_diff>7 and day_diff<=30:
            update_period = 'month'
            sleep_time = 300
            date_30_days_ago = today_time - timedelta(days=30)
            # Convert the date back to a string
            date_30_days_ago = date_30_days_ago.strftime('%Y-%m-%d')
            previous_data_correted = previous_data[previous_data['Date']< date_30_days_ago]

        
        companies = generate_top_100_company_name(path_to_100)
        #print('start fetch', update_period)
        data1 = collect_data_reddit(companies[:20], update_period)
        data2 = collect_data_reddit(companies[20:40], update_period)
        #print('fetchign -1', f"sleep at {datetime.today()}")
        time.sleep(sleep_time)
        #print("end sleep", f"wakeup at {datetime.today()}")
        data3 = collect_data_reddit(companies[40:60], update_period)
        data4 = collect_data_reddit(companies[40:80], update_period)
        #print('fetchign -2')
        time.sleep(sleep_time)
        data5 = collect_data_reddit(companies[80:100], update_period)
        #print('fetched')
        data = data1+data2+data3+data4+data5
        df = pd.DataFrame(data, columns=["Text", "Date", "Company"])
        df['Text'] = df['Text'].apply(clean_text)
        df = df.groupby(['Company','Date']).agg({"Text": lambda x: ' '.join(x.astype(str))}).reset_index()
        df = df[df['Text']!=""]

        data_updated = pd.concat([previous_data_correted, df])

        save_to_csv_reddit(data_updated,"fetched_post_top_100")
