import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="DarkPulse", layout="wide", page_icon="💣")

# --- STYLES ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@400;600&display=swap');

   .stApp {
       /* Handpicked black-and-white tall building image */
       background-image: url("https://images.unsplash.com/photo-1600585154340-be6161a56a0c?ixlib=rb-4.0.3&q=80&w=1600&auto=format&fit=crop");
       background-size: cover;
       background-position: center;
       background-attachment: fixed;
       animation: fadePulse 18s ease-in-out infinite;
       color: #eaeaea;
    font-family: 'Exo 2', sans-serif;
   }

    /* Subtle fade animation */
    @keyframes fadePulse {
        0% { opacity: 0.95; }
        50% { opacity: 1; }
        100% { opacity: 0.95; }
   }
    /* Dark overlay for readability */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: rgba(0,0,0,0.78);
        z-index: -1;
    }

    h1 {
        font-family: 'Orbitron', sans-serif;
        color: #ff4d4d !important;
        text-align: center;
        font-size: 3rem !important;
        text-shadow: 0 0 40px rgba(255,70,70,0.4);
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    .subtitle {
        text-align: center;
        color: #cccccc;
        font-style: italic;
        font-size: 1.15rem;
        margin-top: -10px;
        margin-bottom: 20px;
    }

    .kpi-card {
        background: rgba(25, 25, 25, 0.7);
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 0 20px rgba(255,0,0,0.15);
        transition: all 0.3s ease;
    }

    .kpi-card:hover {
        box-shadow: 0 0 35px rgba(255,0,0,0.3);
        transform: scale(1.03);
    }

    section[data-testid="stSidebar"] {
        background: rgba(10,10,10,0.9);
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION WITH LOGO ---
st.markdown("""
<div style='text-align:center;'>
    <img src='https://upload.wikimedia.org/wikipedia/commons/2/25/Red_circle_icon.svg' 
         width='70' style='filter:drop-shadow(0 0 20px rgba(255,0,0,0.6)); margin-bottom:10px;'>
    <h1>DARKPULSE</h1>
    <p class='subtitle'>Illuminating unseen patterns in a world shadowed by fear</p>
    <hr style='border: 0.5px solid rgba(255,255,255,0.15); width:60%; margin:auto;'>
</div>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    url = "https://drive.google.com/uc?id=1fzYJnNk24rQn_hOwiahtCRreYYXwgNkI"
    use_cols = ["Date", "country_txt", "region_txt", "city", "latitude", "longitude",
                "attacktype1_txt", "targtype1_txt", "weaptype1_txt", "gname",
                "nkill", "nwound", "success", "suicide"]
    df = pd.read_csv(url, usecols=lambda c: c in use_cols, low_memory=False)
    df = df.sample(frac=0.15, random_state=42)
    df["nkill"] = pd.to_numeric(df["nkill"], errors="coerce").fillna(0)
    df["nwound"] = pd.to_numeric(df["nwound"], errors="coerce").fillna(0)
    df["event_date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["iyear"] = df["event_date"].dt.year
    return df

df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🕵️ Filters")
region = st.sidebar.multiselect("Region", df["region_txt"].unique())
attack = st.sidebar.multiselect("Attack Type", df["attacktype1_txt"].unique())
year = st.sidebar.slider("Year Range", int(df["iyear"].min()), int(df["iyear"].max()), (2000, 2015))

dff = df.copy()
dff = dff[(dff["iyear"] >= year[0]) & (dff["iyear"] <= year[1])]
if region: dff = dff[dff["region_txt"].isin(region)]
if attack: dff = dff[dff["attacktype1_txt"].isin(attack)]

# --- KPI CARDS ---
col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"<div class='kpi-card'><h3>💣 Total Attacks</h3><p style='font-size:1.6rem'>{len(dff):,}</p></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='kpi-card'><h3>☠️ Fatalities</h3><p style='font-size:1.6rem'>{int(dff['nkill'].sum()):,}</p></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='kpi-card'><h3>🩸 Injured</h3><p style='font-size:1.6rem'>{int(dff['nwound'].sum()):,}</p></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='kpi-card'><h3>🌍 Countries</h3><p style='font-size:1.6rem'>{dff['country_txt'].nunique()}</p></div>", unsafe_allow_html=True)

# --- VISUALS ---
colA, colB = st.columns(2)
with colA:
    st.subheader("📈 Yearly Attack Trends")
    yearly = dff.groupby("iyear").size().reset_index(name="attacks")
    fig = px.line(yearly, x="iyear", y="attacks", markers=True,
                  template="plotly_dark", color_discrete_sequence=["#ff4444"])
    st.plotly_chart(fig, use_container_width=True)

with colB:
    st.subheader("🎯 Attack Type Distribution")
    att = dff["attacktype1_txt"].value_counts().reset_index()
    att.columns = ["Attack Type","Count"]
    fig2 = px.pie(att, values="Count", names="Attack Type", hole=0.4,
                  color_discrete_sequence=px.colors.sequential.Reds_r)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

colC, colD = st.columns(2)
with colC:
    st.subheader("🔥 Global Hotspots")
    dff["casualty"] = dff["nkill"] + dff["nwound"]
    fig3 = px.scatter_geo(dff, lat="latitude", lon="longitude",
                          color="region_txt", size="casualty",
                          hover_name="country_txt",
                          template="plotly_dark")
    st.plotly_chart(fig3, use_container_width=True)

with colD:
    st.subheader("🧨 Top 10 Terror Groups")
    grp = dff["gname"].value_counts().head(10).reset_index()
    grp.columns = ["Group","Attacks"]
    fig4 = px.bar(grp, x="Attacks", y="Group", orientation="h",
                  color="Attacks", color_continuous_scale="reds")
    st.plotly_chart(fig4, use_container_width=True)

# --- AI SUMMARY ---
st.markdown("---")
st.subheader("🧠 Dark Intelligence Summary")

if not dff.empty:
    top_region = dff["region_txt"].value_counts().idxmax()
    top_attack = dff["attacktype1_txt"].value_counts().idxmax()
    total = len(dff)
    avg_kill = round(dff["nkill"].mean(), 2)
    avg_wound = round(dff["nwound"].mean(), 2)
    period = f"{year[0]}–{year[1]}"
    st.markdown(f"""
    <div style='background:rgba(30,30,30,0.65); padding:15px; border-radius:12px;'>
        <p style='font-size:1.1rem; color:#ddd;'>
        Between <b>{period}</b>, there were <b>{total:,}</b> recorded terrorist incidents.<br>
        The <b>{top_region}</b> region witnessed the highest concentration of attacks, 
        primarily involving <b>{top_attack}</b>.<br>
        Average casualties per attack: <b>{avg_kill}</b> deaths, <b>{avg_wound}</b> injuries.<br><br>
        <i>AI Summary: The data reveals an evolving landscape of violence — not random, but patterned. Each event is a signal in the noise, echoing shifts in ideology, geography, and human unrest.</i>
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("No data available for the selected filters.")




