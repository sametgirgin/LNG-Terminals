import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="Global LNG Report",
    page_icon="🌍",
    layout="wide"
)

# Create two columns for the header
left_col, right_col = st.columns([4, 1])

# Add title, subtitle, and logo
with left_col:
    st.markdown(
        """
        <h1 style="color: #007BFF; margin: 0;">Sustainable Energy Analytics</h1>
        <h2 style="color: #007BFF; margin: 0;">Global LNG Report</h2>
        """,
        unsafe_allow_html=True
    )

with right_col:
    # Display the logo
    st.image("logo.png", width=50)  # Adjust the width as needed

# Function to load and process data
@st.cache_data
def load_data():
    # Load the main data from first sheet
    df = pd.read_excel('LNG-Terminals-2024-01 GEM-GGIT-.xlsx', sheet_name=0)
    
    # Load definitions from second sheet
    definitions_df = pd.read_excel('LNG-Terminals-2024-01 GEM-GGIT-.xlsx', sheet_name=1)
    
    # Data cleaning for main data
    df.dropna(subset=['Latitude', 'Longitude'], inplace=True)
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df = df[(df['Latitude'] >= -90) & (df['Latitude'] <= 90) &
            (df['Longitude'] >= -180) & (df['Longitude'] <= 180)]
    return df, definitions_df

# Function to load LNG buyer deals data
@st.cache_data
def load_buyer_seller_data():
    # Load the LNG buyer deals data
    deals_df = pd.read_excel('LONG TERM LNG BUYER DEALS.xlsx')
    
    # Ensure all country names are strings and handle missing values
    deals_df['Seller_Country'] = deals_df['Seller_Country'].fillna("Unknown").astype(str)
    deals_df['Buyer_Country'] = deals_df['Buyer_Country'].fillna("Unknown").astype(str)

    # Extract unique countries for geocoding
    countries = set(deals_df['Seller_Country'].unique()).union(deals_df['Buyer_Country'].unique())
    
    # Geocode countries to get their latitudes and longitudes
    geolocator = Nominatim(user_agent="lng_app")
    country_coords = {}
    for country in countries:
        try:
            location = geolocator.geocode(country, timeout=10)
            if location:
                country_coords[country] = (location.latitude, location.longitude)
        except GeocoderTimedOut:
            st.warning(f"Geocoding timed out for {country}.")
    
    return deals_df, country_coords

# Load the data
try:
    df, definitions_df = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    data_loaded = False

# Load the buyer and seller data
try:
    deals_df, country_coords = load_buyer_seller_data()
    buyer_seller_data_loaded = True
except Exception as e:
    st.error(f"Error loading buyer and seller data: {str(e)}")
    buyer_seller_data_loaded = False

