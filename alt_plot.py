import seaborn as sns
import altair as alt
import pandas as pd
import re
import numpy as np
def draw_one_company_score(path, company_name):
    df = pd.read_csv(path, index_col=0)
    opacity_map = {
        company_name: 1.0,
        'Top_100_avg': 0.5,
    }
    df['opacity'] = df['Company'].map(opacity_map)
    graph = (
            alt.Chart(df)
            .mark_line()
            .encode(x='Date',y='score',color='Company',
                    opacity=alt.Opacity('opacity', legend=None)  
                    )
            ) 
    return graph
def draw_score_lines(path):
    df = pd.read_csv(path, index_col=0)
    def opacity_map(name):
        if name == "Top_100_avg":
            return 0.5
        else:
            return 1
    df['opacity'] = df['Company'].map(opacity_map)
    graph = (
            alt.Chart(df)
            .mark_line()
            .encode(x='Date',y='score',color='Company',
                    opacity=alt.Opacity('opacity', legend=None)  
                    )
            ) 
    return graph

def draw_score_lines_df(df, period_of_interest):
    def opacity_map(name):
        if name == "Top_100_avg":
            return 0.5
        else:
            return 1
    df['opacity'] = df['Company'].map(opacity_map)
    graph = (
            alt.Chart(df)
            .mark_line()
            .encode(x='Date',y='score',color='Company',
                    opacity=alt.Opacity('opacity', legend=None)  
                    )
            .properties(
                            title=f'Sentiment in the past {period_of_interest}'
                        )
            ) 
    return graph


#draw_score_lines('data/reddit_fetched_post_score.csv')