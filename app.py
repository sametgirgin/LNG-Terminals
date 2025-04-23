import streamlit as st
import pandas as pd
import plotly.express as px

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

# Load the data
try:
    df, definitions_df = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    data_loaded = False

if data_loaded:
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📍 Map View", "📚 Definitions", "ℹ️ About Us"])
    
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
        st.header("📚LNG Terminal Terminologies")
        # Add a container with custom styling for the about us text
        with st.container():
            # Read the Markdown content from the file
            with open("terminologies.md", "r") as file:
                about_us_content = file.read()
            
            # Display the Markdown content
            st.markdown(about_us_content, unsafe_allow_html=True)
        
    with tab3:
        st.header("ℹ️ About Us")
        
        # Add a container with custom styling for the about us text
        with st.container():
            # Read the Markdown content from the file
            with open("richtext_converted_to_markdown.md", "r") as file:
                about_us_content = file.read()
            
            # Display the Markdown content
            st.markdown(about_us_content, unsafe_allow_html=True)
else:
    st.warning("Please ensure the Excel file 'LNG-Terminals-2024-01 GEM-GGIT-.xlsx' is in the same directory as the app.")
