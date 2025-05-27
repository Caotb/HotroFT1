
import streamlit as st
import pandas as pd
import numpy as np

# ====== Load & chuẩn hóa dữ liệu ======
@st.cache_data
def load_data():
    df = pd.read_excel("Log.xlsx", sheet_name="WoList")
    return df

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

# ====== UI ======
st.set_page_config(page_title="FT Job Assistant Mobile", layout="centered")
st.title("📱 HỖ TRỢ FT")

df = load_data()

# Lấy mã nhân viên từ người dùng (mô phỏng đăng nhập)
user_code = st.text_input("🔑 Nhập mã nhân viên (VD: thangth1)", value="").strip().lower()
available_users = df['Nhân viên thực hiện'].dropna().astype(str).str.lower().unique()

if user_code not in available_users:
    st.warning("Mã nhân viên không hợp lệ hoặc chưa có trong hệ thống.")
    st.stop()

# Lọc công việc của nhân viên
user_df = df[df['Nhân viên thực hiện'].astype(str).str.lower() == user_code]

# Công việc gần hết hạn
st.subheader("⏰ Công việc sắp hết hạn (< 24h)")
near_due = user_df[user_df['Thời gian còn lại (H)'] <= 24].copy()
near_due['Nội dung công việc'] = near_due['Nội dung công việc'].astype(str).str.slice(0, 40)
st.dataframe(near_due[['Mã trạm','Nội dung công việc','Thời gian còn lại (H)']], use_container_width=True)

# Tra cứu trạm
st.subheader("📍 Tra cứu theo mã trạm")
station = st.text_input("Nhập mã trạm", value="").strip().upper()
if station:
    station_df = user_df[user_df['Mã trạm'] == station].copy()
    station_df['Nội dung công việc'] = station_df['Nội dung công việc'].astype(str).str.slice(0, 40)
    st.dataframe(station_df[['Nội dung công việc','Thời gian còn lại (H)']], use_container_width=True)

    # Gợi ý công việc tiếp theo
    st.subheader("🚀 Gợi ý công việc tiếp theo")
    if not station_df.empty:
        lat0, lon0 = df[df['Mã trạm'] == station].iloc[0]['Vĩ độ'], df[df['Mã trạm'] == station].iloc[0]['Kinh độ']
        others = user_df[user_df['Mã trạm'] != station].copy()
        others['Distance_km'] = haversine(lat0, lon0, others['Vĩ độ'], others['Kinh độ'])
        others['Nội dung công việc'] = others['Nội dung công việc'].astype(str).str.slice(0, 40)
        others = others.sort_values(['Thời gian còn lại (H)', 'Distance_km'])
        st.dataframe(others[['Mã trạm','Nội dung công việc','Thời gian còn lại (H)','Distance_km']], use_container_width=True)
