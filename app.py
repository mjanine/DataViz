import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# --- PAGE SETUP ---
st.set_page_config(page_title="Sports Analytics & Performance Scout", layout="wide")
st.title("🏀 Sports Analytics & Performance Scout")
st.markdown("**Project ID:** DV-2026-GROUP-06 | **Authors:** Brent Gabriel De Castro & Mariella Janine Sola")
st.markdown("Exploring the evolution of physical archetypes and their correlation to NBA Clutch Performance (2012-2024).")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    return pd.read_csv("G6_Cleaned_NBA_Clutch_Data.csv")

df = load_data()

# ==========================================
# VISUALIZATION 1: STACKED AREA CHART (TRENDS)
# ==========================================
st.divider()
st.header("Key Question 1: The Pace-and-Space Evolution")
st.markdown("**Objective:** How has the share of late-game scoring efficiency shifted among different physical archetypes over the last decade?")

# Data Prep for Area Chart
area_data = df.groupby(['SEASON_START_YEAR', 'PHYSICAL_ARCHETYPE'])['PTS'].sum().reset_index()

# Plotly Stacked Area Chart (Highly Interactive)
fig_area = px.area(
    area_data,
    x="SEASON_START_YEAR",
    y="PTS",
    color="PHYSICAL_ARCHETYPE",
    color_discrete_sequence=px.colors.qualitative.Set2,
    title="Trend Analysis: Total Clutch Points by Physical Archetype (2012-2023)",
    labels={"SEASON_START_YEAR": "Season Start Year", "PTS": "Total Clutch Points"}
)

# Force yearly ticks for clarity
fig_area.update_xaxes(dtick=1)

# Display chart
st.plotly_chart(fig_area, theme="streamlit", width='stretch')

# Professional Explanation Box
st.info("**Narrative Annotation:** Despite the league's heavy shift toward a faster, three-point heavy 'pace-and-space' style, heavier/power archetypes continue to account for a massive share of total clutch scoring. This proves that size remains a highly durable asset in high-pressure, half-court game scenarios.", icon="💡")

# ==========================================
# VISUALIZATION 2 & 3: CORRELATIONS & REGRESSION
# ==========================================
st.divider()
st.header("Key Question 2: Physical Traits vs. Effectiveness")
st.markdown("**Objective:** To what extent do physical traits (BMI/Weight) correlate with a player's effectiveness in high-pressure situations?")

# --- SIDEBAR FILTER ---
st.sidebar.header("Filter by Era")
st.sidebar.markdown("Use this slider to facet the data by time period to see how correlations evolve over eras.")

min_year = int(df['SEASON_START_YEAR'].min())
max_year = int(df['SEASON_START_YEAR'].max())

selected_years = st.sidebar.slider(
    "Select Season Range:",
    min_year,
    max_year,
    (min_year, max_year)
)

# Filter dataframe based on user interaction
era_df = df[
    (df['SEASON_START_YEAR'] >= selected_years[0]) &
    (df['SEASON_START_YEAR'] <= selected_years[1])
]

# Force Matplotlib to use a dark theme so text/axes match Streamlit
plt.style.use('dark_background')

col1, col2 = st.columns(2)

# --------------------------
# SCATTER + REGRESSION
# --------------------------
with col1:
    st.subheader("Scatter Plot with Regression")

    # Check if 'PLAYER_NAME' is in your dataset so we can show it when hovering!
    hover_cols = ['PLAYER_NAME'] if 'PLAYER_NAME' in era_df.columns else None

    # Glow-up: Interactive Plotly Scatter with Tooltips and Regression
    fig1 = px.scatter(
        era_df,
        x='BMI',
        y='PTS_PER_MIN',
        hover_data=hover_cols,
        color_discrete_sequence=['#00b4d8'],
        opacity=0.5,
        trendline="ols",
        trendline_color_override='#ff006e',
        title=f"BMI vs Scoring Efficiency ({selected_years[0]}-{selected_years[1]})",
        labels={"BMI": "Body Mass Index (BMI)", "PTS_PER_MIN": "Clutch Points Per Minute"}
    )

    # Force background to be transparent
    fig1.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", 
        paper_bgcolor="rgba(0,0,0,0)",
        title_font_size=14
    )

    # Draw the interactive chart
    st.plotly_chart(fig1, theme="streamlit", width='stretch')

    # --- DYNAMIC NARRATIVE ---
    era_corr = era_df['BMI'].corr(era_df['PTS_PER_MIN'])

    if era_corr > 0.15:
        story = f"The regression line shows a **notable positive correlation ({era_corr:.2f})**. In this era, heavier players capitalized effectively on mismatches late in the game."
    elif era_corr > 0:
        story = f"The regression line is relatively flat **({era_corr:.2f})**. Size provided only a marginal advantage in this period."
    else:
        story = f"The trend flips **({era_corr:.2f})**. Higher BMI reduced efficiency, suggesting quicker players dominated clutch moments."

    st.info(f"**Dynamic Insight ({selected_years[0]}-{selected_years[1]}):** {story}", icon="📊")

