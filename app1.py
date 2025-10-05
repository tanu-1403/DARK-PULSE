import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="DarkPulse", layout="wide", page_icon="💣")

# --- CUSTOM STYLES WITH FOG PULSE EFFECT ---
st.markdown("""
<style>
    @keyframes fogPulse {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .stApp {
        background: linear-gradient(120deg, rgba(0,0,0,0.9), rgba(15,15,15,0.95), rgba(30,30,30,0.85));
        background-size: 400% 400%;
        animation: fogPulse 25s ease infinite;
        color: #e5e5e5;
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3 {
        text-align: center;
        color: #f5f5f5 !important;
        text-shadow: 0 0 25px rgba(255,255,255,0.1);
    }

    .kpi-card {
        background: rgba(20, 20, 20, 0.55);
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 0 12px rgba(255,255,255,0.05);
        transition: all 0.3s ease;
    }

    .kpi-card:hover {
        box-shadow: 0 0 25px rgba(204,68,68,0.2);
        transform: scale(1.02);
    }

    section[data-testid="stSidebar"] {
        background: rgba(10,10,10,0.9);
        backdrop-filter: blur(8px);
    }

    h2, h3 {
        border-left: 4px solid #cc4444;
        padding-left: 10px;
        text-align: left !important;
    }

</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div style='text-align:center; margin-top:-25px;'>
    <h1>🌑 DarkPulse Dashboard</h1>
    <p style='color:#ccc;'>Illuminating unseen patterns in a world shadowed by fear.</p>
    <hr style='border: 0.5px solid rgba(255,255,255,0.2); width:60%; margin:auto;'>
</div>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    url = "https://drive.google.com/uc?id=1fzYJnNk24rQn_hOwiahtCRreYYXwgNkI"
    use_cols = ["Date","country_txt","region_txt","city","latitude","longitude",
                "attacktype1_txt","targtype1_txt","weaptype1_txt",
                "gname","nkill","nwound","success","suicide"]
    
    df = pd.read_csv(url, usecols=lambda c: c in use_cols, low_memory=False)
    df = df.sample(frac=0.15, random_state=42)  # Reduce lag
    df["nkill"] = pd.to_numeric(df["nkill"], errors="coerce").fillna(0)
    df["nwound"] = pd.to_numeric(df["nwound"], errors="coerce").fillna(0)
    df["event_date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["iyear"] = df["event_date"].dt.year  # extract year for filtering
    return df


df = load_data()
df

# --- SIDEBAR FILTERS ---
st.sidebar.header("🕵️ Filters")
region = st.sidebar.multiselect("Region", df["region_txt"].unique())
attack = st.sidebar.multiselect("Attack Type", df["attacktype1_txt"].unique())
year = st.sidebar.slider("Year Range", int(df["iyear"].min()), int(df["iyear"].max()), (2000, 2015))

# Filter logic
dff = df.copy()
dff = dff[(dff["iyear"] >= year[0]) & (dff["iyear"] <= year[1])]
if region: dff = dff[dff["region_txt"].isin(region)]
if attack: dff = dff[dff["attacktype1_txt"].isin(attack)]

# --- KPI CARDS ---
col1, col2, col3, col4 = st.columns(4)
col1.markdown(f"<div class='kpi-card'><h3>💣 Total Attacks</h3><p style='font-size:1.5rem'>{len(dff):,}</p></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='kpi-card'><h3>☠️ Fatalities</h3><p style='font-size:1.5rem'>{int(dff['nkill'].sum()):,}</p></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='kpi-card'><h3>🩸 Injured</h3><p style='font-size:1.5rem'>{int(dff['nwound'].sum()):,}</p></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='kpi-card'><h3>🌍 Countries</h3><p style='font-size:1.5rem'>{dff['country_txt'].nunique()}</p></div>", unsafe_allow_html=True)

# --- VISUAL LAYOUT ---
colA, colB = st.columns(2)

with colA:
    st.subheader("📈 Yearly Attack Trends")
    yearly = dff.groupby("iyear").size().reset_index(name="attacks")
    fig = px.line(yearly, x="iyear", y="attacks", markers=True,
                  template="plotly_dark", color_discrete_sequence=["#cc4444"])
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

# --- AI SUMMARY SECTION ---
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
    <div style='background:rgba(30,30,30,0.6); padding:15px; border-radius:12px;'>
        <p style='font-size:1.1rem; color:#ddd;'>
        Between <b>{period}</b>, there were <b>{total:,}</b> recorded terrorist incidents.<br>
        The <b>{top_region}</b> region witnessed the highest concentration of attacks, 
        primarily involving <b>{top_attack}</b>.<br>
        On average, each event caused <b>{avg_kill}</b> deaths and <b>{avg_wound}</b> injuries.<br><br>
        These insights reveal not just patterns of violence, but echoes of instability shaping our world.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("No data available for the selected filters.")
