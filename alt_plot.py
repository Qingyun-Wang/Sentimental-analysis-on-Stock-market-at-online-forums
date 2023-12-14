import seaborn as sns
import altair as alt
import pandas as pd
import re
import numpy as np
from datetime import datetime, timedelta

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
    
    if period_of_interest == "week":
        threthod_time = (datetime.today()- timedelta(days=7)).strftime('%Y-%m-%d')
    elif period_of_interest == "month":
        threthod_time = (datetime.today()- timedelta(days=30)).strftime('%Y-%m-%d')
    
    df_perios = df[df['Date'] >= threthod_time]
    graph = (
            alt.Chart(df_perios)
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

def clean_company_name(text):
    terms = ['Inc\.', 'Corporation', 'Company', 'plc', 'Limited', ',', 'and', '\.com', 'A/S', 'PLC', "'s"]
    pattern = r'(?:' + '|'.join(terms) + ')'
    # Replace the matched terms with an empty string
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text


def plot_recommendation_top_100(path_to_pric="data/top100_companies_data.csv", path_to_sentimental="data/reddit_fetched_post_top_100_score.csv"):
    stock_price = pd.read_csv(path_to_pric, index_col=0)
    stock_price = stock_price.rename(columns={"Company Name":"Company"})
    stock_price['Company'] = stock_price['Company'].apply(clean_company_name).apply(lambda x: x.strip())
    df = pd.read_csv(path_to_sentimental,index_col=0)

    df_sorted=df.sort_values('score', ascending=False)
    company_list = df_sorted['Company'].values
    company_list = company_list[company_list != "Top_100_avg"]

    price_change = np.array([float(stock_price[stock_price["Company"] == name]["% Change"].values[0].strip("%")) for name in company_list])
    df_price = pd.DataFrame({"Company": company_list, "percentage_change": price_change})

    merged_df = pd.merge(df,df_price,on="Company", how = 'inner').sort_values('score',ascending=False)
    merged_df['price_direction']=[1 if ele>0 else -1 for ele in merged_df['percentage_change']>0]
    merged_df['Sentimental_score']=[""]*len(merged_df)
    merged_df=merged_df.reset_index(drop=True)
    #merged_df['percentage_change']=[change if (change<=5 and change>=-5) else 5 if change>5 else -5 for change in merged_df['percentage_change']]
    chart1 = (
        alt.Chart(merged_df)
        .mark_bar(opacity=0.7)
        .encode(
            y=alt.Y('Company',sort='-x'),
            x=alt.X('score', scale=alt.Scale(domain=[-1, 2])),  
        # color=alt.Color('Sentimental_score')  
            color=alt.value('steelblue')  
        )
    )

    chart2 = (
        alt.Chart(merged_df)
        .mark_bar(opacity=0.5)
        .encode(
            y=alt.Y('Company', sort=alt.EncodingSortField(field='score', order='descending')), 
            x=alt.X('percentage_change', scale=alt.Scale(domain=[-1, 2])),
            color=alt.Color('price_direction:N', scale=alt.Scale(domain=[-1, 1], range=['green', 'red']), legend = None) # Different color for the 'percentage' bars
        )
    )

    return chart1+chart2