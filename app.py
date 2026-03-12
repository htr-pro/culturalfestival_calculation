import streamlit as st

# 1. ページ設定（スマホで見やすく）
st.set_page_config(page_title="文化祭原価計算", layout="centered")

# 2. デザイン（CSS）
st.markdown("""
    <style>
    .main-title { font-size: 1.8rem !important; text-align: center; color: #3b82f6; font-weight: 900; margin-bottom: 20px; }
    .section-title { font-size: 1.2rem !important; font-weight: 800; border-left: 5px solid #3b82f6; padding-left: 10px; margin-top: 20px; margin-bottom: 15px; }
    .price-card { background-color: #fef2f2; padding: 25px; border-radius: 15px; border: 2px solid #ef4444; text-align: center; margin: 20px 0; }
    @media (prefers-color-scheme: dark) { .price-card { background-color: #450a0a; } }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; background-color: #3b82f6; color: white !important; height: 3.5rem; }
    </style>
    """, unsafe_allow_html=True)

if 'ingredients' not in st.session_state:
    st.session_state.ingredients = []

st.markdown('<h1 class="main-title">🎡 文化祭原価計算アプリ</h1>', unsafe_allow_html=True)

# --- ① 材料を登録 ---
st.markdown('<div class="section-title">① 材料を登録</div>', unsafe_allow_html=True)

with st.expander("➕ 新しい材料を追加する", expanded=not st.session_state.ingredients):
    name = st.text_input("材料名", placeholder="例：鶏もも肉")
    
    col_v, col_u = st.columns([2, 1])
    unit = col_u.selectbox("単位", ["個", "本", "袋", "g", "kg", "ml", "l"])
    
    if unit in ["個", "本", "袋"]:
        vol = col_v.number_input(f"内容量（{unit}数）", min_value=1, value=1, step=1)
    else:
        vol = col_v.number_input(f"内容量（総量）", min_value=0.1, value=100.0, step=0.1)
    
    mode_price = st.radio("価格の入力方法", ["総額で入力", f"1{unit}あたりの単価で入力"], horizontal=True)
    
    if "総額" in mode_price:
        final_p = st.number_input("購入総額 (円)", min_value=0, value=0, step=1)
    else:
        u_p = st.number_input(f"1{unit}あたりの価格 (円)", min_value=0, value=0, step=1)
        final_p = int(u_p * vol)
        st.info(f"💡 合計額: {final_p:,} 円")

    if st.button("材料リストに追加"):
        if name:
            st.session_state.ingredients.append({"name": name, "vol": float(vol), "price": int(final_p), "unit": unit})
            st.rerun()

# --- ② 編集・確認 ---
if st.session_state.ingredients:
    with st.expander("📝 登録済みの材料を確認・削除"):
        for i, item in enumerate(st.session_state.ingredients):
            c1, c2, c3 = st.columns([3, 2, 1])
            c1.write(f"**{item['name']}**")
            c2.write(f"{item['vol']}{item['unit']} / {item['price']}円")
            if c3.button("❌", key=f"del_{i}"):
                st.session_state.ingredients.pop(i)
                st.rerun()

# --- ③ 原価計算 ---
st.markdown('<div class="section-title">② 原価を計算</div>', unsafe_allow_html=True)

if not st.session_state.ingredients:
    st.info("材料を登録すると計算が始まります。")
else:
    mode = st.radio("計算モード", ["1人あたりの使用量で計算", "まとめてモード（全量）"], horizontal=True)
    total_cost = 0.0
    details = ""
    
    if mode == "まとめてモード（全量）":
        servings = st.number_input("合計何人分作りますか？", min_value=1, value=50)
        for item in st.session_state.ingredients:
            total_cost += float(item['price'])
            details += f"・{item['name']}: {item['vol']}{item['unit']}\n"
    else:
        servings = 1
        # 分数選択の辞書
        FRAC = {"なし": 0.0, "1/4 (0.25)": 0.25, "1/3 (0.33)": 0.33, "1/2 (0.5)": 0.5, "2/3 (0.66)": 0.66, "3/4 (0.75)": 0.75}
        
        for i, item in enumerate(st.session_state.ingredients):
            st.markdown(f"**{item['name']}** の使用量")
            unit_p = item['price'] / item['vol']
            
            if item['unit'] in ["個", "本", "袋"]:
                # 整数と端数を分けて入力
                c_i, c_f = st.columns(2)
                iv = c_i.selectbox(f"整数", range(201), key=f"int_{i}")
                fk = c_f.selectbox(f"端数", list(FRAC.keys()), key=f"frac_{i}")
                use = float(iv) + FRAC[fk]
                lbl = f"{iv}と{fk}" if FRAC[fk] > 0 else f"{iv}"
            else:
                use = st.number_input(f"使用量 ({item['unit']})", key=f"u_{i}", min_value=0.0, step=0.1)
                lbl = f"{use}{item['unit']}"
            
            cost = use * unit_p
            total_cost += cost
            details += f"・{item['name']}: {lbl} ({cost:,.1f}円)\n"

    final_price = total_cost / servings
    st.markdown(f"""<div class="price-card">
        <span style="font-size:1rem; color:#ef4444; font-weight:bold;">1人あたりの原価</span><br>
        <span style="font-size:2.5rem; font-weight:900; color:#ef4444;">{final_price:,.2f} 円</span>
    </div>""", unsafe_allow_html=True)

    summary = f"【文化祭原価計算結果】\n{details}💰1人あたり原価: {final_price:,.2f}円"
    st.text_area("結果（コピー用）", value=summary, height=150)

    if st.button("🚨 全データを消去してリセット"):
        st.session_state.ingredients = []
        st.rerun()
