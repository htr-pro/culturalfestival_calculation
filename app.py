
import streamlit as st

# 翻訳を防止するHTML設定
st.set_page_config(page_title="文化祭原価計算アプリ", layout="centered")

# CSS: フォントサイズとデザインの最適化
st.markdown("""
    <style>
    .notranslate { translate: no !important; }

    /* メインタイトルのサイズをアップ */
    .main-title {
        font-size: 7vw !important;
        white-space: nowrap;
        text-align: center;
        color: #1e293b;
        margin-top: 10px;
        margin-bottom: 30px;
        font-weight: 900;
        letter-spacing: -1px;
    }

    /* ①と②の見出しサイズをタイトルに合わせつつ調整 */
    .section-title {
        font-size: 6vw !important;
        font-weight: 800;
        color: #334155;
        margin-top: 20px;
        margin-bottom: 15px;
        border-bottom: 3px solid #3b82f6;
        display: inline-block;
        padding-right: 10px;
    }

    @media (min-width: 600px) {
        .main-title { font-size: 2.8rem !important; }
        .section-title { font-size: 2rem !important; }
    }

    .stButton>button { width: 100%; border-radius: 10px; height: 3.5rem; font-weight: bold; background-color: #3b82f6; color: white; font-size: 1.1rem; }
    .price-card { background-color: #fdf2f2; padding: 20px; border-radius: 15px; border: 2px solid #ef4444; text-align: center; margin-top: 20px; }
    .item-box { background-color: #f8fafc; padding: 12px; border-radius: 8px; border-left: 6px solid #3b82f6; margin-bottom: 10px; font-weight: bold; font-size: 1.1rem; }
    input { font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

# タイトル表示
st.markdown('<div class="notranslate"><h1 class="main-title">🎡 文化祭原価計算アプリ</h1></div>', unsafe_allow_html=True)

if 'ingredients' not in st.session_state:
    st.session_state.ingredients = []

UNITS = ["g", "kg", "ml", "l", "袋", "本", "個"]
INT_UNITS = ["袋", "本", "個"]

# --- ① 材料を登録する ---
st.markdown('<div class="notranslate section-title">① 材料を登録する</div>', unsafe_allow_html=True)

with st.form(key='reg_form', clear_on_submit=True):
    name = st.text_input("材料名（例：ソーセージ）", key="new_name")
    col1, col2 = st.columns(2)
    vol = col1.number_input("内容量", min_value=1, value=10, step=1)
    unit = col2.selectbox("単位", UNITS)
    price = st.number_input("購入金額(円)", min_value=0, value=1000, step=10)

    submit = st.form_submit_button("➕ この材料を登録する")
    if submit and name:
        st.session_state.ingredients.append({
            "name": name,
            "unit_price": price / vol,
            "unit": unit
        })
        st.rerun()

# --- ② 1人当たりの材料を入力する ---
st.write(" ") # 余白
st.markdown('<div class="notranslate section-title">② 1人当たりの材料を入力する</div>', unsafe_allow_html=True)
total_cost = 0.0

if not st.session_state.ingredients:
    st.info("まずは上のフォームから材料を登録してください。")
else:
    for i, item in enumerate(st.session_state.ingredients):
        st.markdown(f'<div class="item-box notranslate">【{item["name"]}】 <small>(単価:{item["unit_price"]:.2f}円/{item["unit"]})</small></div>', unsafe_allow_html=True)

        c_in, c_del = st.columns([4, 1])

        with c_in:
            if item['unit'] in INT_UNITS:
                used = st.number_input(f"使用数 ({item['unit']})", key=f"inp_{i}", min_value=0, value=0, step=1)
            else:
                used = st.number_input(f"使用量 ({item['unit']})", key=f"inp_{i}", min_value=0.0, value=0.0, step=0.1)

        with c_del:
            st.write("") # 上の余白調整
            if st.button("🗑️", key=f"btn_{i}"):
                st.session_state.ingredients.pop(i)
                st.rerun()

        item_cost = used * item['unit_price']
        total_cost += item_cost
        st.markdown(f"<div style='text-align:right;'>原価: <span style='color:#b91c1c; font-weight:bold; font-size:1.2rem;'>{item_cost:,.2f} 円</span></div>", unsafe_allow_html=True)
        st.divider()

    # 合計表示
    st.markdown(f"""
        <div class="price-card notranslate">
            <p style="margin:0; color:#b91c1c; font-weight:bold;">💰 1人当たりの合計原価</p>
            <h1 style="margin:5px 0; color:#b91c1c; font-size: 3rem;">{total_cost:,.2f} 円</h1>
        </div>
    """, unsafe_allow_html=True)

    st.write(" ")
    if st.button("🚨 全データをリセット"):
        st.session_state.ingredients = []
        st.rerun()
