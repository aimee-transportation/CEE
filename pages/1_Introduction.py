import streamlit as st

def main():
    st.title("Analyzing the Effects of Ride Sharing on Urban Mobility")
    
    # Introduction Section
    st.header("Introduction")
    st.write(
        "There is a need for a detailed analysis to understand the effects of ride sharing on urban mobility. Since we were only given the data for Uber for 2014-2015, we took a look at the month of June and the peak hour of transportation from 5-6PM. The project's motivation comes from claims of ride-sharing services impacting urban traffic congestion in NYC. The goal of this project is to see if Uber and other ride share services are creating a difference in taxi pickups and traffic congestion."
    )
    
    # Attributes analyzed section
    st.header("Attirbutes analyzed")
    st.write(
        "We analyzed taxi data based on Borough, 2012 Median Income (USD), and Borough Code to understand ride-sharing trends. Borough classification helps identify areas where certain taxis are allowed to operate, median income provides context to assess affordability and accessibility for residents, and borough codes were used to organize and sort data in an organized matter."
    )

# Load image from a URL
    st.image('https://cdn.prod.website-files.com/63ff9cd42186283f0e990e08/65d635cda06cdba37c76afa6_MOZCO%20Mateusz%20Szymanski%20Getty%20Images.jpg', caption='Uber', use_container_width=True)

    
if __name__ == "__main__":
    main()

