import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. Konfigurasi Halaman
st.set_page_config(page_title="VibeCheck Insurance Dashboard", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
    }
    .stPlotlyChart { background-color: #ffffff; border-radius: 15px; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: #1e1e1e; }
    </style>
    """, unsafe_allow_html=True)

# 2. Load Data
@st.cache_data
def load_data():
    try:
        # Mencoba membaca Excel
        df = pd.read_excel('lap_on_risk_28_feb_26.XLS')
    except:
        # Fallback ke CSV jika Excel gagal
        df = pd.read_csv('lap_on_risk_28_feb_26.csv')
    
    # Bersihkan nama kolom dari spasi (mencegah KeyError)
    df.columns = [str(c).strip() for c in df.columns]
    
    # Konversi kolom numerik
    cols_to_fix = ['TSI_OC', 'PREMIUM_GROSS', 'DISCOUNT']
    for col in cols_to_fix:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            # Jika kolom tidak ada, buatkan kolom kosong agar kode tidak error
            df[col] = 0.0
            
    return df

df = load_data()

# 3. Sidebar Filter
st.sidebar.header("🎛️ Dashboard Filters")

# Ambil list kolom yang tersedia untuk menghindari error jika kolom tidak ada
list_cob = df['COB_DESC'].unique() if 'COB_DESC' in df.columns else []
list_seg = df['SEGMENT'].unique() if 'SEGMENT' in df.columns else []
list_branch = df['BRANCH_DESC'].unique() if 'BRANCH_DESC' in df.columns else []

selected_cob = st.sidebar.multiselect("Select COB:", options=list_cob, default=list_cob)
selected_segment = st.sidebar.multiselect("Select Segment:", options=list_seg, default=list_seg)
selected_branch = st.sidebar.multiselect("Select Branch:", options=list_branch, default=list_branch)

# Filter data
filtered_df = df[
    (df['COB_DESC'].isin(selected_cob)) &
    (df['SEGMENT'].isin(selected_segment)) &
    (df['BRANCH_DESC'].isin(selected_branch))
]

# 4. Header
st.title("Videi Insurance: On Risk Dashboard")
st.markdown("Real-time portfolio monitoring.")
st.write("---")

# 5. TOP ROW: Metrik Utama
col1, col2, col3 = st.columns(3)

# PERBAIKAN: Menggunakan BRANCH_DESC karena BRANCH tidak ditemukan di dataset
total_branch = filtered_df[filtered_df['PREMIUM_GROSS'] > 0]['BRANCH_DESC'].nunique() if 'BRANCH_DESC' in filtered_df.columns else 0
total_tsi = filtered_df['TSI_OC'].sum()
total_premium = filtered_df['PREMIUM_GROSS'].sum()

with col1:
    st.metric(label="Total Active Branches", value=f"{total_branch}")
with col2:
    st.metric(label="Total TSI (OC)", value=f"{total_tsi:,.0f}")
with col3:
    st.metric(label="Total Premium Gross", value=f"{total_premium:,.0f}")

st.write("")

# 6. MIDDLE ROW: Grafik
col_mid1, col_mid2 = st.columns([1, 1.5])

with col_mid1:
    st.subheader("On Risk by Branch")
    branch_data = filtered_df.groupby('BRANCH_DESC')['PREMIUM_GROSS'].sum().reset_index()
    fig_branch = px.bar(branch_data, x='BRANCH_DESC', y='PREMIUM_GROSS', template="plotly_white")
    st.plotly_chart(fig_branch, use_container_width=True)

with col_mid2:
    st.subheader("TSI vs Premium per COB")
    cob_data = filtered_df.groupby('COB_DESC')[['TSI_OC', 'PREMIUM_GROSS']].sum().reset_index()
    fig_cob = go.Figure()
    fig_cob.add_trace(go.Bar(y=cob_data['COB_DESC'], x=cob_data['TSI_OC'], name='TSI OC', orientation='h', marker_color='#00CC96'))
    fig_cob.add_trace(go.Bar(y=cob_data['COB_DESC'], x=cob_data['PREMIUM_GROSS'], name='Premium Gross', orientation='h', marker_color='#EF553B'))
    fig_cob.update_layout(barmode='group', template="plotly_white")
    st.plotly_chart(fig_cob, use_container_width=True)

# 7. DETAIL TABLE DENGAN RASIO
st.write("---")
st.subheader("📋 Detailed Transaction Summary")

# Grouping
agg_cols = ['BRANCH_DESC', 'COB_DESC', 'TOC_DESCRIPTION']
# Pastikan semua kolom grouping ada
agg_cols = [c for c in agg_cols if c in filtered_df.columns]

table_data = filtered_df.groupby(agg_cols).agg({
    'TSI_OC': 'sum',
    'PREMIUM_GROSS': 'sum',
    'DISCOUNT': 'sum'
}).reset_index()

# Hitung Rasio Diskon (Cegah Division by Zero)
table_data['Disc_Ratio'] = np.where(
    table_data['PREMIUM_GROSS'] != 0, 
    (table_data['DISCOUNT'] / table_data['PREMIUM_GROSS']) * 100, 
    0
)

# Tampilkan
st.dataframe(
    table_data.style.format({
        'TSI_OC': '{:,.2f}',
        'PREMIUM_GROSS': '{:,.2f}',
        'DISCOUNT': '{:,.2f}',
        'Disc_Ratio': '{:.2f}%'
    }),
    use_container_width=True,
    hide_index=True
)
