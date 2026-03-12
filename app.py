<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文化祭原価計算アプリ</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #f1f5f9; }
        .card { background: white; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); padding: 1.5rem; margin-bottom: 1.5rem; }
        label { display: block; font-size: 0.875rem; font-weight: 700; color: #475569; margin-bottom: 0.25rem; }
        input, select { width: 100%; border: 1px solid #cbd5e1; border-radius: 8px; padding: 0.5rem; margin-bottom: 1rem; }
        .btn-blue { background-color: #3b82f6; color: white; font-weight: 700; width: 100%; padding: 0.75rem; border-radius: 8px; transition: 0.2s; }
        .btn-blue:hover { background-color: #2563eb; }
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-2xl mx-auto">
        <h1 class="text-2xl font-black text-center text-blue-600 mb-6">🎡 文化祭原価計算</h1>

        <div class="card">
            <h2 class="text-lg font-bold border-l-4 border-blue-500 pl-2 mb-4">① 材料を登録</h2>
            <label>材料名</label>
            <input type="text" id="name" placeholder="例：鶏もも肉">
            
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label>内容量</label>
                    <input type="number" id="vol" value="100">
                </div>
                <div>
                    <label>単位</label>
                    <select id="unit">
                        <option>個</option><option>本</option><option>袋</option>
                        <option selected>g</option><option>kg</option><option>ml</option><option>l</option>
                    </select>
                </div>
            </div>

            <label>購入総額 (円)</label>
            <input type="number" id="price" value="500">
            
            <button onclick="addIngredient()" class="btn-blue">材料リストに追加</button>
        </div>

        <div id="listSection" class="card hidden">
            <h2 class="text-lg font-bold border-l-4 border-blue-500 pl-2 mb-4">② 登録済みの材料</h2>
            <div id="ingredientList" class="space-y-2"></div>
        </div>

        <div class="card">
            <h2 class="text-lg font-bold border-l-4 border-blue-500 pl-2 mb-4">③ 原価を計算</h2>
            <label>計算モード</label>
            <div class="flex gap-4 mb-4">
                <label class="flex items-center font-normal"><input type="radio" name="mode" value="per" checked class="w-4 h-4 mr-2" onclick="renderCalc()"> 1人ずつ</label>
                <label class="flex items-center font-normal"><input type="radio" name="mode" value="total" class="w-4 h-4 mr-2" onclick="renderCalc()"> まとめて</label>
            </div>

            <div id="calcArea"></div>

            <div id="resultCard" class="mt-6 p-6 bg-red-50 border-2 border-red-500 rounded-2xl text-center hidden">
                <span class="text-red-500 font-bold">1人あたりの原価</span><br>
                <span id="finalPrice" class="text-4xl font-black text-red-600">0.00</span> <span class="text-red-600 font-bold">円</span>
            </div>
        </div>

        <button onclick="resetAll()" class="text-sm text-gray-400 w-full hover:text-red-500 transition">🚨 全データを消去してリセット</button>
    </div>

    <script>
        let ingredients = JSON.parse(localStorage.getItem('bunkasai_data')) || [];

        function save() {
            localStorage.setItem('bunkasai_data', JSON.stringify(ingredients));
            renderList();
            renderCalc();
        }

        function addIngredient() {
            const name = document.getElementById('name').value;
            const vol = parseFloat(document.getElementById('vol').value);
            const price = parseInt(document.getElementById('price').value);
            const unit = document.getElementById('unit').value;

            if (!name) return alert("材料名を入力してください");
            ingredients.push({ name, vol, price, unit });
            save();
            document.getElementById('name').value = "";
        }

        function removeIngredient(index) {
            ingredients.splice(index, 1);
            save();
        }

        function renderList() {
            const list = document.getElementById('ingredientList');
            const section = document.getElementById('listSection');
            if (ingredients.length === 0) {
                section.classList.add('hidden');
                return;
            }
            section.classList.remove('hidden');
            list.innerHTML = ingredients.map((item, i) => `
                <div class="flex justify-between items-center bg-gray-50 p-2 rounded">
                    <span><b>${item.name}</b> (${item.vol}${item.unit} / ${item.price}円)</span>
                    <button onclick="removeIngredient(${i})" class="text-red-500 font-bold px-2">×</button>
                </div>
            `).join('');
        }

        function renderCalc() {
            const mode = document.querySelector('input[name="mode"]:checked').value;
            const area = document.getElementById('calcArea');
            const resultCard = document.getElementById('resultCard');

            if (ingredients.length === 0) {
                area.innerHTML = "<p class='text-gray-400'>材料を登録してください</p>";
                resultCard.classList.add('hidden');
                return;
            }
            resultCard.classList.remove('hidden');

            if (mode === 'total') {
                area.innerHTML = `
                    <label>合計何人分作りますか？</label>
                    <input type="number" id="servings" value="50" oninput="calculate()">
                `;
            } else {
                area.innerHTML = ingredients.map((item, i) => `
                    <div class="mb-4 p-3 border rounded">
                        <label class="text-blue-600">${item.name} の使用量</label>
                        ${['個', '本', '袋'].includes(item.unit) ? `
                            <div class="grid grid-cols-2 gap-2">
                                <select id="int_${i}" onchange="calculate()">
                                    ${Array.from({length: 101}, (_, n) => `<option value="${n}">${n}${item.unit}</option>`).join('')}
                                </select>
                                <select id="frac_${i}" onchange="calculate()">
                                    <option value="0">端数なし</option>
                                    <option value="0.25">1/4</option>
                                    <option value="0.33">1/3</option>
                                    <option value="0.5">1/2</option>
                                    <option value="0.66">2/3</option>
                                    <option value="0.75">3/4</option>
                                </select>
                            </div>
                        ` : `
                            <input type="number" id="use_${i}" value="0" step="0.1" oninput="calculate()">
                        `}
                    </div>
                `).join('');
            }
            calculate();
        }

        function calculate() {
            const mode = document.querySelector('input[name="mode"]:checked').value;
            let total = 0;
            let servings = 1;

            if (mode === 'total') {
                servings = parseFloat(document.getElementById('servings').value) || 1;
                ingredients.forEach(item => total += item.price);
            } else {
                ingredients.forEach((item, i) => {
                    const up = item.price / item.vol;
                    let used = 0;
                    if (['個', '本', '袋'].includes(item.unit)) {
                        used = parseFloat(document.getElementById(`int_${i}`).value) + parseFloat(document.getElementById(`frac_${i}`).value);
                    } else {
                        used = parseFloat(document.getElementById(`use_${i}`).value) || 0;
                    }
                    total += used * up;
                });
            }
            document.getElementById('finalPrice').innerText = (total / servings).toFixed(2);
        }

        function resetAll() {
            if (confirm("全てのデータを消去しますか？")) {
                ingredients = [];
                save();
            }
        }

        window.onload = () => { renderList(); renderCalc(); };
    </script>
</body>
</html>
