import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. Konfigurasi Halaman
st.set_page_config(page_title="VibeCheck Insurance Dashboard", layout="wide")

# Custom CSS untuk tampilan Modern & Gen-Z
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
    .stPlotlyChart { 
        background-color: #ffffff; 
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: #1e1e1e; }
    </style>
    """, unsafe_allow_html=True)

# 2. Load Data
@st.cache_data
def load_data():
    try:
        # Membaca Excel (mendukung format .XLS lama maupun baru)
        df = pd.read_excel('lap_on_risk_28_feb_26.XLS')
    except:
        # Fallback ke CSV jika file Excel tidak terbaca
        df = pd.read_csv('lap_on_risk_28_feb_26.csv')
    
    # Bersihkan nama kolom dari spasi yang tidak terlihat
    df.columns = [str(c).strip() for c in df.columns]
    
    # Konversi kolom numerik krusial
    cols_to_fix = ['TSI_OC', 'PREMIUM_GROSS', 'DISCOUNT']
    for col in cols_to_fix:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0.0 # Buat kolom dummy jika tidak ada agar kode tidak pecah
            
    return df

df = load_data()

# 3. Sidebar Filter (Drill-down)
st.sidebar.header("🎛️ Dashboard Filters")

# Ambil list unik dengan proteksi jika kolom tidak ditemukan
def get_unique(col_name):
    return df[col_name].unique() if col_name in df.columns else []

list_cob = get_unique('COB_DESC')
list_seg = get_unique('SEGMENT')
list_branch = get_unique('BRANCH_DESC')

selected_cob = st.sidebar.multiselect("Select COB:", options=list_cob, default=list_cob)
selected_segment = st.sidebar.multiselect("Select Segment:", options=list_seg, default=list_seg)
selected_branch = st.sidebar.multiselect("Select Branch:", options=list_branch, default=list_branch)

# Filter data berdasarkan input
mask = (
    (df['COB_DESC'].isin(selected_cob)) &
    (df['SEGMENT'].isin(selected_segment)) &
    (df['BRANCH_DESC'].isin(selected_branch))
)
filtered_df = df[mask]

# 4. Header Section
st.title("Videi Insurance: On Risk Dashboard")
st.markdown("Real-time portfolio monitoring.")
st.write("---")

# 5. TOP ROW: Metrik Utama
col1, col2, col3 = st.columns(3)

# Menggunakan BRANCH_DESC karena BRANCH seringkali tidak ada di beberapa format export
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

# 6. MIDDLE ROW: Grafik Bar & Analisis Utama
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

# 7. BOTTOM ROW: Analisis Donut (DIKEMBALIKAN)
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
    if 'TOC_DESCRIPTION' in filtered_df.columns:
        top_toc = filtered_df.groupby('TOC_DESCRIPTION')['PREMIUM_GROSS'].sum().nlargest(5).reset_index()
        fig_don3 = px.pie(top_toc, values='PREMIUM_GROSS', names='TOC_DESCRIPTION', hole=.6,
                          color_discrete_sequence=px.colors.qualitative.Prism)
        fig_don3.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_don3, use_container_width=True)
    else:
        st.info("Kolom TOC_DESCRIPTION tidak ditemukan.")

# 8. DETAIL TABLE DENGAN RASIO DISKON
st.write("---")
st.subheader("📋 Detailed Transaction Summary")

# Grouping data untuk tabel
group_cols = ['BRANCH_DESC', 'COB_DESC', 'TOC_DESCRIPTION']
# Pastikan kolom tersedia sebelum grouping
existing_group_cols = [c for c in group_cols if c in filtered_df.columns]

table_data = filtered_df.groupby(existing_group_cols).agg({
    'TSI_OC': 'sum',
    'PREMIUM_GROSS': 'sum',
    'DISCOUNT': 'sum'
}).reset_index()

# Hitung Rasio Diskon (%) dengan penanganan pembagian nol
table_data['Disc_Ratio'] = np.where(
    table_data['PREMIUM_GROSS'] != 0, 
    (table_data['DISCOUNT'] / table_data['PREMIUM_GROSS']) * 100, 
    0
)

# Proteksi terakhir terhadap NaN
table_data = table_data.fillna(0)

# Tampilkan Tabel
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
