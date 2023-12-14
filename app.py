import streamlit as st

from data_collection import *
from sentimental_score_engine import *
from alt_plot import *


def app(company_list):
    st.title("Select the company you want to study")


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


    # Button to trigger calculation for selectbox
    if st.button(f'Get the Sentimental Analysis report for selected company in the last {period_of_interest} !'):
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

    


if __name__ == "__main__":
    #company_list = pd.read_csv("data/top100_name.csv",index_col=0)
    company_list = generate_top_100_company_name("data/top100_companies_data.csv")
    app(company_list)
    