import streamlit as st

# 翻訳防止とデザイン設定
st.set_page_config(page_title="文化祭原価計算アプリ", layout="centered")

st.markdown("""
    <style>
    .notranslate { translate: no !important; }
    .main-title { font-size: 7vw !important; white-space: nowrap; text-align: center; color: #1e293b; margin-top: 10px; margin-bottom: 30px; font-weight: 900; }
    .section-title { font-size: 6vw !important; font-weight: 800; color: #334155; margin-top: 20px; border-bottom: 3px solid #3b82f6; display: inline-block; }
    @media (min-width: 600px) { .main-title { font-size: 2.8rem !important; } .section-title { font-size: 2rem !important; } }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5rem; font-weight: bold; background-color: #3b82f6; color: white; }
    .price-card { background-color: #fdf2f2; padding: 20px; border-radius: 15px; border: 2px solid #ef4444; text-align: center; margin-top: 20px; }
    .item-box { background-color: #f8fafc; padding: 12px; border-radius: 8px; border-left: 6px solid #3b82f6; margin-bottom: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="notranslate"><h1 class="main-title">🎡 文化祭原価計算アプリ</h1></div>', unsafe_allow_html=True)

if 'ingredients' not in st.session_state:
    st.session_state.ingredients = []

UNITS = ["g", "kg", "ml", "l", "袋", "本", "個"]
INT_UNITS = ["袋", "本", "個"]

# --- ① 材料を登録 ---
st.markdown('<div class="notranslate section-title">① 材料を登録する</div>', unsafe_allow_html=True)
with st.form(key='reg_form', clear_on_submit=True):
    name = st.text_input("材料名")
    col1, col2 = st.columns(2)
    vol = col1.number_input("内容量", min_value=1, value=10, step=1)
    unit = col2.selectbox("単位", UNITS)
    price = st.number_input("購入金額(円)", min_value=0, value=1000, step=10)
    if st.form_submit_button("➕ この材料を登録する"):
        if name:
            st.session_state.ingredients.append({"name": name, "unit_price": price / vol, "unit": unit})
            st.rerun()

# --- ② 1人当たり入力 ---
st.write(" ")
st.markdown('<div class="notranslate section-title">② 1人当たりの材料を入力する</div>', unsafe_allow_html=True)
total_cost = 0.0

if not st.session_state.ingredients:
    st.info("材料を登録してください。")
else:
    # 集計用のテキストを作成（画像保存の代わりにテキスト出力も用意）
    summary_text = "【文化祭原価計算結果】\n"
    
    for i, item in enumerate(st.session_state.ingredients):
        st.markdown(f'<div class="item-box notranslate">【{item["name"]}】</div>', unsafe_allow_html=True)
        c_in, c_del = st.columns([4, 1])
        with c_in:
            if item['unit'] in INT_UNITS:
                used = st.number_input(f"使用数 ({item['unit']})", key=f"inp_{i}", min_value=0, value=0, step=1)
            else:
                used = st.number_input(f"使用量 ({item['unit']})", key=f"inp_{i}", min_value=0.0, value=0.0, step=0.1)
        if c_del.button("🗑️", key=f"btn_{i}"):
            st.session_state.ingredients.pop(i)
            st.rerun()
        
        item_cost = used * item['unit_price']
        total_cost += item_cost
        summary_text += f"・{item['name']}: {used}{item['unit']} ({item_cost:,.2f}円)\n"
        st.markdown(f"<div style='text-align:right;'>原価: <span style='color:#b91c1c; font-weight:bold;'>{item_cost:,.2f} 円</span></div>", unsafe_allow_html=True)
        st.divider()

    summary_text += f"\n💰1人当たりの合計原価: {total_cost:,.2f}円"

    # 合計表示
    st.markdown(f"""
        <div class="price-card notranslate">
            <p style="margin:0; color:#b91c1c; font-weight:bold;">💰 1人当たりの合計原価</p>
            <h1 style="margin:5px 0; color:#b91c1c; font-size: 3rem;">{total_cost:,.2f} 円</h1>
        </div>
    """, unsafe_allow_html=True)

    # --- 📸 共有・保存機能 ---
    st.write(" ")
    st.subheader("📸 結果を共有する")
    
    # 手順：スマホのスクリーンショットを促しつつ、テキストコピーも可能に
    st.info("💡 スマホの「スクリーンショット」でこの画面を保存してLINEに送るのが一番きれいです！")
    
    # コピー用テキストエリア
    st.text_area("LINE貼り付け用テキスト（コピーして使ってください）", value=summary_text, height=150)

    if st.button("🚨 全データをリセット"):
        st.session_state.ingredients = []
        st.rerun()
