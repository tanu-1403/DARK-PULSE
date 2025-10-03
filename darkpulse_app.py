#!/usr/bin/env python
# coding: utf-8

# In[15]:


# darkpulse_streamlit.py
# Streamlit app for visualizing Global

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ----------------------
# Load GTD dataset
# ----------------------

CSV_PATH = "https://drive.google.com/uc?id=1fzYJnNk24rQn_hOwiahtCRreYYXwgNkI"



# In[18]:


@st.cache_data
def load_data(path):
    cols = [
        "eventid","iyear","imonth","iday","country_txt","region_txt","provstate","city",
        "latitude","longitude","attacktype1_txt","targtype1_txt","weaptype1_txt",
        "gname","nkill","nwound","success","suicide","Date"
    ]
    try:
        df = pd.read_csv(path, encoding="ISO-8859-1", low_memory=False)
        df = df[[c for c in cols if c in df.columns]]
    except:
        st.warning("GTD CSV not found. Using sample data.")
        df = pd.DataFrame({
            "eventid":[1,2,3,4,5],
            "iyear":[2001,2005,2010,2015,2019],
            "imonth":[9,6,1,12,7],
            "iday":[11,15,5,20,3],
            "country_txt":["USA","Iraq","India","Syria","Nigeria"],
            "region_txt":["North America","Middle East & North Africa","South Asia","Middle East & North Africa","Sub-Saharan Africa"],
            "city":["NY","Baghdad","Mumbai","Aleppo","Lagos"],
            "latitude":[40.7,33.3,19.0,36.2,6.5],
            "longitude":[-74,44,72,37,3],
            "attacktype1_txt":["Bombing/Explosion","Armed Assault","Bombing/Explosion","Assassination","Bombing/Explosion"],
            "targtype1_txt":["Civilians","Military","Civilians","Government","Civilians"],
            "weaptype1_txt":["Explosives","Firearms","Explosives","Firearms","Explosives"],
            "gname":["Unknown","Group A","Group B","Group C","Group D"],
            "nkill":[3000,150,12,500,30],
            "nwound":[6000,200,30,1000,50],
            "success":[1,1,1,1,1],
            "suicide":[0,0,0,0,0]
        })

    # clean numbers
    df["nkill"] = pd.to_numeric(df.get("nkill",0), errors="coerce").fillna(0)
    df["nwound"] = pd.to_numeric(df.get("nwound",0), errors="coerce").fillna(0)

    # Handle Date
    if "Date" in df.columns:
        df["event_date"] = pd.to_datetime(df["Date"], errors="coerce")
    else:
        df["imonth"] = df["imonth"].replace(0, 1)
        df["iday"] = df["iday"].replace(0, 1)
        df["event_date"] = pd.to_datetime(
            df["iyear"].astype(str) + "-" +
            df["imonth"].astype(str).str.zfill(2) + "-" +
            df["iday"].astype(str).str.zfill(2),
            errors="coerce"
        )

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