if data_loaded and buyer_seller_data_loaded:
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📍 Map View", "📚 LNG Terminologies","🌍 Long-Term LNG Deals Map", "ℹ️ About Us"])
    
    with tab1:
        # Sidebar filters
        st.sidebar.header("Filters")

        # Create filters
        facility_types = ['All'] + sorted(df['FacilityType'].unique().tolist())
        selected_facility = st.sidebar.selectbox('Facility Type', facility_types)

        status_options = ['All'] + sorted(df['Status'].unique().tolist())
        selected_status = st.sidebar.selectbox('Status', status_options)

        owner_options = ['All'] + sorted(df['Owner'].unique().tolist())
        selected_owner = st.sidebar.selectbox('Owner', owner_options)

        country_options = ['All'] + sorted(df['Country'].unique().tolist())  # Add country filter
        selected_country = st.sidebar.selectbox('Country', country_options)

        # Filter the data
        filtered_df = df.copy()
        if selected_facility != 'All':
            filtered_df = filtered_df[filtered_df['FacilityType'] == selected_facility]
        if selected_status != 'All':
            filtered_df = filtered_df[filtered_df['Status'] == selected_status]
        if selected_owner != 'All':
            filtered_df = filtered_df[filtered_df['Owner'] == selected_owner]
        if selected_country != 'All':  # Apply country filter
            filtered_df = filtered_df[filtered_df['Country'] == selected_country]

        # Create the Plotly map
        if not filtered_df.empty:
            fig = px.scatter_mapbox(filtered_df, 
                                  lat="Latitude", 
                                  lon="Longitude",
                                  hover_name="TerminalName",
                                  hover_data=["State/Province", "Country", 
                                            "Status", "Owner", "Parent", "CapacityInMtpa", "CapacityInBcm/y"],
                                  color="Status",
                                  zoom=1,
                                  height=600)

            fig.update_layout(
                mapbox_style="open-street-map",
                margin={"r":0,"t":0,"l":0,"b":0}
            )
            fig.update_traces(marker=dict(size=8))

            # Display the map
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No terminals match the selected filters.")
            
    with tab2:
        #st.header("📚LNG Terminal Terminologies")
        # Add a container with custom styling for the about us text
        with st.container():
            # Read the Markdown content from the file
            with open("terminologies.md", "r") as file:
                about_us_content = file.read()
            
            # Display the Markdown content
            st.markdown(about_us_content, unsafe_allow_html=True)
    with tab3:
        #st.header("🌍 Long-Term LNG Deals Map")

        # Prepare data for the map
        country_roles = {}
        for _, row in deals_df.iterrows():
            seller = row['Seller_Country']
            buyer = row['Buyer_Country']

            # Track seller countries
            if seller not in country_roles:
                country_roles[seller] = {'Role': 'Seller', 'Deals': 0}
            country_roles[seller]['Deals'] += 1

            # Track buyer countries
            if buyer not in country_roles:
                country_roles[buyer] = {'Role': 'Buyer', 'Deals': 0}
            country_roles[buyer]['Deals'] += 1

            # If a country is both a buyer and seller, update its role
            if seller == buyer:
                country_roles[seller]['Role'] = 'Both'

        # Create a DataFrame for the country roles
        country_data = pd.DataFrame([
            {
                'Country': country,
                'Role': data['Role'],
                'Deals': data['Deals']
            }
            for country, data in country_roles.items()
        ])

        # Map roles to colors
        role_colors = {
            'Seller': 'aqua',
            'Buyer': 'lime',
            'Both': 'purple'
        }

        # Create the choropleth map
        fig = px.choropleth(
            country_data,
            locations="Country",
            locationmode="country names",
            color_continuous_scale="Viridis",
            color="Role",
            hover_name="Country",
            hover_data={"Deals": True, "Role": True},  # Include deal details in hover
            title="Buyer and Seller Countries",
            color_discrete_map=role_colors
        )

        # Update layout for a visually friendly map
        fig.update_layout(
            geo=dict(
                showland=True,
                landcolor="rgb(243, 243, 243)",
                showcountries=True,
                countrycolor="rgb(204, 204, 204)"
            ),
            title=dict(
                text="Buyer and Seller Countries",
                x=0.5,  # Center the title
                xanchor="center",
                font=dict(size=20)
            ),
            margin={"r": 0, "t": 50, "l": 0, "b": 0},  # Adjust margins
            height=700  # Increase height for better visibility
        )

        # Display the map
        st.plotly_chart(fig, use_container_width=True)

        # Create a dropdown with countries in ascending order
        selected_country = st.selectbox(
            "Select a Country to View Deal Details",
            options=sorted(set(deals_df['Seller_Country']).union(deals_df['Buyer_Country']))
        )

        # Display the deal details for the selected country
        if selected_country:
            st.subheader(f"Deals for {selected_country}")
            # Filter the DataFrame for the selected country
            filtered_deals = deals_df[
                (deals_df['Seller_Country'] == selected_country) | (deals_df['Buyer_Country'] == selected_country)
            ][['BUYER', 'SELLER', 'Buyer_Country', 'Seller_Country', 'VOLUME (bcf/day)', 'DURATION (years)', 'START', 'END']]
            
            # Display the filtered deals in a table
            st.dataframe(filtered_deals)    
               
    with tab4:
        st.header("ℹ️ About Us")
        
        # Add a container with custom styling for the about us text
        with st.container():
            # Read the Markdown content from the file
            with open("richtext_converted_to_markdown.md", "r") as file:
                about_us_content = file.read()
            
            # Display the Markdown content
            st.markdown(about_us_content, unsafe_allow_html=True)
    
else:
    st.warning("Please ensure the Excel file 'LNG-Terminals-2024-01 GEM-GGIT-.xlsx' and 'LONG TERM LNG BUYER DEALS.xlsx' are in the same directory as the app.")