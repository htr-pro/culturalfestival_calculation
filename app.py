import streamlit as st
import streamlit.components.v1 as components
import json

# 1. ページ設定
st.set_page_config(page_title="文化祭原価計算アプリ", layout="centered")

# 2. JavaScript: 自動保存・復元
def auto_save_and_load():
    js_code = """
    <script>
    window.saveToBr = (data) => {
        localStorage.setItem('bunkasai_data_v11', JSON.stringify(data));
    };
    setTimeout(() => {
        const saved = localStorage.getItem('bunkasai_data_v11');
        if (saved) {
            const bridge = parent.document.querySelector('textarea[aria-label="bridge_area"]');
            if (bridge && !bridge.value) {
                bridge.value = saved;
                bridge.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
    }, 500);
    </script>
    """
    components.html(js_code, height=0)

def save_trigger(data):
    js_code = f"<script>window.saveToBr({json.dumps(data)});</script>"
    components.html(js_code, height=0)

# 3. CSS: システムの余白を殺して自前で制御する
st.markdown("""
    <style>
    /* 標準ラベルを全消しして「予約スペース」自体を抹殺 */
    div[data-testid="stWidgetLabel"] { display: none !important; }
    
    .main-title { font-size: 1.6rem !important; text-align: center; color: #3b82f6; font-weight: 900; margin-bottom: 20px; }
    .section-title { font-size: 1.2rem !important; font-weight: 800; border-bottom: 3px solid #3b82f6; display: inline-block; margin-top: 10px; margin-bottom: 15px; }
    
    /* 自前で作るラベルのスタイル */
    .field-label {
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 4px;
        color: #475569;
        display: block;
    }
    @media (prefers-color-scheme: dark) { .field-label { color: #cbd5e1; } }

    /* フォームの枠 */
    .custom-form { 
        border: 1px solid #e2e8f0; padding: 20px; border-radius: 15px; background-color: #f8fafc; margin-bottom: 20px;
    }
    @media (prefers-color-scheme: dark) { .custom-form { border-color: #334155; background-color: #1e293b; } }

    /* 入力パーツを整列 */
    .stTextInput, .stNumberInput, .stSelectbox { margin-bottom: 15px !important; }
    
    /* 1人あたり原価のカード */
    .price-card { background-color: #fef2f2; padding: 20px; border-radius: 15px; border: 2px solid #ef4444; text-align: center; }
    @media (prefers-color-scheme: dark) { .price-card { background-color: #450a0a; } }
    
    /* ボタン */
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; background-color: #3b82f6; color: white !important; height: 3rem; }
    
    /* ブリッジエリアを隠す */
    div[data-testid="stTextArea"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

if 'ingredients' not in st.session_state:
    st.session_state.ingredients = []

bridge_data = st.text_area("bridge_area", key="bridge_area", label_visibility="collapsed")
if bridge_data and not st.session_state.ingredients:
    try:
        st.session_state.ingredients = json.loads(bridge_data)
        st.rerun()
    except: pass

auto_save_and_load()

st.markdown('<h1 class="main-title">🎡 文化祭原価計算アプリ</h1>', unsafe_allow_html=True)

# --- ① 材料を登録 ---
st.markdown('<div class="section-title">① 材料を登録・編集する</div>', unsafe_allow_html=True)

with st.expander("➕ 新しい材料を追加する", expanded=not st.session_state.ingredients):
    st.markdown('<div class="custom-form">', unsafe_allow_html=True)
    
    # --- 材料名 ---
    st.markdown('<span class="field-label">材料名</span>', unsafe_allow_html=True)
    name = st.text_input("name", placeholder="例：鶏もも肉", label_visibility="collapsed")
    
    # --- 内容量と単位 ---
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<span class="field-label">内容量</span>', unsafe_allow_html=True)
        # 単位を先に判断するために一度変数を確保
        pass 
    with col2:
        st.markdown('<span class="field-label">単位</span>', unsafe_allow_html=True)
        selected_unit = st.selectbox("unit", ["個", "本", "袋", "g", "kg", "ml", "l"], label_visibility="collapsed")

    # 内容量の実体（単位によって整数/小数を分ける）
    with col1:
        if selected_unit in ["個", "本", "袋"]:
            vol = st.number_input("vol_int", min_value=1, value=10, step=1, label_visibility="collapsed")
        else:
            vol = st.number_input("vol_float", min_value=0.1, value=1000.0, step=0.1, label_visibility="collapsed")
    
    # --- 価格入力 ---
    st.markdown('<span class="field-label">価格の入力方法</span>', unsafe_allow_html=True)
    price_mode = st.radio("mode", ["総額で入力", f"1{selected_unit}あたりの価格で入力"], horizontal=True, label_visibility="collapsed")
    
    if "総額" in price_mode:
        st.markdown('<span class="field-label">購入総額 (円)</span>', unsafe_allow_html=True)
        price = st.number_input("price", min_value=0, value=500, step=1, label_visibility="collapsed")
    else:
        st.markdown(f'<span class="field-label">1{selected_unit}あたりの価格 (円)</span>', unsafe_allow_html=True)
        u_price = st.number_input("u_price", min_value=0.0, value=10.0, step=0.1, label_visibility="collapsed")
        price = int(u_price * vol)
        st.info(f"💡 合計額: {price:,} 円")

    st.write("")
    if st.button("材料リストに追加"):
        if name:
            st.session_state.ingredients.append({"name": name, "vol": float(vol), "price": int(price), "unit": selected_unit})
            save_trigger(st.session_state.ingredients)
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

# --- ② 編集・削除 ---
if st.session_state.ingredients:
    with st.expander("📝 登録済みの材料を編集・削除"):
        for i, item in enumerate(st.session_state.ingredients):
            c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 0.8, 0.5])
            new_name = c1.text_input(f"e_n_{i}", value=item['name'], label_visibility="collapsed")
            if item['unit'] in ["個", "本", "袋"]:
                new_vol = c2.number_input(f"e_v_{i}", value=int(item['vol']), step=1, label_visibility="collapsed")
            else:
                new_vol = c2.number_input(f"e_v_{i}", value=float(item['vol']), step=0.1, label_visibility="collapsed")
            new_price = c3.number_input(f"e_p_{i}", value=int(item['price']), step=1, label_visibility="collapsed")
            c4.markdown(f'<p style="margin-top:10px;">{item["unit"]}</p>', unsafe_allow_html=True)
            if c5.button("❌", key=f"d_{i}"):
                st.session_state.ingredients.pop(i)
                save_trigger(st.session_state.ingredients)
                st.rerun()
            st.session_state.ingredients[i] = {"name": new_name, "vol": float(new_vol), "price": int(new_price), "unit": item['unit']}

# --- ③ 原価計算 ---
st.markdown('<div class="section-title">② 原価を計算する</div>', unsafe_allow_html=True)

if not st.session_state.ingredients:
    st.info("材料を登録してください。")
else:
    mode = st.radio("c_mode", ["1人あたりの使用量で計算", "まとめてモード"], horizontal=True, label_visibility="collapsed")
    total_material_cost = 0.0
    line_details = ""
    
    if mode == "まとめてモード":
        st.markdown('<span class="field-label">合計何人分作る？</span>', unsafe_allow_html=True)
        serving_count = st.number_input("s_count", min_value=1, value=50, label_visibility="collapsed")
        for i, item in enumerate(st.session_state.ingredients):
            st.markdown(f'<b>・{item["name"]}</b> ({item["vol"]}{item["unit"]})', unsafe_allow_html=True)
            total_material_cost += float(item['price'])
            p_p = item['vol'] / serving_count
            line_details += f"・{item['name']}: 全量{item['vol']}{item['unit']} (1人当り:{p_p:,.2f}{item['unit']})\n"
    else:
        serving_count = 1
        FRACTIONS = {"なし (0)": 0.0, "1/4 (0.25)": 0.25, "1/3 (0.33)": 0.33, "1/2 (0.5)": 0.5, "2/3 (0.66)": 0.66, "3/4 (0.75)": 0.75}
        for i, item in enumerate(st.session_state.ingredients):
            st.write(f"**{item['name']}**")
            u_p = item['price'] / item['vol']
            if item['unit'] in ["個", "本", "袋"]:
                col_i, col_f = st.columns(2)
                iv = col_i.selectbox(f"int_{i}", range(int(item['vol']) + 1), label_visibility="collapsed")
                fk = col_f.selectbox(f"frc_{i}", list(FRACTIONS.keys()), label_visibility="collapsed")
                used = float(iv) + FRACTIONS[fk]
                used_l = f"{iv}と{fk}" if FRACTIONS[fk] > 0 else f"{iv}"
            else:
                used = st.number_input(f"use_{i}", min_value=0.0, max_value=float(item['vol']), step=0.1, label_visibility="collapsed")
                used_l = str(used)
            item_c = used * u_p
            total_material_cost += item_c
            line_details += f"・{item['name']}: {used_l}{item['unit']} ({item_c:,.2f}円)\n"

    final_cost = total_material_cost / serving_count
    st.markdown(f"""<div class="price-card">💰 1人あたりの原価<br><span style="font-size: 2rem; font-weight: 900; color: #ef4444;">{final_cost:,.2f} 円</span><br>(総額 {total_material_cost:,.0f}円 ÷ {serving_count}人分)</div>""", unsafe_allow_html=True)

    st.write(" ")
    summary = f"【文化祭原価計算結果】\nモード: {mode}\n予定数: {serving_count}人分\n{line_details}\n💰1人あたり原価: {final_cost:,.2f}円"
    st.text_area("共有用", value=summary, height=150, label_visibility="collapsed")

    if st.button("🚨 全データをリセット"):
        st.session_state.ingredients = []
        save_trigger([])
        st.rerun()
