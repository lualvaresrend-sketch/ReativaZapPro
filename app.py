import os, time, json
from flask import Flask, render_template_string, request, redirect
app = Flask(__name__)

DATA = {
    "vendas": [],
    "regras": [
        {"min": 0.0, "max": 100.0, "desconto": 5.0},
        {"min": 100.01, "max": 500.0, "desconto": 12.0},
        {"min": 500.01, "max": 99999.0, "desconto": 20.0}
    ],
    "loja": {"nome": "Loja Premium", "cnpj": "00.000.000/0001-00", "pix": "CHAVE PIX"}
}
SG = "1965"

H = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Reativa Zap Pro</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; font-family:sans-serif; }
        body { background:#09090A; color:#E1E1E6; display:flex; justify-content:center; padding:20px; }
        .box { background:#121214; width:100%; max-width:440px; border-radius:10px; border:1px solid #29292E; padding:20px; text-align:center; }
        .logo { font-size:24px; font-weight:bold; color:#00B37E; }
        .sel { display:flex; gap:10px; margin:15px 0; background:#202024; padding:4px; border-radius:6px; }
        .bm { flex:1; background:transparent; border:none; color:#8D8D99; padding:6px; font-weight:bold; cursor:pointer; font-size:12px; }
        .bm.active { background:#00B37E; color:#FFF; border-radius:4px; }
        .gr-in { margin-bottom:10px; text-align:left; }
        label { display:block; font-size:11px; margin-bottom:4px; }
        input { width:100%; background:#202024; border:1px solid #323238; border-radius:6px; padding:8px; color:#FFF; font-size:14px; outline:none; }
        .btn { background:#00B37E; color:#FFF; width:100%; border:none; padding:10px; font-weight:bold; border-radius:6px; cursor:pointer; text-transform:uppercase; margin-top:5px; }
        .s-box { background:#202024; border:1px solid #323238; padding:10px; border-radius:6px; margin-bottom:10px; font-size:12px; }
        .lista { margin-top:15px; text-align:left; }
        .lt { font-size:12px; font-weight:bold; margin-bottom:8px; border-left:3px solid #00B37E; padding-left:6px; display:flex; justify-content:space-between; }
        .busca { width:150px; padding:4px; font-size:11px; background:#202024; border:1px solid #323238; color:#FFF; border-radius:4px; }
        .item { background:#202024; border:1px solid #323238; border-radius:6px; padding:10px; margin-bottom:6px; font-size:12px; }
        .bt-v { display:flex; gap:6px; margin-top:6px; }
        .mi { background:#29292E; border:1px solid #323238; color:#FFF; padding:3px 6px; font-size:11px; border-radius:4px; text-decoration:none; font-weight:bold; cursor:pointer; }
    </style>
</head>
<body>
    <div class="box">
        <div class="logo">Reativa Zap Pro 🚀</div>
        <div class="sel">
            <button class="bm active" id="bf" onclick="m('func')">⚡ Vendedor</button>
            <button class="bm" id="bg" onclick="m('ger')">👔 Gerente</button>
        </div>
        <div id="box-gerente" style="display:none; margin-bottom:15px; background:#16161A; padding:10px; border-radius:6px; border:1px solid #323238; text-align:left;">
            <form action="/salvar-regras" method="POST">
                {% for r in regras %}
                <div style="margin-bottom:6px; font-size:12px;">
                    <span>Até R$ {{ "%.0f"|format(r.max) }}:</span>
                    <input type="number" name="desc_{{ loop.index0 }}" value="{{ r.desconto }}" style="width:50px; padding:2px;" required>% Máx
                </div>
                {% endfor %}
                <button type="submit" class="btn" style="padding:4px; font-size:11px;">Salvar Regras</button>
            </form>
        </div>
        <form action="/salvar-venda" method="POST">
            <div class="gr-in"><label>Nome:</label><input type="text" name="nome" id="inome" required></div>
            <div class="gr-in"><label>CPF (Opcional):</label><input type="text" name="cpf"></div>
            <div class="gr-in"><label>Valor Bruto (R$):</label><input type="number" step="0.01" name="valor" id="ivalor" oninput="cTrava()" required></div>
            <div class="s-box">
                <div style="display:flex; justify-content:space-between;"><span>Desconto: <b id="t-desc">0%</b></span><span>Limite: <b id="t-lim">5%</b></span></div>
                <input type="range" name="desconto_aplicado" id="islider" min="0" max="5" value="0" oninput="atVal()" style="width:100%;">
                <div style="display:flex; justify-content:space-between; margin-top:6px; font-weight:bold;"><span>Final: <span id="t-fin" style="color:#00B37E;">R$ 0.00</span></span></div>
            </div>
            <button type="submit" class="btn">🟢 Confirmar Venda</button>
        </form>
        <div class="lista">
            <div class="lt"><span>📋 Caixa</span><input type="text" id="ibusca" class="busca" placeholder="🔍 Buscar..." oninput="fLista()"></div>
            <div id="l-vendas">
                {% if vendas %}{% for v in vendas[::-1] %}
                <div class="item-venda item" data-nome="{{ v.nome.lower() }}" data-valor="{{ "%.2f"|format(v.final) }}">
                    <div style="display:flex; justify-content:space-between;"><strong>{{ v.nome }}</strong><span style="color:#00B37E;">R$ {{ "%.2f"|format(v.final) }}</span></div>
                    <p style="color:#8D8D99; font-size:11px;">Bruto: R$ {{ "%.2f"|format(v.bruto) }} | Desc: {{ v.desc_dado }}% | CPF: {{ v.cpf }}</p>
                    <div class="bt-v">
                        <span onclick="copiar('{{v.nome}}','{{"%.2f"|format(v.bruto)}}','{{v.desc_dado}}','{{"%.2f"|format(v.final)}}')" class="mi" style="border-color:#00B37E; color:#00B37E;">📋 Copiar</span>
                        <a href="/pdf/{{ v.id }}" target="_blank" class="mi" style="border-color:#FBA94C; color:#FBA94C;">📄 PDF</a>
                    </div>
                </div>
                {% endfor %}{% endif %}
            </div>
        </div>
    </div>
    <script>
        let mo = "func"; const regras = JSON.parse('{{ regras_json|safe }}');
        function cTrava() {
            let v = parseFloat(document.getElementById('ivalor').value) || 0; let lim = 5;
            for(let r of regras) { if(v >= r.min && v <= r.max) { lim = r.desconto; break; } }
            let s = document.getElementById('islider'); s.max = lim; if(parseInt(s.value) > lim) s.value = lim;
            document.getElementById('t-lim').innerText = lim + "%"; atVal();
        }
        function atVal() {
            let b = parseFloat(document.getElementById('ivalor').value) || 0; let d = parseInt(document.getElementById('islider').value) || 0;
            let f = b - (b * (d / 100)); document.getElementById('txt-desc').innerText = d + "%"; document.getElementById('t-fin').innerText = "R$ " + f.toFixed(2);
        }
        function m(x){
            if(x==="ger" && mo!=="ger"){
                if(prompt("Senha:") === "{{ senha_chave }}"){ mo="ger"; document.getElementById('bg').classList.add('active'); document.getElementById('bf').classList.remove('active'); document.getElementById('box-gerente').style.display='block'; }
            }else if(x==="func"){ mo="func"; document.getElementById('bf').classList.add('active'); document.getElementById('bg').classList.remove('active'); document.getElementById('box-gerente').style.display='none'; }
        }
        function fLista() {
            let b = document.getElementById('ibusca').value.toLowerCase(); let itens = document.getElementsByClassName('item-venda');
            for(let i of itens) { i.style.display = (i.getAttribute('data-nome').includes(b) || i.getAttribute('data-valor').includes(b)) ? "block" : "none"; }
        }
        function copiar(n,b,d,f) {
            let t = `Pedido: ${n}\\nOriginal: R$ ${b}\\nDesconto: ${d}%\\nTotal: R$ ${f}\\nPix: {{ pix_loja }}`;
            navigator.clipboard.writeText(t).then(() => alert("Copiado!"));
        }
    </script>
</body>
</html>"""
PDF_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Recibo #{{ ref }}</title>
    <style>
        body { background:#09090A; color:#E1E1E6; font-family:sans-serif; padding:20px; display:flex; justify-content:center; }
        .box { background:#121214; border:2px solid #00B37E; border-radius:8px; width:100%; max-width:400px; padding:20px; text-align:center; }
        .topo { border-bottom:2px dashed #29292E; padding-bottom:10px; margin-bottom:15px; }
        .linha { display:flex; justify-content:space-between; margin-bottom:6px; font-size:13px; }
    </style>
</head>
<body>
    <div class="box">
        <div class="topo"><strong>🏆 {{ loja_nome }}</strong><p style="font-size:10px; color:#8D8D99;">CNPJ: {{ loja_cnpj }}</p></div>
        <div class="linha"><span>Cliente:</span> <strong>{{ nome }}</strong></div>
        <div class="linha"><span>CPF:</span> <span>{{ cpf }}</span></div>
        <div class="linha"><span>Total Líquido:</span> <strong style="color:#00B37E; font-size:16px;">R$ {{ "%.2f"|format(final) }}</strong></div>
        <div style="margin-top:20px; background:#202024; padding:10px; border-radius:4px; font-size:11px; color:#FBA94C;">📲 PIX PRONTO: R$ {{ "%.2f"|format(final) }}</div>
    </div>
    <script>window.print();</script>
</body>
</html>"""

@app.route('/')
def home():
    regras_json = json.dumps(DATA["regras"])
    return render_template_string(H, vendas=DATA["vendas"], regras=DATA["regras"], regras_json=regras_json, senha_chave=SG, pix_loja=DATA["loja"]["pix"])

@app.route('/salvar-venda', methods=['POST'])
def salvar_venda():
    nome, cpf = request.form.get('nome', '').strip(), request.form.get('cpf', '').strip() or "N/I"
    try: bruto = float(request.form.get('valor', '0').replace(",", "."))
    except: bruto = 0.0
    try: desc = int(request.form.get('desconto_aplicado', '0'))
    except: desc = 0
    eco = bruto * (desc / 100)
    final = bruto - eco
    DATA["vendas"].append({"id": int(time.time()), "nome": nome, "cpf": cpf, "bruto": bruto, "desc_dado": desc, "eco": eco, "final": final, "ref": f"REC-{int(time.time())}"})
    return redirect('/')

@app.route('/salvar-regras', methods=['POST'])
def salvar_regras():
    for i in range(len(DATA["regras"])):
        try: DATA["regras"][i]["desconto"] = float(request.form.get(f"desc_{i}", "5"))
        except: pass
    return redirect('/')

@app.route('/pdf/<int:id_venda>')
def ver_pdf(id_venda):
    for v in DATA["vendas"]:
        if v["id"] == id_venda:
            return render_template_string(PDF_TEMPLATE, loja_nome=DATA["loja"]["nome"], loja_cnpj=DATA["loja"]["cnpj"], nome=v["nome"], cpf=v["cpf"], final=v["final"], ref=v["ref"])
    return "Não Encontrado", 404

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
