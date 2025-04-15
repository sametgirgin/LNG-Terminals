import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(
    page_title="European Gas Report",
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
        <h2 style="color: #007BFF; margin: 0;">European Gas Report</h2>
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

        # Filter the data
        filtered_df = df.copy()
        if selected_facility != 'All':
            filtered_df = filtered_df[filtered_df['FacilityType'] == selected_facility]
        if selected_status != 'All':
            filtered_df = filtered_df[filtered_df['Status'] == selected_status]
        if selected_owner != 'All':
            filtered_df = filtered_df[filtered_df['Owner'] == selected_owner]

        # Create the Plotly map
        if not filtered_df.empty:
            fig = px.scatter_mapbox(filtered_df, 
                                  lat="Latitude", 
                                  lon="Longitude",
                                  hover_name="TerminalName",
                                  hover_data=["State/Province", "Country", "Capacity", "CapacityUnits", 
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
        st.header("📚 Definitions and Terminology")
        st.markdown("This section provides definitions and explanations of terms used in the dataset.")
        
        # Display definitions with better formatting
        if not definitions_df.empty:
            # Add a search box for definitions
            search_term = st.text_input("🔍 Search definitions", "")
            
            if search_term:
                # Filter definitions based on search term
                filtered_definitions = definitions_df[
                    definitions_df.apply(lambda x: x.astype(str).str.contains(search_term, case=False)).any(axis=1)
                ]
            else:
                filtered_definitions = definitions_df
            
            # Display definitions in an expandable format
            for idx, row in filtered_definitions.iterrows():
                with st.expander(f"{row.iloc[0]}", expanded=False):
                    st.write(row.iloc[1])
    with tab3:
        st.header("ℹ️ About Us")
        
        # Add a container with custom styling for the about us text
        with st.container():
            st.markdown("""
            <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: justify;">
            <p style="font-size: 16px; line-height: 1.6;">
            Welcome to Sustainable Energy Analytics, your go-to source for insightful analysis and the latest developments 
            in the sustainable energy world. Our mission is to empower individuals, businesses, and policymakers with the 
            knowledge they need to make informed decisions for a sustainable future.
            </p>
            <p style="font-size: 16px; line-height: 1.6;">
            At Sustainable Energy Analytics, we cover a wide range of topics, including solar, wind, hydro, and geothermal 
            energy, as well as emerging technologies and innovative solutions driving the transition to a greener planet.
            </p>
            <p style="font-size: 16px; line-height: 1.6;">
            Our team of experts is dedicated to providing accurate data, in-depth research, and expert commentary to help 
            you stay ahead in the rapidly evolving energy landscape.
            </p>
            <p style="font-size: 16px; line-height: 1.6;">
            Join us on our journey towards a cleaner, more sustainable world. Together, we can make a difference.
            </p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.warning("Please ensure the Excel file 'LNG-Terminals-2024-01 GEM-GGIT-.xlsx' is in the same directory as the app.")