# --------------------------
# HEATMAP
# --------------------------
with col2:
    st.subheader("Correlation Matrix (Heatmap)")

    matrix_cols = [
        'PLAYER_HEIGHT_INCHES',
        'PLAYER_WEIGHT',
        'BMI',
        'MIN',
        'PTS',
        'PTS_PER_MIN',
        'PLUS_MINUS'
    ]

    corr_data = era_df[matrix_cols].corr()

    # Glow-up: Interactive Plotly Heatmap
    fig2 = px.imshow(
        corr_data,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="Tealgrn",
        zmin=-1, 
        zmax=1,
        title=f"Metric Correlations ({selected_years[0]}-{selected_years[1]})"
    )

    # Force background to be transparent
    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        title_font_size=14
    )

    # Draw the interactive chart
    st.plotly_chart(fig2, theme="streamlit", width='stretch')

    # --- DYNAMIC NARRATIVE ---
    pm_weight_corr = corr_data.loc['PLUS_MINUS', 'PLAYER_WEIGHT']

    if pm_weight_corr > 0.15:
        heatmap_story = f"The correlation is **{pm_weight_corr:.2f}**, showing a clear advantage for heavier players. This indicates that in this era, traditional 'big men' were crucial for winning close games, likely dominating through rebounding, paint protection, and setting hard screens in slower half-court sets."
    elif pm_weight_corr > 0:
        heatmap_story = f"The correlation is **{pm_weight_corr:.2f}**, which is practically zero. This means sheer physical weight did not automatically translate to winning. During this era, 'pace-and-space' tactics likely neutralized heavy players, as their interior advantages were cancelled out by being too slow to defend the perimeter."
    else:
        heatmap_story = f"The correlation is negative (**{pm_weight_corr:.2f}**). In this timeframe, being heavier was actually a liability in the clutch. Teams likely utilized 'small ball' lineups, targeting and exposing slower, heavier players on defense during high-pressure pick-and-rolls."

    st.info(
        f"**Dynamic Insight ({selected_years[0]}-{selected_years[1]}):** "
        f"Look at the Weight vs. Plus/Minus square. {heatmap_story}",
        icon="🔍"
    )

# ==========================================
# FINAL CONCLUSION (DYNAMIC SYNTHESIS)
# ==========================================
st.divider()
st.subheader("🏆 Final Answer: Does Size Matter in the Clutch?")

# Combine both metrics to generate a synthesized final verdict
if era_corr > 0.05 and pm_weight_corr > 0.05:
    final_verdict = f"**Yes.** Between {selected_years[0]} and {selected_years[1]}, physical size was a distinct advantage. Heavier players not only scored more efficiently (Correlation: {era_corr:.2f}) but their presence on the floor directly correlated with winning outcomes and positive Plus/Minus (Correlation: {pm_weight_corr:.2f})."
elif era_corr <= 0.05 and pm_weight_corr > 0.05:
    final_verdict = f"**It's complicated.** Between {selected_years[0]} and {selected_years[1]}, heavier players weren't necessarily the most efficient scorers (Correlation: {era_corr:.2f}). However, their sheer physical presence still strongly contributed to winning outcomes (Plus/Minus Correlation: {pm_weight_corr:.2f}), likely through unselfish play like screen-setting and rebounding."
elif era_corr > 0.05 and pm_weight_corr <= 0.05:
    final_verdict = f"**Offensively, yes. Overall, no.** Between {selected_years[0]} and {selected_years[1]}, heavier players remained highly efficient scorers (Correlation: {era_corr:.2f}). But interestingly, their weight did not translate to winning the game (Plus/Minus Correlation: {pm_weight_corr:.2f}), suggesting their defensive liabilities in space outweighed their offensive output."
else:
    final_verdict = f"**No.** During the {selected_years[0]}-{selected_years[1]} period, the 'pace-and-space' era fully marginalized traditional size. Heavier players saw almost no advantage in scoring efficiency (Correlation: {era_corr:.2f}), nor did their weight correlate with winning close games (Plus/Minus Correlation: {pm_weight_corr:.2f}). Speed and shooting dominated."

# Display the verdict in a prominent success box
st.success(final_verdict, icon="✅")