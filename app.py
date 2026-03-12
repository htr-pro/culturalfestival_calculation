import streamlit as st

# 1. ページ設定と翻訳防止
st.set_page_config(page_title="文化祭原価計算アプリ", layout="centered")

# 2. CSS: ダークモード対策 & デザイン調整
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        color: #1e293b !important;
        background-color: #ffffff !important;
    }
    .notranslate { translate: no !important; }
    .main-title { font-size: 7vw !important; text-align: center; color: #1e293b; font-weight: 900; margin-bottom: 20px; }
    .section-title { font-size: 5.5vw !important; font-weight: 800; color: #1e293b; border-bottom: 3px solid #3b82f6; display: inline-block; margin-top: 20px; }
    @media (min-width: 600px) { .main-title { font-size: 2.8rem !important; } .section-title { font-size: 1.8rem !important; } }
    label, p, span, div { color: #1e293b !important; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; background-color: #3b82f6; color: white !important; }
    .price-card { background-color: #fdf2f2; padding: 20px; border-radius: 15px; border: 2px solid #ef4444; text-align: center; margin-top: 10px; }
    .item-box { background-color: #f1f5f9; padding: 12px; border-radius: 8px; border-left: 6px solid #3b82f6; margin-bottom: 10px; font-weight: bold; }
    .stNumberInput input, .stTextInput input, .stSelectbox div { color: #1e293b !important; }
    </style>
    """, unsafe_allow_html=True)

if 'ingredients' not in st.session_state:
    st.session_state.ingredients = []

UNITS = ["g", "kg", "ml", "l", "袋", "本", "個"]
INT_UNITS = ["袋", "本", "個"]
FRACTIONS = {"1": 1.0, "1/2 (0.5)": 0.5, "1/3 (0.33)": 0.33, "1/4 (0.25)": 0.25, "1/5 (0.2)": 0.2, "0": 0.0}

st.markdown('<div class="notranslate"><h1 class="main-title">🎡 文化祭原価計算アプリ</h1></div>', unsafe_allow_html=True)

# --- ① 材料を登録・編集 ---
st.markdown('<div class="notranslate section-title">① 材料を登録・編集する</div>', unsafe_allow_html=True)

with st.expander("➕ 新しい材料を追加する", expanded=not st.session_state.ingredients):
    with st.form(key='reg_form', clear_on_submit=True):
        name = st.text_input("材料名")
        c1, c2 = st.columns(2)
        vol = c1.number_input("内容量", min_value=1, value=1000)
        unit = c2.selectbox("単位", UNITS)
        price = st.number_input("購入価格(円)", min_value=0, value=500)
        if st.form_submit_button("材料リストに追加"):
            if name:
                st.session_state.ingredients.append({"name": name, "vol": vol, "price": price, "unit": unit})
                st.rerun()

if st.session_state.ingredients:
    with st.expander("📝 登録済みの材料を編集・削除"):
        for i, item in enumerate(st.session_state.ingredients):
            c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 0.5])
            new_name = c1.text_input("名前", value=item['name'], key=f"e_n_{i}")
            new_vol = c2.number_input("量", value=item['vol'], key=f"e_v_{i}")
            new_price = c3.number_input("価格", value=item['price'], key=f"e_p_{i}")
            c4.write(f"\n{item['unit']}")
            if c5.button("❌", key=f"d_{i}"):
                st.session_state.ingredients.pop(i)
                st.rerun()
            st.session_state.ingredients[i] = {"name": new_name, "vol": new_vol, "price": new_price, "unit": item['unit']}

# --- ② 原価を計算 ---
st.write(" ")
st.markdown('<div class="notranslate section-title">② 原価を計算する</div>', unsafe_allow_html=True)

if not st.session_state.ingredients:
    st.info("材料を登録してください。")
else:
    mode = st.radio("計算モード", ["1人あたりの使用量で計算", "全体の分量から人数で割る"], horizontal=True)
    total_material_cost = 0.0
    line_details = ""
    
    if mode == "全体の分量から人数で割る":
        serving_count = st.number_input("何人分作りますか？", min_value=1, value=50)
        for i, item in enumerate(st.session_state.ingredients):
            st.markdown(f'<div class="item-box notranslate">{item["name"]}</div>', unsafe_allow_html=True)
            u_p = item['price'] / item['vol']
            step_val = 0.5 if item['unit'] in INT_UNITS else 1.0
            used_all = st.number_input(f"合計の使用量 ({item['unit']})", key=f"all_{i}", min_value=0.0, step=step_val)
            item_total = used_all * u_p
            total_material_cost += item_total
            line_details += f"・{item['name']}: {used_all}{item['unit']} ({item_total:,.1f}円)\n"
            st.write(f"小計: {item_total:,.1f} 円")
    else:
        serving_count = 1
        for i, item in enumerate(st.session_state.ingredients):
            st.markdown(f'<div class="item-box notranslate">{item["name"]}</div>', unsafe_allow_html=True)
            u_p = item['price'] / item['vol']
            if item['unit'] in INT_UNITS:
                choice = st.selectbox(f"使用数 ({item['unit']})", list(FRACTIONS.keys()), key=f"fr_{i}")
                used = FRACTIONS[choice]
                used_label = choice
            else:
                used = st.number_input(f"使用量 ({item['unit']})", key=f"ind_{i}", min_value=0.0, step=0.1)
                used_label = str(used)
            item_cost = used * u_p
            total_material_cost += item_cost
            line_details += f"・{item['name']}: {used_label}{item['unit']} ({item_cost:,.2f}円)\n"
            st.write(f"小計: {item_cost:,.2f} 円")

    final_cost = total_material_cost / serving_count
    
    # 結果表示
    st.markdown(f"""
        <div class="price-card notranslate">
            <p style="margin:0; color:#b91c1c; font-weight:bold;">💰 1人あたりの原価</p>
            <h1 style="margin:5px 0; color:#b91c1c; font-size: 2.8rem;">{final_cost:,.2f} 円</h1>
            <p style="margin:0; color:#666;">(総額 {total_material_cost:,.0f}円 ÷ {serving_count}人分)</p>
        </div>
    """, unsafe_allow_html=True)

    # --- 📸 LINE貼り付け用 ---
    st.write(" ")
    st.subheader("📸 結果を共有する")
    summary = f"【文化祭原価計算結果】\nモード: {mode}\n"
    if mode == "全体の分量から人数で割る":
        summary += f"予定数: {serving_count}人分\n"
    summary += f"{line_details}\n💰1人あたり原価: {final_cost:,.2f}円"
    
    st.info("💡 下の枠内を全選択してコピーし、LINEに貼り付けてください。")
    st.text_area("LINE貼り付け用テキスト", value=summary, height=200)

    if st.button("🚨 全データをリセット"):
        st.session_state.ingredients = []
        st.rerun()
