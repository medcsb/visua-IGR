import streamlit as st
import pandas as pd
import geopandas as gpd
import altair as alt

# --- Page Configuration ---
st.set_page_config(
    page_title="French Baby Names Dashboard",
    page_icon="👶",
    layout="wide"
)

# --- Data Loading ---
@st.cache_data
def load_data():
    """Loads and preprocesses the datasets."""
    # Load names data
    names_df = pd.read_csv("dpt2020.csv", sep=";")
    names_df = names_df[names_df['preusuel'] != '_PRENOMS_RARES']
    names_df = names_df[names_df['dpt'] != 'XX']
    names_df['annais'] = pd.to_numeric(names_df['annais'], errors='coerce')
    names_df['nombre'] = pd.to_numeric(names_df['nombre'], errors='coerce')
    names_df.dropna(subset=['annais', 'nombre', 'preusuel'], inplace=True)
    names_df['annais'] = names_df['annais'].astype(int)

    # Load geo data
    depts_gdf = gpd.read_file('departements-version-simplifiee.geojson')
    
    # Merge for visualizations that need it
    merged_df = depts_gdf.merge(names_df, how='right', left_on='code', right_on='dpt')
    
    return names_df, depts_gdf, merged_df

names_df, depts_gdf, merged_df = load_data()
alt.data_transformers.enable('json')

# --- Main App ---
st.title("French Baby Names Visualization Dashboard 👶")
st.markdown("This dashboard provides interactive visualizations of French baby name trends from 1900 to 2020. Use the tabs below to explore different aspects of the data.")

tab1, tab2, tab3 = st.tabs(["🏆 Top Names by Year", "🗺️ Name Popularity Map", "🚻 Gender Distribution"])

# --- Tab 1: Top Names by Year ---
with tab1:
    st.header("Top 15 Baby Names by Year")
    st.markdown("Use the slider to see the most popular names for a given year.")

    df_grouped = names_df.groupby(['annais', 'preusuel'])['nombre'].sum().reset_index()

    slider = alt.binding_range(min=int(df_grouped['annais'].min()), 
                              max=int(df_grouped['annais'].max()), 
                              step=1, 
                              name='Year: ')
    select_year = alt.param(bind=slider, value=2000)

    base = alt.Chart(df_grouped).add_params(
        select_year
    ).transform_filter(
        alt.datum.annais == select_year
    ).transform_window(
        rank='rank(nombre)',
        sort=[alt.SortField('nombre', order='descending')]
    ).transform_filter(
        alt.datum.rank <= 15
    )

    histogram = base.mark_bar(
        color='steelblue',
        stroke='white',
        strokeWidth=1
    ).encode(
        x=alt.X('nombre:Q', 
                title='Number of Births',
                scale=alt.Scale(nice=True)),
        y=alt.Y('preusuel:N', 
                title='Name',
                sort=alt.SortField('nombre', order='descending')),
        tooltip=['preusuel:N', 'nombre:Q', 'annais:O']
    )

    text = base.mark_text(
        align='left',
        baseline='middle',
        dx=3,
        fontSize=10,
        color='black'
    ).encode(
        x=alt.X('nombre:Q'),
        y=alt.Y('preusuel:N', sort=alt.SortField('nombre', order='descending')),
        text=alt.Text('nombre:Q', format='.0f')
    )

    chart1 = (histogram + text).properties(
        title=alt.TitleParams(
            text='Top 15 Baby Names',
            subtitle='Use the slider to explore different years',
            anchor='start'
        )
    )
    
    st.altair_chart(chart1, use_container_width=True)

# --- Tab 2: Name Popularity Map ---
with tab2:
    st.header("Most and Least Popular Names by Department")
    st.markdown("This map shows the most popular name for each department across all years. Hover over a department to see details.")

    grouped = names_df.groupby(['dpt', 'preusuel', 'sexe'], as_index=False).agg({'nombre': 'sum'})

    def get_extremes(df):
        max_row = df.loc[df['nombre'].idxmax()]
        min_row = df.loc[df['nombre'].idxmin()]
        return pd.Series({
            'max_name': max_row['preusuel'],
            'max_nombre': max_row['nombre'],
            'min_name': min_row['preusuel'],
            'min_nombre': min_row['nombre'],
        })

    extremes = grouped.groupby('dpt').apply(get_extremes).reset_index()

    merged_map_data = depts_gdf.merge(extremes, how='left', left_on='code', right_on='dpt')

    chart2 = alt.Chart(merged_map_data).mark_geoshape(stroke='white').encode(
        tooltip=['nom:N', 'max_name:N', 'max_nombre:Q', 'min_name:N', 'min_nombre:Q'],
        color=alt.Color('max_nombre:Q', legend=alt.Legend(title="Total births of most popular name"))
    ).properties(
        title="Most Popular Name by Department (All Years)"
    )
    
    st.altair_chart(chart2, use_container_width=True)

# --- Tab 3: Gender Distribution ---
with tab3:
    st.header("Gender Distribution of a Name Over Time")
    st.markdown("Select a name and a department to see the evolution of its gender distribution over the years.")

    col1, col2 = st.columns(2)
    with col1:
        all_names = sorted(names_df['preusuel'].unique())
        default_name = 'CAMILLE' if 'CAMILLE' in all_names else all_names[0]
        chosen_name = st.selectbox("Choose a name", options=all_names, index=all_names.index(default_name))

    with col2:
        all_depts = ['All'] + sorted(depts_gdf['nom'].unique().tolist())
        chosen_department = st.selectbox("Choose a department (or 'All')", options=all_depts)

    df_name = merged_df[merged_df['preusuel'].str.upper() == chosen_name.upper()]

    if chosen_department != 'All':
        df_name = df_name.loc[df_name['nom'] == chosen_department]

    if df_name.empty:
        st.warning(f"No data available for the name '{chosen_name}' with the selected filters.")
    else:
        grouped = df_name.groupby(['annais', 'sexe'])['nombre'].sum().reset_index()

        pivot = grouped.pivot(index='annais', columns='sexe', values='nombre').fillna(0)
        
        if 1 not in pivot.columns: pivot[1] = 0
        if 2 not in pivot.columns: pivot[2] = 0
            
        pivot = pivot.rename(columns={1: 'Boys', 2: 'Girls'})

        pivot['Total'] = pivot['Girls'] + pivot['Boys']
        
        pivot['% Girls'] = (pivot['Girls'] / pivot['Total']).fillna(0) * 100
        pivot['% Boys'] = (pivot['Boys'] / pivot['Total']).fillna(0) * 100

        plot_df = pivot[['% Girls', '% Boys']].reset_index().melt(id_vars='annais', 
                                                                  var_name='Sex', 
                                                                  value_name='Percentage')

        plot_df['Sex'] = plot_df['Sex'].map({'% Girls': 'Girls', '% Boys': 'Boys'})

        if chosen_department == 'All':
            title_str = f"Percentage of Boys and Girls Named {chosen_name.title()} Over Time in France"
        else:
            title_str = f"Percentage of Boys and Girls Named {chosen_name.title()} Over Time in {chosen_department}"

        chart3 = alt.Chart(plot_df).mark_line(point=True).encode(
            x=alt.X('annais:O', title='Year'),
            y=alt.Y('Percentage:Q', title='Percentage (%)', scale=alt.Scale(domain=[0, 100])),
            color='Sex:N',
            tooltip=['annais', 'Sex', 'Percentage']
        ).properties(
            title=title_str
        ).interactive()

        st.altair_chart(chart3, use_container_width=True)
