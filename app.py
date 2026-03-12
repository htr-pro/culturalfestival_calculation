import streamlit as st
import streamlit.components.v1 as components
import json

# 1. ページ設定
st.set_page_config(page_title="文化祭原価計算アプリ", layout="centered")

# 2. JavaScript: 自動保存
def auto_save_and_load():
    js_code = """
    <script>
    window.saveToBr = (data) => { localStorage.setItem('bunkasai_data_v16', JSON.stringify(data)); };
    setTimeout(() => {
        const saved = localStorage.getItem('bunkasai_data_v16');
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

# 3. CSS: 見やすさを重視した標準レイアウト
st.markdown("""
    <style>
    .main-title { font-size: 1.8rem !important; text-align: center; color: #3b82f6; font-weight: 900; margin-bottom: 20px; }
    .section-title { font-size: 1.2rem !important; font-weight: 800; border-left: 5px solid #3b82f6; padding-left: 10px; margin-bottom: 15px; }
    
    /* ボタンを押しやすく */
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; background-color: #3b82f6; color: white !important; height: 3.5rem; }
    
    /* 原価表示カード */
    .price-card { background-color: #fef2f2; padding: 25px; border-radius: 15px; border: 2px solid #ef4444; text-align: center; margin: 20px 0; }
    @media (prefers-color-scheme: dark) { .price-card { background-color: #450a0a; } }

    /* 隠し要素 */
    div[data-testid="stTextArea"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

if 'ingredients' not in st.session_state:
    st.session_state.ingredients = []

# localStorageとの橋渡し用（非表示）
bridge_data = st.text_area("bridge_area", key="bridge_area", label_visibility="collapsed")
if bridge_data and not st.session_state.ingredients:
    try:
        st.session_state.ingredients = json.loads(bridge_data); st.rerun()
    except: pass

auto_save_and_load()

st.markdown('<h1 class="main-title">🎡 文化祭原価計算アプリ</h1>', unsafe_allow_html=True)

# --- ① 材料を登録 ---
st.markdown('<div class="section-title">① 材料を登録</div>', unsafe_allow_html=True)

with st.expander("➕ 新しい材料を追加する", expanded=not st.session_state.ingredients):
    # 材料名
    name = st.text_input("材料名", placeholder="例：鶏もも肉")
    
    # 内容量と単位を横並びに
    col_v, col_u = st.columns([2, 1])
    unit = col_u.selectbox("単位", ["個", "本", "袋", "g", "kg", "ml", "l"])
    
    if unit in ["個", "本", "袋"]:
        vol = col_v.number_input(f"内容量（{unit}数）", min_value=1, value=1, step=1)
    else:
        vol = col_v.number_input(f"内容量（総量）", min_value=0.1, value=100.0, step=0.1)
    
    # 価格入力方法
    mode_price = st.radio("価格の入力方法", ["総額で入力", f"1{unit}あたりの価格で入力"], horizontal=True)
    
    if "総額" in mode_price:
        final_price_val = st.number_input("購入総額 (円)", min_value=0, value=0, step=1)
    else:
        # ここを整数入力（value=0, step=1）に固定しました
        unit_price = st.number_input(f"1{unit}あたりの価格 (円)", min_value=0, value=0, step=1)
        final_price_val = int(unit_price * vol)
        st.info(f"💡 計算された総額: {final_price_val:,} 円")

    if st.button("材料リストに追加"):
        if name:
            st.session_state.ingredients.append({
                "name": name, 
                "vol": float(vol), 
                "price": int(final_price_val), 
                "unit": unit
            })
            save_trigger(st.session_state.ingredients); st.rerun()
        else:
            st.warning("材料名を入力してください")

# --- ② 編集・確認 ---
if st.session_state.ingredients:
    with st.expander("📝 登録済みの材料を編集・削除"):
        for i, item in enumerate(st.session_state.ingredients):
            c1, c2, c3, c4 = st.columns([2, 1, 1, 0.5])
            c1.write(f"**{item['name']}**")
            c2.write(f"{item['vol']}{item['unit']}")
            c3.write(f"{item['price']}円")
            if c4.button("❌", key=f"del_{i}"):
                st.session_state.ingredients.pop(i)
                save_trigger(st.session_state.ingredients); st.rerun()

# --- ③ 原価計算 ---
st.markdown('<div class="section-title">② 原価を計算</div>', unsafe_allow_html=True)

if not st.session_state.ingredients:
    st.info("まずは上の「材料を追加する」から材料を登録してください。")
else:
    calc_mode = st.radio("計算モード", ["1人あたりの使用量で計算", "まとめてモード"], horizontal=True)
    total_cost = 0.0
    details = ""
    
    if calc_mode == "まとめてモード":
        servings = st.number_input("合計で何人分作りますか？", min_value=1, value=1)
        for item in st.session_state.ingredients:
            total_cost += float(item['price'])
            per_use = item['vol'] / servings
            details += f"・{item['name']}: {item['vol']}{item['unit']} (1人当り:{per_use:,.2f}{item['unit']})\n"
    else:
        servings = 1
        for i, item in enumerate(st.session_state.ingredients):
            st.markdown(f"**{item['name']}** の使用量")
            # 1単位あたりの単価を計算
            u_p = item['price'] / item['vol']
            
            if item['unit'] in ["個", "本", "袋"]:
                # 使用量も整数のほうが使いやすいため step=1.0 に設定
                use = st.number_input(f"使用数 ({item['unit']})", key=f"u_{i}", min_value=0.0, step=1.0)
            else:
                use = st.number_input(f"使用量 ({item['unit']})", key=f"u_{i}", min_value=0.0, step=0.1)
            
            item_cost = use * u_p
            total_cost += item_cost
            details += f"・{item['name']}: {use}{item['unit']} ({item_cost:,.1f}円)\n"

    final_price = total_cost / servings
    st.markdown(f"""<div class="price-card">
        <span style="font-size:1rem; color:#ef4444; font-weight:bold;">1人あたりの原価</span><br>
        <span style="font-size:2.5rem; font-weight:900; color:#ef4444;">{final_price:,.2f} 円</span>
    </div>""", unsafe_allow_html=True)

    summary = f"【原価計算結果】\n{details}💰1人あたり原価: {final_price:,.2f}円"
    st.text_area("結果（コピー用）", value=summary, height=150)

    if st.button("🚨 全データを消去してリセット"):
        st.session_state.ingredients = []; save_trigger([]); st.rerun()
