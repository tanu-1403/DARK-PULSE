import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- Page setup ---
st.set_page_config(
    page_title="DarkPulse: Terrorism Analytics Dashboard",
    layout="wide"
)

# --- Background + Style ---
st.markdown("""
<style>
/* Whole background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(
        rgba(10,10,10,0.85), rgba(20,20,20,0.95)
    ),
    url('https://images.unsplash.com/photo-1600101021653-cf2b00a9f6b8?auto=format&fit=crop&w=1600&q=80');
    background-size: cover;
    background-attachment: fixed;
    background-position: center;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(20, 20, 20, 0.9);
}

/* Text colors */
h1, h2, h3, h4, h5, h6, p, div, span {
    color: #f5f5f5 !important;
    font-family: 'Segoe UI', sans-serif;
}

.block-container {
    padding-top: 1.5rem;
}
</style>

        /* KPI Cards */
        [data-testid="stMetricValue"] {
            color: #f0f0f0 !important;
            font-weight: 700 !important;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: rgba(20,20,20,0.85);
            backdrop-filter: blur(6px);
        }

        /* Charts */
        .plotly {
            background-color: rgba(255,255,255,0);
        }

        /* Subheaders */
        h2, h3 {
            color: #fafafa !important;
            border-left: 4px solid #cc4444;
            padding-left: 10px;
            margin-top: 40px;
        }
    </style>
""", unsafe_allow_html=True)

# --- HEADER / HERO SECTION ---
st.markdown("""
    <div style='text-align:center; margin-top: -30px;'>
        <h1>🌑 DarkPulse</h1>
        <p style='font-size:1.1rem; color:#cccccc;'>
            Illuminating unseen patterns in a world shadowed by fear.
        </p>
        <hr style='border: 0.5px solid rgba(255,255,255,0.2); width:60%; margin:auto;'>
    </div>
""", unsafe_allow_html=True)

#!/usr/bin/env python
# coding: utf-8

# In[15]:


# darkpulse_streamlit.py
# Streamlit app for visualizing Global

# ----------------------
# Load GTD dataset
# ----------------------

CSV_PATH = "https://drive.google.com/file/d/1fzYJnNk24rQn_hOwiahtCRreYYXwgNkI/view?usp=drive_link"
try:
    # Load CSV into DataFrame
    df = pd.read_csv(CSV_PATH)
    
except Exception as e:
    st.error(f"Failed to load data: {e}")
    df = pd.DataFrame()  # Empty fallback


# In[18]:


@st.cache_data
def load_data(path):
    cols = [
        "eventid", "Date", "country_txt", "region_txt", "provstate", "city",
        "latitude", "longitude", "attacktype1_txt", "targtype1_txt", "weaptype1_txt",
        "gname", "nkill", "nwound", "success", "suicide"
    ]

    try:
        df = pd.read_csv(path, encoding="ISO-8859-1", low_memory=False)
        df = df[[c for c in cols if c in df.columns]]
    except Exception:
        st.warning("⚠️ GTD CSV not found. Using sample data.")
        df = pd.DataFrame({
            "eventid": [1, 2, 3, 4, 5],
            "Date": pd.to_datetime(
                ["2001-09-11", "2005-06-15", "2010-01-05", "2015-12-20", "2019-07-03"]
            ),
            "country_txt": ["USA", "Iraq", "India", "Syria", "Nigeria"],
            "region_txt": ["North America", "Middle East & North Africa", "South Asia",
                           "Middle East & North Africa", "Sub-Saharan Africa"],
            "city": ["NY", "Baghdad", "Mumbai", "Aleppo", "Lagos"],
            "latitude": [40.7, 33.3, 19.0, 36.2, 6.5],
            "longitude": [-74, 44, 72, 37, 3],
            "attacktype1_txt": ["Bombing/Explosion", "Armed Assault", "Bombing/Explosion",
                                "Assassination", "Bombing/Explosion"],
            "targtype1_txt": ["Civilians", "Military", "Civilians", "Government", "Civilians"],
            "weaptype1_txt": ["Explosives", "Firearms", "Explosives", "Firearms", "Explosives"],
            "gname": ["Unknown", "Group A", "Group B", "Group C", "Group D"],
            "nkill": [3000, 150, 12, 500, 30],
            "nwound": [6000, 200, 30, 1000, 50],
            "success": [1, 1, 1, 1, 1],
            "suicide": [0, 0, 0, 0, 0]
        })

    # Clean numeric columns
    df["nkill"] = pd.to_numeric(df.get("nkill", 0), errors="coerce").fillna(0)
    df["nwound"] = pd.to_numeric(df.get("nwound", 0), errors="coerce").fillna(0)

    # ✅ Ensure proper datetime conversion
    df["event_date"] = pd.to_datetime(df["Date"], errors="coerce")

    # ✅ Optional: reduce data for performance
    if len(df) > 50000:
        st.info("Sampling 50,000 records to reduce lag ⚡")
        df = df.sample(50000, random_state=42)

    return df



df = load_data(CSV_PATH)


# ----------------------
# Sidebar filters
# ----------------------
st.sidebar.header("Global Filters")

