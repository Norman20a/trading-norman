import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 設定網頁
st.set_page_config(page_title="Norman 的交易日記", layout="wide")

# 2. CSS 美化
st.markdown("""
<style>
    .metric-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
    }
</style>
""", unsafe_allow_html=True)

# 3. 標題
st.title("🦅 Norman 的 ICT 交易日記")
st.markdown("### *「交易不是預測，而是執行你的計畫。」*")
st.divider()

# --- 側邊欄：輸入區 ---
st.sidebar.header("📝 新增交易")
with st.sidebar.form("trade_form"):
    col1, col2 = st.columns(2)
    symbol = st.selectbox("商品", ["NAS100", "XAUUSD", "GBPUSD", "EURUSD", "BTCUSD"])
    direction = st.selectbox("方向", ["Buy", "Sell"])
    
    entry_price = st.number_input("進場價", min_value=0.0, format="%.2f")
    exit_price = st.number_input("出場價", min_value=0.0, format="%.2f")
    pnl = st.number_input("損益 (USD)", value=0.0, step=10.0, help="負數代表虧損")
    notes = st.text_area("筆記", placeholder="ICT Setup / 心態紀錄...")
    
    submitted = st.form_submit_button("💾 儲存紀錄")

# --- 邏輯處理 ---
if 'journal' not in st.session_state:
    st.session_state.journal = []

if submitted:
    new_trade = {
        "已選取": False,  # 預設不勾選
        "日期": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "商品": symbol,
        "方向": direction,
        "進場": entry_price,
        "出場": exit_price,
        "損益": pnl,
        "筆記": notes
    }
    st.session_state.journal.append(new_trade)
    st.success(f"已新增 {symbol}！")
    st.rerun() # 強制重新整理讓資料馬上出現

# --- 儀表板 ---
trades = st.session_state.journal
total_pnl = sum(t['損益'] for t in trades)
win_rate = 0
if len(trades) > 0:
    wins = len([t for t in trades if t['損益'] > 0])
    win_rate = (wins / len(trades)) * 100

c1, c2, c3 = st.columns(3)
c1.metric("💰 總損益", f"${total_pnl:,.2f}")
c2.metric("📊 總單數", f"{len(trades)} 次")
c3.metric("🎯 勝率", f"{win_rate:.1f}%")

st.divider()

# --- 歷史紀錄 (含刪除功能) ---
st.subheader("📋 交易紀錄管理")

if len(trades) > 0:
    df = pd.DataFrame(trades)
    
    # 使用 Data Editor 讓使用者可以勾選
    # num_rows="dynamic" 讓你可以直接在表格裡刪除，但我們用 checkbox 比較保險
    edited_df = st.data_editor(
        df,
        column_config={
            "已選取": st.column_config.CheckboxColumn(
                "刪除?",
                help="勾選後按下方的刪除按鈕",
                default=False,
            )
        },
        disabled=["日期", "商品", "方向", "損益"], # 鎖定其他欄位不讓改
        hide_index=True,
        use_container_width=True
    )

    # 刪除按鈕邏輯
    col_del, col_space = st.columns([1, 4])
    with col_del:
        if st.button("🗑️ 刪除勾選的資料", type="primary"):
            # 找出沒有被勾選的資料留下來
            to_keep = []
            for index, row in edited_df.iterrows():
                if not row['已選取']:
                    # 把 '已選取' 這個欄位拿掉再存回去，保持乾淨
                    record = row.to_dict()
                    record['已選取'] = False 
                    to_keep.append(record)
            
            st.session_state.journal = to_keep
            st.rerun() # 重新整理頁面
            
else:
    st.info("目前沒有紀錄。")

st.caption("🔴 cTrader Auto-Sync: Disconnected")