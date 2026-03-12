import streamlit as st
import streamlit.components.v1 as components
import json

# 1. ページ設定
st.set_page_config(page_title="文化祭原価計算アプリ", layout="centered")

# 2. JavaScript: 自動保存
def auto_save_and_load():
    js_code = """
    <script>
    window.saveToBr = (data) => { localStorage.setItem('bunkasai_data_v14', JSON.stringify(data)); };
    setTimeout(() => {
        const saved = localStorage.getItem('bunkasai_data_v14');
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

# 3. CSS: ここで「謎のグレーの箱」と「その上の余白」を物理的に破壊します
st.markdown("""
    <style>
    /* 1. 全ての標準余白とラベル領域をゼロにする */
    [data-testid="stWidgetLabel"] { display: none !important; height: 0px !important; margin: 0px !important; padding: 0px !important; }
    .element-container, .stVerticalBlock { gap: 0rem !important; }
    
    /* 2. Expander（折りたたみ）自体の余白を削る */
    .stExpander { border: none !important; background: transparent !important; }
    [data-testid="stExpanderDetails"] { padding-top: 0px !important; }

    /* 3. 「グレーの長方形」の隙間を消し、上部に密着させる */
    div[data-testid="stTextInput"], div[data-testid="stNumberInput"], div[data-testid="stSelectbox"] {
        margin-top: -15px !important; /* これで上の隙間を強制的に埋めます */
    }

    /* 4. 入力欄の背景を白くし、枠線を細くして「謎の箱感」を消す */
    input, .stSelectbox div[data-baseweb="select"] {
        background-color: white !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }

    /* デザインラベル */
    .field-tag {
        font-size: 0.8rem;
        font-weight: 800;
        color: #3b82f6;
        margin-bottom: 2px;
        margin-top: 12px;
        display: block;
        z-index: 10;
        position: relative;
    }

    .main-card {
        background-color: #f1f5f9;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
    }
    @media (prefers-color-scheme: dark) {
        .main-card { background-color: #0f172a; border-color: #1e293b; }
        input, .stSelectbox div[data-baseweb="select"] { background-color: #1e293b !important; color: white !important; }
    }

    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; background-color: #3b82f6; color: white !important; height: 3rem; margin-top: 15px; }
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

st.markdown('<h2 style="text-align:center; color:#3b82f6; font-size:1.5rem;">🎡 文化祭原価計算</h2>', unsafe_allow_html=True)

# --- ① 材料を登録 ---
with st.expander("➕ 材料を追加する", expanded=not st.session_state.ingredients):
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # --- 材料名 ---
    st.markdown('<span class="field-tag">材料名</span>', unsafe_allow_html=True)
    name = st.text_input("n", placeholder="例：鶏肉", label_visibility="collapsed")
    
    # --- 内容量と単位 ---
    c1, c2 = st.columns([2, 1])
    with c1: st.markdown('<span class="field-tag">内容量</span>', unsafe_allow_html=True)
    with c2:
        st.markdown('<span class="field-tag">単位</span>', unsafe_allow_html=True)
        u = st.selectbox("u", ["個", "本", "袋", "g", "kg", "ml", "l"], label_visibility="collapsed")
    
    with c1:
        if u in ["個", "本", "袋"]:
            v = st.number_input("vi", min_value=1, value=10, step=1, label_visibility="collapsed")
        else:
            v = st.number_input("vf", min_value=0.1, value=1000.0, step=0.1, label_visibility="collapsed")
    
    # --- 価格 ---
    st.markdown('<span class="field-tag">入力モード</span>', unsafe_allow_html=True)
    pm = st.radio("pm", ["総額", f"1{u}単価"], horizontal=True, label_visibility="collapsed")
    
    if "総額" in pm:
        st.markdown('<span class="field-tag">購入総額 (円)</span>', unsafe_allow_html=True)
        p = st.number_input("pt", min_value=0, value=500, step=1, label_visibility="collapsed")
    else:
        st.markdown(f'<span class="field-tag">1{u}単価 (円)</span>', unsafe_allow_html=True)
        up = st.number_input("pu", min_value=0.0, value=10.0, step=0.1, label_visibility="collapsed")
        p = int(up * v)
        st.caption(f"合計: {p:,} 円")

    if st.button("材料を追加"):
        if name:
            st.session_state.ingredients.append({"name": name, "vol": float(v), "price": int(p), "unit": u})
            save_trigger(st.session_state.ingredients); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- ② 編集・計算 ---
if st.session_state.ingredients:
    st.write("---")
    with st.expander("📝 材料の確認・削除"):
        for i, item in enumerate(st.session_state.ingredients):
            col_n, col_d = st.columns([3, 1])
            col_n.write(f"**{item['name']}** ({item['vol']}{item['unit']} / {item['price']}円)")
            if col_d.button("❌", key=f"del_{i}"):
                st.session_state.ingredients.pop(i)
                save_trigger(st.session_state.ingredients); st.rerun()

    st.markdown('<h3 style="font-size:1.1rem; border-bottom:2px solid #3b82f6;">② 原価計算</h3>', unsafe_allow_html=True)
    mode = st.radio("cm", ["使用量で計算", "まとめてモード"], horizontal=True, label_visibility="collapsed")
    tc = 0.0; details = ""
    
    if mode == "まとめてモード":
        st.markdown('<span class="field-tag">何人分？</span>', unsafe_allow_html=True)
        sc = st.number_input("sc", min_value=1, value=50, label_visibility="collapsed")
        for item in st.session_state.ingredients:
            tc += float(item['price'])
            details += f"・{item['name']}: {item['vol']}{item['unit']}\n"
    else:
        sc = 1
        for i, item in enumerate(st.session_state.ingredients):
            st.markdown(f'<span class="field-tag">{item["name"]}</span>', unsafe_allow_html=True)
            u_p = item['price'] / item['vol']
            u_amt = st.number_input(f"u_{i}", min_value=0.0, max_value=float(item['vol']), value=0.0, step=0.1, label_visibility="collapsed")
            ic = u_amt * u_p; tc += ic; details += f"・{item['name']}: {u_amt}{item['unit']}\n"

    final = tc / sc
    st.markdown(f"""<div style="background-color:#fef2f2; padding:15px; border-radius:15px; border:2px solid #ef4444; text-align:center; margin-top:10px;">
        <span style="font-size:0.9rem; color:#ef4444; font-weight:bold;">1人あたりの原価</span><br>
        <span style="font-size:2rem; font-weight:900; color:#ef4444;">{final:,.1f} 円</span>
    </div>""", unsafe_allow_html=True)
    
    if st.button("🚨 リセット"):
        st.session_state.ingredients = []; save_trigger([]); st.rerun()