start_date = st.sidebar.date_input("Start Date", df["event_date"].min())
end_date = st.sidebar.date_input("End Date", df["event_date"].max())
region_sel = st.sidebar.multiselect("Region", df["region_txt"].unique())
country_sel = st.sidebar.multiselect("Country", df["country_txt"].unique())
attack_sel = st.sidebar.multiselect("Attack Type", df["attacktype1_txt"].unique())
target_sel = st.sidebar.multiselect("Target Type", df["targtype1_txt"].unique())
casualty_range = st.sidebar.slider("Casualty Range", 0, int(df["nkill"].max()+df["nwound"].max()), (0,1000))
success_sel = st.sidebar.multiselect("Attack Success", [1,0], default=[1])
suicide_sel = st.sidebar.multiselect("Suicide Attack", [1,0], default=[0,1])

# ----------------------
# Apply filters
# ----------------------
dff = df.copy()
dff = dff[(dff["event_date"]>=pd.to_datetime(start_date)) & (dff["event_date"]<=pd.to_datetime(end_date))]
if region_sel: dff = dff[dff["region_txt"].isin(region_sel)]
if country_sel: dff = dff[dff["country_txt"].isin(country_sel)]
if attack_sel: dff = dff[dff["attacktype1_txt"].isin(attack_sel)]
if target_sel: dff = dff[dff["targtype1_txt"].isin(target_sel)]
dff = dff[(dff["nkill"] + dff["nwound"] >= casualty_range[0]) & (dff["nkill"] + dff["nwound"] <= casualty_range[1])]
if success_sel is not None: dff = dff[dff["success"].isin(success_sel)]
if suicide_sel is not None: dff = dff[dff["suicide"].isin(suicide_sel)]

# ----------------------
# KPIs
# ----------------------
st.title("DarkPulse: Where hidden patterns of terror come to light")
col1,col2,col3,col4 = st.columns(4)
col1.metric("Total Attacks", f"{len(dff):,}")
col2.metric("Total Fatalities", f"{int(dff['nkill'].sum()):,}")
col3.metric("Total Wounded", f"{int(dff['nwound'].sum()):,}")
deadliest = dff.groupby("region_txt")["nkill"].sum().idxmax() if not dff.empty else "N/A"
col4.metric("Deadliest Region", deadliest)

# ----------------------
# Trends over time
st.subheader("Attacks Over Time")
agg = st.selectbox("Aggregation", ["Yearly", "Monthly", "Decade"], index=0)

# Ensure event_date is datetime (already handled in load_data, but just in case)
dff['event_date'] = pd.to_datetime(dff['event_date'], errors='coerce')

if agg == "Monthly":
    ts = dff.groupby(pd.Grouper(key="event_date", freq="M")).size().reset_index(name="attacks")
    fig_trend = px.line(ts, x="event_date", y="attacks", title="Attacks Over Time (Monthly)")

elif agg == "Decade":
    dff['decade'] = (dff['event_date'].dt.year // 10) * 10
    ts = dff.groupby('decade').size().reset_index(name="attacks")
    fig_trend = px.line(ts, x="decade", y="attacks", title="Attacks Over Time (Decade)")

else:  # Yearly
    dff['year'] = dff['event_date'].dt.year
    ts = dff.groupby('year').size().reset_index(name="attacks")
    fig_trend = px.line(ts, x="year", y="attacks", title="Attacks Over Time (Yearly)")

st.plotly_chart(fig_trend, use_container_width=True)



# ----------------------
# Global Map
# ----------------------
st.subheader("Global Distribution of Attacks")
color_by = st.selectbox("Color by", ["Attack Type","Casualty"], index=0)

if color_by=="Casualty":
    dff["casualty"] = dff["nkill"] + dff["nwound"]
    fig_map = px.scatter_geo(dff, lat="latitude", lon="longitude", size="casualty",
                             hover_name="country_txt",
                             hover_data=["gname","attacktype1_txt","targtype1_txt","nkill","nwound"],
                             title="Global Distribution of Attacks (Casualty)")
else:
    fig_map = px.scatter_geo(dff, lat="latitude", lon="longitude", color="attacktype1_txt",
                             hover_name="country_txt",
                             hover_data=["gname","nkill","nwound"],
                             title="Global Distribution of Attacks (Attack Type)")

st.plotly_chart(fig_map, use_container_width=True)

# ----------------------
# Most active groups
# ----------------------
st.subheader("Most Active Terrorist Groups")
top_groups = dff.groupby("gname").size().reset_index(name="attacks").sort_values("attacks", ascending=False).head(20)
fig_groups = px.bar(top_groups, x="attacks", y="gname", orientation="h")
st.plotly_chart(fig_groups, use_container_width=True)

# ----------------------
# Attack types vs casualties
# ----------------------
st.subheader("Attack Types vs Fatalities (Box Plot)")
fig_box = px.box(dff, x="attacktype1_txt", y="nkill", points="all")
st.plotly_chart(fig_box, use_container_width=True)

# ----------------------
# Target vs Weapon Heatmap
# ----------------------
st.subheader("Target Types vs Weapon Types (Heatmap)")
heat = pd.crosstab(dff["targtype1_txt"], dff["weaptype1_txt"]).astype(float)
fig_heat = px.imshow(heat, labels=dict(x="Weapon Type", y="Target Type", color="Count"))
st.plotly_chart(fig_heat, use_container_width=True)

# ----------------------
# Seasonal Pattern
# ----------------------
st.subheader("Seasonal Attack Pattern (Polar)")
if not dff.empty:
    dff["month"] = dff["event_date"].dt.month
    monthly = dff.groupby("month").size().reindex(range(1,13), fill_value=0).reset_index(name="attacks")
    fig_polar = px.line_polar(monthly, r="attacks", theta="month", line_close=True)
    st.plotly_chart(fig_polar, use_container_width=True)



# In[19]:



