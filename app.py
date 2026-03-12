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
        localStorage.setItem('bunkasai_data_v4', JSON.stringify(data));
    };
    setTimeout(() => {
        const saved = localStorage.getItem('bunkasai_data_v4');
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

# 3. CSS: スタイル
st.markdown("""
    <style>
    .main-title { font-size: 1.6rem !important; text-align: center; color: #3b82f6; font-weight: 900; margin-bottom: 5px; }
    .section-title { font-size: 1.2rem !important; font-weight: 800; border-bottom: 3px solid #3b82f6; display: inline-block; margin-top: 10px; margin-bottom: 10px; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; background-color: #3b82f6; color: white !important; }
    .price-card { background-color: #fef2f2; padding: 15px; border-radius: 15px; border: 2px solid #ef4444; text-align: center; }
    @media (prefers-color-scheme: dark) { .price-card { background-color: #450a0a; } }
    div[data-testid="stTextArea"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

if 'ingredients' not in st.session_state:
    st.session_state.ingredients = []

# データ復元ブリッジ
bridge_data = st.text_area("bridge_area", key="bridge_area", label_visibility="collapsed")
if bridge_data and not st.session_state.ingredients:
    try:
        st.session_state.ingredients = json.loads(bridge_data)
        st.rerun()
    except: pass

auto_save_and_load()

st.markdown('<h1 class="main-title">🎡 文化祭原価計算アプリ</h1>', unsafe_allow_html=True)

# --- ① 材料を登録・編集 ---
st.markdown('<div class="section-title">① 材料を登録・編集する</div>', unsafe_allow_html=True)

with st.expander("➕ 新しい材料を追加する", expanded=not st.session_state.ingredients):
    with st.form(key='reg_form', clear_on_submit=True):
        name = st.text_input("材料名")
        col_vol, col_unit = st.columns([2, 1])
        selected_unit = col_unit.selectbox("単位", ["個", "本", "袋", "g", "kg", "ml", "l"])
        
        # 内容量の入力（単位によってステップを切り替え）
        if selected_unit in ["個", "本", "袋"]:
            vol = col_vol.number_input(f"内容量（購入{selected_unit}数）", min_value=1.0, value=10.0, step=1.0)
        else:
            vol = col_vol.number_input(f"内容量（総{selected_unit}数）", min_value=0.1, value=1000.0, step=0.1)
        
        # 1. 修正：ラジオボタンのラベルを単位連動に
        price_mode = st.radio("価格の入力方法", ["総額で入力", f"1{selected_unit}あたりの価格で入力"], horizontal=True)
        
        # 2. 修正：数値入力の型を常にfloat(小数対応)で統一しつつ表示を制御
        if "総額" in price_mode:
            price = st.number_input("購入総額(円)", min_value=0, value=500, step=1)
        else:
            # 1つ目の登録後も小数入力ができるよう明示的にstep=0.1を指定
            u_p = st.number_input(f"1{selected_unit}あたりの価格(円)", min_value=0.0, value=10.0, step=0.1)
            price = int(u_p * vol)
            # 3. 修正：総額入力時はこのメッセージを出さない
            st.info(f"➡ 計算された総額: {price:,} 円")

        if st.form_submit_button("材料リストに追加"):
            if name:
                st.session_state.ingredients.append({"name": name, "vol": float(vol), "price": int(price), "unit": selected_unit})
                save_trigger(st.session_state.ingredients)
                st.rerun()

if st.session_state.ingredients:
    with st.expander("📝 登録済みの材料を編集・削除"):
        for i, item in enumerate(st.session_state.ingredients):
            c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 0.5])
            new_name = c1.text_input("名前", value=item['name'], key=f"e_n_{i}")
            new_vol = c2.number_input("量", value=float(item['vol']), key=f"e_v_{i}", step=0.1)
            new_price = c3.number_input("価格", value=int(item['price']), key=f"e_p_{i}", step=1)
            c4.write(f"\n{item['unit']}")
            if c5.button("❌", key=f"d_{i}"):
                st.session_state.ingredients.pop(i)
                save_trigger(st.session_state.ingredients)
                st.rerun()
            st.session_state.ingredients[i] = {"name": new_name, "vol": float(new_vol), "price": int(new_price), "unit": item['unit']}

# --- ② 原価を計算 ---
st.markdown('<div class="section-title">② 原価を計算する</div>', unsafe_allow_html=True)

if not st.session_state.ingredients:
    st.info("材料を登録してください。")
else:
    mode = st.radio("計算モード", ["1人あたりの使用量で計算", "まとめてモード"], horizontal=True)
    total_material_cost = 0.0
    line_details = ""
    
    if mode == "まとめてモード":
        serving_count = st.number_input("合計で何人分作りますか？", min_value=1, value=50)
        for i, item in enumerate(st.session_state.ingredients):
            st.markdown(f'<b>・{item["name"]}</b> (全量: {item["vol"]}{item["unit"]})', unsafe_allow_html=True)
            total_material_cost += float(item['price'])
            per_p = item['vol'] / serving_count
            line_details += f"・{item['name']}: 全量{item['vol']}{item['unit']} (1人当り:{per_p:,.2f}{item['unit']})\n"
    else:
        serving_count = 1
        FRACTION_OPTIONS = {"なし (0)": 0.0, "1/4 (0.25)": 0.25, "1/3 (0.33)": 0.33, "1/2 (0.5)": 0.5, "2/3 (0.66)": 0.66, "3/4 (0.75)": 0.75}
        for i, item in enumerate(st.session_state.ingredients):
            st.write(f"**{item['name']}**")
            u_p = item['price'] / item['vol']
            if item['unit'] in ["個", "本", "袋"]:
                col_i, col_f = st.columns(2)
                iv = col_i.selectbox("整数", range(int(item['vol']) + 1), key=f"int_{i}")
                fk = col_f.selectbox("端数", list(FRACTION_OPTIONS.keys()), key=f"frac_{i}")
                used = float(iv) + FRACTION_OPTIONS[fk]
                used_l = f"{iv}と{fk}" if FRACTION_OPTIONS[fk] > 0 else f"{iv}"
            else:
                used = st.number_input(f"使用量 ({item['unit']})", key=f"ind_{i}", min_value=0.0, max_value=float(item['vol']), step=0.1)
                used_l = str(used)
            item_c = used * u_p
            total_material_cost += item_c
            line_details += f"・{item['name']}: {used_l}{item['unit']} ({item_c:,.2f}円)\n"

    final_cost = total_material_cost / serving_count
    st.markdown(f"""<div class="price-card">💰 1人あたりの原価<br><span style="font-size: 2rem; font-weight: 900; color: #ef4444;">{final_cost:,.2f} 円</span><br>(総額 {total_material_cost:,.0f}円 ÷ {serving_count}人分)</div>""", unsafe_allow_html=True)

    st.write(" ")
    summary = f"【文化祭原価計算結果】\nモード: {mode}\n"
    if mode == "まとめてモード": summary += f"予定数: {serving_count}人分\n"
    summary += f"{line_details}\n💰1人あたり原価: {final_cost:,.2f}円"
    st.text_area("貼り付けテキスト", value=summary, height=200)

    if st.button("🚨 全データを消去"):
        st.session_state.ingredients = []
        save_trigger([])
        st.rerun()
