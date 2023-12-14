import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

nltk.download('vader_lexicon', quiet=True)


def load_csv(path):
    data = pd.read_csv(path, index_col=0)
    return data

def get_raw_scored(path):
    sia = SentimentIntensityAnalyzer()
    data = load_csv(path)
    data['score'] = data['Text'].apply(sia.polarity_scores).apply(lambda x: x['compound'])
    return data

def calculate_ema(group, history, alpha):
    if not history:
        return group.ewm(alpha=alpha).mean().iloc[-1]
    else:
        return group.ewm(alpha=alpha).mean()
def get_ewm_score(df, df_100_emavg, his=False, alpha_value = 0.3):
    # Function to apply EMA on each group and return a single value

    ema_result = df.groupby('Company')['score'].apply(lambda x: calculate_ema(x, his, alpha_value))
    if not his:
        data_pre = {"Company": ema_result.index, "score": ema_result.values}
        new_row = pd.DataFrame({'Company': ['Top_100_avg'], 'score': df_100_emavg.values[-1]})
    else:
        data_pre = {"Company": [ele[0] for ele in ema_result.index.values],'Date':df['Date'], "score": ema_result.values}
        new_row = pd.DataFrame({'Company': ['Top_100_avg']*len(df_100_emavg), 'Date':df_100_emavg.index.values, 'score': df_100_emavg.values[:,0]})

    df_emavg = pd.DataFrame(data_pre)
    df_emavg = pd.concat([df_emavg, new_row], ignore_index=True)
    
    return df_emavg

def save_score(df, name = "fetched_post_score"):

    save_file_name = 'data/reddit_'+ name +'.csv'

    df.to_csv(save_file_name)

# get the ewme score for the top 100 together
def create_avg_score_top100_company(path, alpha_value):
    df_100 = get_raw_scored(path)
    df_100_emavg = df_100.groupby('Date')['score'].apply(lambda x: calculate_ema(x, False, alpha_value))
    df_100_emavg.to_csv("data/reddit_fetched_post_top100_avg_score.csv")

# get ewme score for the requested company
def create_scored_data_history(path, path_to_top_100, history=True, alpha_value=0.3):
    df_100_emavg = pd.read_csv(path_to_top_100, index_col=0)
    df = get_raw_scored(path)
    df_emavg=get_ewm_score(df, df_100_emavg, history, alpha_value=alpha_value)
    save_score(df_emavg)
    return df_emavg

# get the ewme score for each top 100 company
def create_recommendation_top100(path, path_to_top_100, history=False, alpha_value=0.3):
    df_100_emavg = pd.read_csv(path_to_top_100, index_col=0)
    df = get_raw_scored(path)
    
    # only consider the score up to last day, since later we will use this score to compare with today's stock price return
    last_date_string = df["Date"].max()
    last_date_time = datetime.strptime(last_date_string, '%Y-%m-%d')- timedelta(days=1)
    last_date_time_str = last_date_time.strftime('%Y-%m-%d')
    df = df[df['Date']< last_date_time_str]

    df_emavg=get_ewm_score(df, df_100_emavg, history, alpha_value=alpha_value)
    save_score(df_emavg, name = "fetched_post_top_100_score")
    return df_emavg


#create_avg_score_top100_company('data/reddit_fetched_post_top_100.csv', .3)
#create_scored_data_history("data/reddit_fetched_post.csv", "data/reddit_fetched_post_top100_avg_score.csv", True)
#create_scored_data_history("data/reddit_fetched_post.csv", "data/reddit_top100_avg_score.csv", False)
#create_scored_data_history("data/reddit_fetched_post.csv", "data/reddit_top100_avg_score.csv", True)




