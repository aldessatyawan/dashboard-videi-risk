import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Konfigurasi Halaman
st.set_page_config(page_title="VibeCheck Insurance Dashboard", layout="wide")

# Custom CSS untuk tampilan Modern & Gen-Z
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
    }
    .stPlotlyChart {
        background-color: #ffffff;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #1e1e1e;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Load Data
@st.cache_data
def load_data():
    # Pastikan file name sesuai dengan yang ada di repositori GitHub Anda
    try:
        df = pd.read_excel('lap_on_risk_28_feb_26.XLS')
    except Exception:
        # Fallback jika file Excel gagal dibaca atau menggunakan CSV hasil konversi
        df = pd.read_csv('lap_on_risk_28_feb_26.csv')
    
    # List kolom yang harus berupa angka
    cols_to_fix = ['TSI_OC', 'PREMIUM_GROSS', 'DISCOUNT']
    for col in cols_to_fix:
        if col in df.columns:
            # Ubah ke numerik, jika error (seperti teks) ubah jadi NaN lalu isi dengan 0
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

df = load_data()

# 3. Sidebar Filter
st.sidebar.header("🎛️ Dashboard Filters")
selected_cob = st.sidebar.multiselect("Select COB:", options=df['COB_DESC'].unique(), default=df['COB_DESC'].unique())
selected_segment = st.sidebar.multiselect("Select Segment:", options=df['SEGMENT'].unique(), default=df['SEGMENT'].unique())
selected_branch = st.sidebar.multiselect("Select Branch:", options=df['BRANCH_DESC'].unique(), default=df['BRANCH_DESC'].unique())

# Filter data berdasarkan input
filtered_df = df[
    (df['COB_DESC'].isin(selected_cob)) &
    (df['SEGMENT'].isin(selected_segment)) &
    (df['BRANCH_DESC'].isin(selected_branch))
]

# 4. Header Section
st.title("Videi Insurance: On Risk Dashboard")
st.markdown("Real-time portfolio monitoring.")
st.write("---")

# 5. TOP ROW: Metrik Utama
col1, col2, col3 = st.columns(3)

total_branch = filtered_df[filtered_df['PREMIUM_GROSS'] > 0]['BRANCH'].nunique()
total_tsi = filtered_df['TSI_OC'].sum()
total_premium = filtered_df['PREMIUM_GROSS'].sum()

with col1:
    st.metric(label="Total Active Branches", value=f"{total_branch}")
with col2:
    st.metric(label="Total TSI (OC)", value=f"{total_tsi:,.0f}")
with col3:
    st.metric(label="Total Premium Gross", value=f"{total_premium:,.0f}")

st.write("")

# 6. MIDDLE ROW: Grafik Bar & Analisis
col_mid1, col_mid2 = st.columns([1, 1.5])

with col_mid1:
    st.subheader("On Risk by Branch")
    branch_data = filtered_df.groupby('BRANCH_DESC')['PREMIUM_GROSS'].sum().reset_index()
    fig_branch = px.bar(branch_data, x='BRANCH_DESC', y='PREMIUM_GROSS', 
                        color_discrete_sequence=['#636EFA'],
                        template="plotly_white")
    fig_branch.update_layout(margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_branch, use_container_width=True)

with col_mid2:
    st.subheader("TSI vs Premium per COB")
    cob_data = filtered_df.groupby('COB_DESC')[['TSI_OC', 'PREMIUM_GROSS']].sum().reset_index()
    fig_cob = go.Figure()
    fig_cob.add_trace(go.Bar(y=cob_data['COB_DESC'], x=cob_data['TSI_OC'], name='TSI OC', orientation='h', marker_color='#00CC96'))
    fig_cob.add_trace(go.Bar(y=cob_data['COB_DESC'], x=cob_data['PREMIUM_GROSS'], name='Premium Gross', orientation='h', marker_color='#EF553B'))
    fig_cob.update_layout(barmode='group', template="plotly_white", margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_cob, use_container_width=True)

# 7. BOTTOM ROW: Analisis Donut
st.write("---")
st.subheader("Portfolio Distribution")
col_bot1, col_bot2, col_bot3 = st.columns(3)

with col_bot1:
    st.markdown("**Top 5 Branch by Premium**")
    top_branch = filtered_df.groupby('BRANCH_DESC')['PREMIUM_GROSS'].sum().nlargest(5).reset_index()
    fig_don1 = px.pie(top_branch, values='PREMIUM_GROSS', names='BRANCH_DESC', hole=.6,
                      color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_don1.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_don1, use_container_width=True)

with col_bot2:
    st.markdown("**Segment Distribution**")
    seg_data = filtered_df.groupby('SEGMENT')['PREMIUM_GROSS'].sum().reset_index()
    fig_don2 = px.pie(seg_data, values='PREMIUM_GROSS', names='SEGMENT', hole=.6,
                      color_discrete_sequence=px.colors.qualitative.Safe)
    fig_don2.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_don2, use_container_width=True)

with col_bot3:
    st.markdown("**Top 5 TOC Description**")
    top_toc = filtered_df.groupby('TOC_DESCRIPTION')['PREMIUM_GROSS'].sum().nlargest(5).reset_index()
    fig_don3 = px.pie(top_toc, values='PREMIUM_GROSS', names='TOC_DESCRIPTION', hole=.6,
                      color_discrete_sequence=px.colors.qualitative.Prism)
    fig_don3.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_don3, use_container_width=True)

# 8. DETAIL TABLE (FIXED AREA)
st.write("---")
st.subheader("📋 Detailed Transaction Summary")

# Grouping data
table_data = filtered_df.groupby(['BRANCH_DESC', 'COB_DESC', 'TOC_DESCRIPTION']).agg({
    'TSI_OC': 'sum',
    'PREMIUM_GROSS': 'sum',
    'DISCOUNT': 'sum'
}).reset_index()

# Proteksi terakhir: Isi nilai kosong dengan 0 sebelum masuk ke styler
table_data = table_data.fillna(0)

# Format tabel
st.dataframe(
    table_data.style.format({
        'TSI_OC': '{:,.2f}',
        'PREMIUM_GROSS': '{:,.2f}',
        'DISCOUNT': '{:,.2f}'
    }, na_rep='0.00'),
    use_container_width=True,
    hide_index=True
)
