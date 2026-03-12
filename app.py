import streamlit as st
import streamlit.components.v1 as components
import json

# 1. ページ設定
st.set_page_config(page_title="文化祭原価計算アプリ", layout="centered")

# 2. CSS: 文字サイズとデザインの微調整
st.markdown("""
    <style>
    :root { --text-color: #1e293b; --bg-color: #ffffff; --box-bg: #f1f5f9; --accent-blue: #3b82f6; }
    @media (prefers-color-scheme: dark) { :root { --text-color: #f1f5f9; --bg-color: #0f172a; --box-bg: #1e293b; --accent-blue: #60a5fa; } }
    .notranslate { translate: no !important; }
    .main-title { font-size: 6vw !important; text-align: center; color: var(--accent-blue); font-weight: 900; margin-bottom: 15px; }
    .section-title { font-size: 4.5vw !important; font-weight: 800; color: var(--text-color); border-bottom: 3px solid var(--accent-blue); display: inline-block; margin-top: 15px; margin-bottom: 10px; }
    @media (min-width: 600px) { .main-title { font-size: 2.2rem !important; } .section-title { font-size: 1.5rem !important; } }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; background-color: var(--accent-blue); color: white !important; }
    .price-card { background-color: #fef2f2; padding: 20px; border-radius: 15px; border: 2px solid #ef4444; text-align: center; margin-top: 10px; }
    @media (prefers-color-scheme: dark) { .price-card { background-color: #450a0a; } }
    .item-box { background-color: var(--box-bg); padding: 10px; border-radius: 8px; border-left: 6px solid var(--accent-blue); margin-bottom: 5px; font-weight: bold; color: var(--text-color); }
    </style>
    """, unsafe_allow_html=True)

# ブラウザ保存用JS
def save_data(data):
    js_code = f"<script>localStorage.setItem('bunkasai_data', '{json.dumps(data)}');</script>"
    components.html(js_code, height=0)

if 'ingredients' not in st.session_state:
    st.session_state.ingredients = []

st.markdown('<div class="notranslate"><h1 class="main-title">🎡 文化祭原価計算アプリ</h1></div>', unsafe_allow_html=True)

# --- ① 材料を登録・編集 ---
st.markdown('<div class="notranslate section-title">① 材料を登録・編集する</div>', unsafe_allow_html=True)

with st.expander("➕ 新しい材料を追加する", expanded=not st.session_state.ingredients):
    with st.form(key='reg_form', clear_on_submit=True):
        name = st.text_input("材料名")
        c1, c2 = st.columns(2)
        vol = c1.number_input("内容量（購入数/量）", min_value=1.0, value=10.0, step=0.1)
        unit = c2.selectbox("単位", ["個", "本", "袋", "g", "kg", "ml", "l"])
        price = st.number_input("購入金額(円)", min_value=0, value=500)
        if st.form_submit_button("材料リストに追加"):
            if name:
                st.session_state.ingredients.append({"name": name, "vol": vol, "price": price, "unit": unit})
                save_data(st.session_state.ingredients)
                st.rerun()

if st.session_state.ingredients:
    with st.expander("📝 登録済みの材料を編集・削除"):
        for i, item in enumerate(st.session_state.ingredients):
            c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 0.5])
            new_name = c1.text_input("名前", value=item['name'], key=f"e_n_{i}")
            new_vol = c2.number_input("量", value=float(item['vol']), key=f"e_v_{i}", step=0.1)
            new_price = c3.number_input("価格", value=item['price'], key=f"e_p_{i}")
            c4.write(f"\n{item['unit']}")
            if c5.button("❌", key=f"d_{i}"):
                st.session_state.ingredients.pop(i)
                save_data(st.session_state.ingredients)
                st.rerun()
            st.session_state.ingredients[i] = {"name": new_name, "vol": new_vol, "price": new_price, "unit": item['unit']}
            save_data(st.session_state.ingredients)

# --- ② 原価を計算 ---
st.write(" ")
st.markdown('<div class="notranslate section-title">② 原価を計算する</div>', unsafe_allow_html=True)

if not st.session_state.ingredients:
    st.info("材料を登録してください。")
else:
    mode = st.radio("計算モード", ["1人あたりの使用量で計算", "まとめてモード"], horizontal=True)
    total_material_cost = 0.0
    line_details = ""
    
    if mode == "まとめてモード":
        serving_count = st.number_input("合計で何人分作りますか？", min_value=1, value=50)
        for i, item in enumerate(st.session_state.ingredients):
            st.markdown(f'<div class="item-box notranslate">{item["name"]} (全量: {item["vol"]}{item["unit"]})</div>', unsafe_allow_html=True)
            total_material_cost += float(item['price'])
            # 1人あたりの分量を計算
            per_person_vol = item['vol'] / serving_count
            line_details += f"・{item['name']}: 全量{item['vol']}{item['unit']} (1人当り:{per_person_vol:,.2f}{item['unit']})\n"
    else:
        serving_count = 1
        FRACTION_OPTIONS = {"なし (0)": 0.0, "1/4 (0.25)": 0.25, "1/3 (0.33)": 0.33, "1/2 (0.5)": 0.5, "2/3 (0.66)": 0.66, "3/4 (0.75)": 0.75}
        for i, item in enumerate(st.session_state.ingredients):
            st.markdown(f'<div class="item-box notranslate">{item["name"]}</div>', unsafe_allow_html=True)
            u_p = item['price'] / item['vol']
            if item['unit'] in ["個", "本", "袋"]:
                col_int, col_frac = st.columns(2)
                int_val = col_int.selectbox("整数", range(int(item['vol']) + 1), key=f"int_{i}")
                frac_key = col_frac.selectbox("端数", list(FRACTION_OPTIONS.keys()), key=f"frac_{i}")
                used = float(int_val) + FRACTION_OPTIONS[frac_key]
                used_label = f"{int_val}と{frac_key}" if FRACTION_OPTIONS[frac_key] > 0 else f"{int_val}"
            else:
                used = st.number_input(f"使用量 ({item['unit']})", key=f"ind_{i}", min_value=0.0, max_value=float(item['vol']), step=0.1)
                used_label = str(used)
            item_cost = used * u_p
            total_material_cost += item_cost
            line_details += f"・{item['name']}: {used_label}{item['unit']} ({item_cost:,.2f}円)\n"

    final_cost = total_material_cost / serving_count
    st.markdown(f"""<div class="price-card notranslate"><p style="margin:0; color:#ef4444; font-weight:bold;">💰 1人あたりの原価</p><h1 style="margin:5px 0; color:#ef4444; font-size: 2.5rem;">{final_cost:,.2f} 円</h1><p style="margin:0; font-size: 0.9rem;">(総額 {total_material_cost:,.0f}円 ÷ {serving_count}人分)</p></div>""", unsafe_allow_html=True)

    st.write(" ")
    st.subheader("📸 結果を共有する")
    summary = f"【文化祭原価計算結果】\nモード: {mode}\n"
    if mode == "まとめてモード": summary += f"予定数: {serving_count}人分\n"
    summary += f"{line_details}\n💰1人あたり原価: {final_cost:,.2f}円"
    
    # ラベルを「貼り付けテキスト」に変更
    st.text_area("貼り付けテキスト", value=summary, height=200)

    if st.button("🚨 全データを消去（リセット）"):
        st.session_state.ingredients = []
        save_data([])
        st.rerun()
