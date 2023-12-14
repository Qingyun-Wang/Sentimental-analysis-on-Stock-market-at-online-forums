import streamlit as st

from data_collection import *
from sentimental_score_engine import *
from alt_plot import *


def app(company_list):

    st.title("Sentiment Analysis of Major Corporations in the Stock Market Using Online Forum Data")

    st.markdown(f"## Select the company you want to study")
  
    # Create a multiselect dropdown with search capability
    selected_options = st.multiselect(
                                        "Select your companies:",
                                        company_list,
                                        default=None,  # You can set default selections here if required
                                        help="Type to search and select multiple options"  # Optional help text
                                    )
    # Display the selected options
    companies = selected_options


    options = ["week", "month"]
    selected_option = st.selectbox(
                                        "Select your period of interest, please note that larger period will lead to longer calcualting time:",
                                        options,
                                        index=0,  # Default selected index (optional)
                                        help="Type to search and select an option"  # Optional help text
                                    )
     # Display the selected options
    period_of_interest = selected_option

    ##### Generate sentimental score
    df = pd.read_csv('data/reddit_fetched_post_score.csv', index_col=0)
    
    # Button to trigger calculation for selectbox
    if st.button(f'Click for report!'):
        if selected_options and selected_option:
            ##### Data sourcing
            companies = [clean_company_name(com.strip()) for com in companies]
            source_company_post_to_csv(companies, period_of_interest)
            ##### Generate sentimental score
            df = create_scored_data_history("data/reddit_fetched_post.csv", "data/reddit_fetched_post_top100_avg_score.csv", True)
            #### Plot
            chart = draw_score_lines_df(df, period_of_interest)
            st.write(chart)        
        else:
            st.write("Please complete the selections")
    st.markdown(""" 
                * The Top_100_avg above means the average score of all top-100 largest company in the market
    """)
 
    st.markdown(f"## Check the correlation between our sentimental score and real stock market movement, updated to {df['Date'].values.max()}")
    st.markdown(""" 
                * Red/green represent stock return for the date shown above. 
                * Blue represent sentimental score for the previous day, such that it will have the predictive power!
                * The score is calculated using exponential moving average with alpha = 0.3
    """)
    recommendation_chart = plot_recommendation_top_100(path_to_pric="data/top100_companies_data.csv", path_to_sentimental="data/reddit_fetched_post_top_100_score.csv")
    st.altair_chart(recommendation_chart, use_container_width=True)
    
    # Create a button in the sidebar
    if st.sidebar.button('Click Me to ferch new posts for all top-100 company up to date! May take from less than a second to 20s minutes to run depending on the number of post'):
        update_today_post_top100("data/reddit_fetched_post_top_100.csv", "data/top100_companies_data.csv")
        df = create_scored_data_history("data/reddit_fetched_post.csv", "data/reddit_fetched_post_top100_avg_score.csv", True)
        st.sidebar.write('Fetched!')

        
if __name__ == "__main__":
    #company_list = pd.read_csv("data/top100_name.csv",index_col=0)
    company_list = generate_top_100_company_name("data/top100_companies_data.csv")
    app(company_list)
    