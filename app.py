import streamlit as st
import streamlit.components.v1 as components
import json

# 1. ページ設定
st.set_page_config(page_title="文化祭原価計算アプリ", layout="centered")

# 2. JavaScript: 自動保存
def auto_save_and_load():
    js_code = """
    <script>
    window.saveToBr = (data) => { localStorage.setItem('bunkasai_data_v13', JSON.stringify(data)); };
    setTimeout(() => {
        const saved = localStorage.getItem('bunkasai_data_v13');
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

# 3. CSS: 「薄いグレーの長方形」と余白の徹底除去
st.markdown("""
    <style>
    /* 標準のラベルと余白を完全に殺す */
    div[data-testid="stWidgetLabel"] { display: none !important; }
    div[data-testid="stVerticalBlock"] > div { padding: 0 !important; margin: 0 !important; }

    /* Expander内の余白をリセット */
    div[data-testid="stExpander"] div[role="region"] > div { padding: 10px !important; }

    /* 各入力パーツの隙間を詰める */
    .element-container { margin-bottom: 0px !important; }
    
    /* 1. 材料登録エリアを「1つの綺麗なカード」にする */
    .registration-card {
        background-color: #f8fafc;
        border: 2px solid #e2e8f0;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
    }
    @media (prefers-color-scheme: dark) {
        .registration-card { background-color: #1e293b; border-color: #334155; }
    }

    /* ラベル風テキスト */
    .field-title {
        font-size: 0.85rem;
        font-weight: 800;
        color: #3b82f6;
        margin-bottom: 4px;
        margin-top: 10px;
        display: block;
    }

    /* ボタン */
    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; background-color: #3b82f6; color: white !important; height: 3.2rem; margin-top: 15px; border: none; }
    
    /* 結果カード */
    .price-card { background-color: #fef2f2; padding: 20px; border-radius: 15px; border: 2px solid #ef4444; text-align: center; margin-top: 10px; }
    @media (prefers-color-scheme: dark) { .price-card { background-color: #450a0a; } }
    
    .main-title { font-size: 1.6rem !important; text-align: center; color: #3b82f6; font-weight: 900; margin-bottom: 10px; }
    .section-title { font-size: 1.1rem !important; font-weight: 800; border-bottom: 3px solid #3b82f6; display: inline-block; margin-bottom: 15px; }

    div[data-testid="stTextArea"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

if 'ingredients' not in st.session_state:
    st.session_state.ingredients = []

bridge_data = st.text_area("bridge_area", key="bridge_area", label_visibility="collapsed")
if bridge_data and not st.session_state.ingredients:
    try:
        st.session_state.ingredients = json.loads(bridge_data); st.rerun()
    except: pass

auto_save_and_load()

st.markdown('<h1 class="main-title">🎡 文化祭原価計算アプリ</h1>', unsafe_allow_html=True)

# --- ① 材料を登録 ---
st.markdown('<div class="section-title">① 材料を登録・編集する</div>', unsafe_allow_html=True)

with st.expander("➕ 新しい材料を追加する", expanded=not st.session_state.ingredients):
    st.markdown('<div class="registration-card">', unsafe_allow_html=True)
    
    # --- 材料名 ---
    st.markdown('<span class="field-title">材料名</span>', unsafe_allow_html=True)
    name = st.text_input("name", placeholder="例：鶏もも肉", label_visibility="collapsed")
    
    # --- 内容量と単位 ---
    c_vol, c_unit = st.columns([2, 1])
    with c_vol: st.markdown('<span class="field-title">内容量</span>', unsafe_allow_html=True)
    with c_unit:
        st.markdown('<span class="field-title">単位</span>', unsafe_allow_html=True)
        u = st.selectbox("unit", ["個", "本", "袋", "g", "kg", "ml", "l"], label_visibility="collapsed")
    
    with c_vol:
        if u in ["個", "本", "袋"]:
            v = st.number_input("v_i", min_value=1, value=10, step=1, label_visibility="collapsed")
        else:
            v = st.number_input("v_f", min_value=0.1, value=1000.0, step=0.1, label_visibility="collapsed")
    
    # --- 価格 ---
    st.markdown('<span class="field-title">価格の入力方法</span>', unsafe_allow_html=True)
    pm = st.radio("pm", ["総額で入力", f"1{u}あたりの価格で入力"], horizontal=True, label_visibility="collapsed")
    
    if "総額" in pm:
        st.markdown('<span class="field-title">購入総額 (円)</span>', unsafe_allow_html=True)
        p = st.number_input("p_tot", min_value=0, value=500, step=1, label_visibility="collapsed")
    else:
        st.markdown(f'<span class="field-title">1{u}あたりの価格 (円)</span>', unsafe_allow_html=True)
        up = st.number_input("p_u", min_value=0.0, value=10.0, step=0.1, label_visibility="collapsed")
        p = int(up * v)
        st.info(f"💡 合計額: {p:,} 円")

    if st.button("材料リストに追加"):
        if name:
            st.session_state.ingredients.append({"name": name, "vol": float(v), "price": int(p), "unit": u})
            save_trigger(st.session_state.ingredients); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- ② 編集・削除 ---
if st.session_state.ingredients:
    with st.expander("📝 登録済みの材料を編集・削除"):
        for i, item in enumerate(st.session_state.ingredients):
            c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 0.8, 0.5])
            n_n = c1.text_input(f"e_n_{i}", value=item['name'], label_visibility="collapsed")
            if item['unit'] in ["個", "本", "袋"]:
                n_v = c2.number_input(f"e_v_{i}", value=int(item['vol']), step=1, label_visibility="collapsed")
            else:
                n_v = c2.number_input(f"e_v_{i}", value=float(item['vol']), step=0.1, label_visibility="collapsed")
            n_p = c3.number_input(f"e_p_{i}", value=int(item['price']), step=1, label_visibility="collapsed")
            c4.markdown(f'<p style="margin-top:10px; font-weight:bold;">{item["unit"]}</p>', unsafe_allow_html=True)
            if c5.button("❌", key=f"d_{i}"):
                st.session_state.ingredients.pop(i)
                save_trigger(st.session_state.ingredients); st.rerun()
            st.session_state.ingredients[i] = {"name": n_n, "vol": float(n_v), "price": int(n_p), "unit": item['unit']}

# --- ③ 原価計算 ---
st.markdown('<div class="section-title">② 原価を計算する</div>', unsafe_allow_html=True)

if not st.session_state.ingredients:
    st.info("材料を登録してください。")
else:
    mode = st.radio("cm", ["1人あたりの使用量で計算", "まとめてモード"], horizontal=True, label_visibility="collapsed")
    tc = 0.0; details = ""
    
    if mode == "まとめてモード":
        st.markdown('<span class="field-title">合計何人分作る？</span>', unsafe_allow_html=True)
        sc = st.number_input("sc", min_value=1, value=50, label_visibility="collapsed")
        for item in st.session_state.ingredients:
            tc += float(item['price'])
            pp = item['vol'] / sc
            details += f"・{item['name']}: {item['vol']}{item['unit']} (1人当り:{pp:,.2f}{item['unit']})\n"
    else:
        sc = 1; FRAC = {"なし (0)": 0.0, "1/4 (0.25)": 0.25, "1/3 (0.33)": 0.33, "1/2 (0.5)": 0.5, "2/3 (0.66)": 0.66, "3/4 (0.75)": 0.75}
        for i, item in enumerate(st.session_state.ingredients):
            st.markdown(f'<span class="field-title">{item["name"]}</span>', unsafe_allow_html=True)
            up = item['price'] / item['vol']
            if item['unit'] in ["個", "本", "袋"]:
                c_i, c_f = st.columns(2)
                iv = c_i.selectbox(f"i_{i}", range(int(item['vol']) + 1), label_visibility="collapsed")
                fk = c_f.selectbox(f"f_{i}", list(FRAC.keys()), label_visibility="collapsed")
                u_amt = float(iv) + FRAC[fk]
                u_lbl = f"{iv}と{fk}" if FRAC[fk] > 0 else f"{iv}"
            else:
                u_amt = st.number_input(f"u_{i}", min_value=0.0, max_value=float(item['vol']), step=0.1, label_visibility="collapsed")
                u_lbl = str(u_amt)
            ic = u_amt * up; tc += ic; details += f"・{item['name']}: {u_lbl}{item['unit']} ({ic:,.1f}円)\n"

    final = tc / sc
    st.markdown(f"""<div class="price-card">💰 1人あたりの原価<br><span style="font-size: 2.2rem; font-weight: 900; color: #ef4444;">{final:,.2f} 円</span></div>""", unsafe_allow_html=True)
    summary = f"【文化祭原価計算】\n{details}\n💰1人あたり原価: {final:,.2f}円"
    st.text_area("copy", value=summary, height=120, label_visibility="collapsed")

    if st.button("🚨 全データをリセット"):
        st.session_state.ingredients = []; save_trigger([]); st.rerun()
