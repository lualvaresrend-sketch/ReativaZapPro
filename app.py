import os, time, urllib.parse
from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)

BM = {
    "vendas": [],
    "caixa_recuperado": 0.0,
    "caixa_pendente": 0.0,
    "msg": "Olá, [NOME]! Segue o fechamento da sua compra. Valor: R$ [VALOR]. Chave Pix: CNPJ DA LOJA AQUI."
}
SG = "1965"

H = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Reativa Zap Pro</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',sans-serif; }
        body { background:#09090A; color:#E1E1E6; display:flex; justify-content:center; align-items:center; min-height:100vh; padding:20px; }
        .container { background:#121214; width:100%; max-width:450px; border-radius:12px; border:1px solid #29292E; padding:25px; text-align:center; }
        .logo { font-size:28px; font-weight:800; color:#00B37E; margin-bottom:4px; }
        .sub { color:#8D8D99; font-size:12px; margin-bottom:20px; }
        .sel { display:flex; gap:10px; margin-bottom:20px; background:#202024; padding:4px; border-radius:8px; }
        .bm { flex:1; background:transparent; border:none; color:#8D8D99; padding:8px; font-weight:bold; cursor:pointer; font-size:12px; }
        .bm.active { background:#00B37E; color:#FFF; border-radius:6px; }
        .db { display:none; gap:10px; margin-bottom:20px; }
        .card { flex:1; background:#202024; border:1px solid #323238; border-radius:8px; padding:12px; text-align:left; }
        .ct { font-size:10px; color:#8D8D99; font-weight:bold; text-transform:uppercase; }
        .cv { font-size:16px; font-weight:800; }
        .gr { color: #00B37E; }
        .rd { color: #FF3333; }
        .gr-in { margin-bottom:12px; text-align:left; }
        label { display:block; font-size:11px; color:#E1E1E6; margin-bottom:6px; font-weight:600; }
        input,textarea { width:100%; background:#202024; border:1px solid #323238; border-radius:6px; padding:10px; color:#FFF; font-size:14px; outline:none; }
        input:focus,textarea:focus { border-color:#00B37E; }
        textarea { height:60px; resize:none; font-size:12px; color:#A8A8B3; }
        .btn { background:#00B37E; color:#FFF; width:100%; border:none; padding:12px; font-size:14px; font-weight:bold; border-radius:6px; cursor:pointer; text-transform:uppercase; }
        .lista { margin-top:20px; text-align:left; }
        .lt { font-size:12px; font-weight:bold; color:#FFF; margin-bottom:10px; border-left:3px solid #00B37E; padding-left:6px; }
        .item { background:#202024; border:1px solid #323238; border-radius:6px; padding:12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; }
        .item h2 { font-size:14px; color:#FFF; margin-bottom:2px; }
        .item p { font-size:11px; color:#8D8D99; }
        .st { font-size:10px; font-weight:bold; padding:2px 6px; border-radius:4px; }
        .pd { background:#291F12; color:#FBA94C; }
        .pg { background:#12291B; color:#00B37E; }
        .bt-v { display:flex; gap:6px; margin-top:6px; }
        .mi { background:#29292E; border:1px solid #323238; color:#FFF; padding:4px 8px; font-size:11px; border-radius:4px; text-decoration:none; font-weight:bold; }
        .mi.cb { border-color:#00B37E; color:#00B37E; }
        .mi.bx { border-color:#FF3333; color:#FF3333; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">Reativa Zap Pro 🚀</div>
        <div class="sub">Auditoria de Caixa e Recuperação</div>
        <div class="sel">
            <button class="bm active" id="bf" onclick="m('func')">👤 Funcionário</button>
            <button class="bm" id="bg" onclick="m('ger')">👔 Gerente</button>
        </div>
        <div class="db" id="pg">
            <div class="card"><div class="ct">💰 Recuperado</div><div class="cv gr">R$ {{ total_recuperado }}</div></div>
            <div class="card"><div class="ct">🚨 Na Rua</div><div class="cv rd">R$ {{ total_pendente }}</div></div>
        </div>
        <form action="/salvar" method="POST">
            <input type="hidden" name="criado_por" id="icp" value="Funcionário">
            <div class="gr-in"><label>Nome do Cliente:</label><input type="text" name="nome" required></div>
            <div class="gr-in"><label>WhatsApp (Com DDD):</label><input type="text" name="whatsapp" placeholder="Ex: 71991039981" required></div>
            <div class="gr-in"><label>Valor Devido (R$):</label><input type="text" name="valor" placeholder="Ex: 150.00" required></div>
            <div class="gr-in"><label>Texto Pix (Editável):</label><textarea name="texto" required>{{ texto_atual }}</textarea></div>
            <button type="submit" class="btn">🟢 Registrar Lançamento</button></form>
        <div class="lista">
            <div class="lt">📋 Fila de Cobranças Ativas</div>
            {% if vendas %}
                {% for v in vendas[::-1] %}
                <div class="item">
                    <div>
                        <h2>{{ v.nome }}</h2>
                        <p>R$ {{ "%.2f"|format(v.valor) }} | Por: {{ v.criado_por }}</p>
                        {% if v.status == 'Pendente' %}
                        <div class="bt-v">
                            <!-- 🔥 O REDIRECIONAMENTO CLASSICO DE VOLTA: Agora abrindo em nova guia, totalmente livre de bloqueios do Chrome! -->
                            <a href="https://whatsapp.com{{ v.whatsapp }}&text={{ v.link_zap }}" target="_blank" class="mi cb">💸 Cobrar</a>
                            <a href="/dar-baixa/{{ v.id }}" class="mi bx">🟩 Baixa</a>
                        </div>
                        {% endif %}
                    </div>
                    <span class="st {% if v.status == 'Pendente' %}pd{% else %}pg{% endif %}">{{ v.status }}</span>
                </div>
                {% endfor %}
            {% else %}
                <p style="font-size:12px;color:#8D8D99;text-align:center;">Fila zerada.</p>
            {% endif %}
        </div>
    </div>
    <script>
        let mo="func";
        function m(x){
            if(x==="ger"&&mo!=="ger"){
                let s=prompt("🔑 GESTOR: Senha:");
                if(s==="{{ senha_chave }}"){
                    mo="ger";
                    document.getElementById('bg').classList.add('active');
                    document.getElementById('bf').classList.remove('active');
                    document.getElementById('pg').style.display='flex';
                    document.getElementById('icp').value="Gerente";
                }else{alert("❌ Incorreta!");}
            }else if(x==="func"){
                mo="func";
                document.getElementById('bf').classList.add('active');
                document.getElementById('bg').classList.remove('active');
                document.getElementById('pg').style.display='none';
                document.getElementById('icp').value="Funcionário";
            }
        }
        if("{{ status_retorno }}" === "Gerente"){m("ger");}
    </script>
</body>
</html>"""

@app.route('/')
def home():
    return render_template_string(H, vendas=BM["vendas"], total_recuperado=f"{BM['caixa_recuperado']:.2f}", total_pendente=f"{BM['caixa_pendente']:.2f}", senha_chave=SG, status_retorno="Funcionário", texto_atual=BM["msg"])

@app.route('/salvar', methods=['POST'])
def salvar():
    nome = request.form.get('nome', '').strip()
    w_cru = request.form.get('whatsapp', '').strip()
    criado_por = request.form.get('criado_por', 'Funcionário')
    texto_mensagem = request.form.get('texto', '').strip()
    valor_cru = request.form.get('valor', '0')
    
    w = w_cru.replace("-", "").replace("(", "").replace(")", "").replace(" ", "").strip()
    if w.startswith("55"): w = w[2:]
    if len(w) == 10: w = w[:2] + "9" + w[2:]
    whatsapp = "55" + w
    
    v_limpo = valor_cru.replace("R$", "").replace("$", "").replace(" ", "").replace(",", ".").strip()
    try: valor = float(v_limpo)
    except: valor = 0.0
    
    BM["msg"] = texto_mensagem
    msg_final = texto_mensagem.replace("[NOME]", nome).replace("[VALOR]", f"{valor:.2f}")
    link_zap = urllib.parse.quote(msg_final)
    
    nova = {"id": int(time.time()), "nome": nome, "whatsapp": whatsapp, "valor": valor, "criado_por": criado_por, "status": "Pendente", "link_zap": link_zap}
    BM["vendas"].append(nova)
    BM["caixa_pendente"] += valor
    return redirect('/')

@app.route('/dar-baixa/<int:id_venda>')
def dar_baixa(id_venda):
    for v in BM["vendas"]:
        if v["id"] == id_venda and v["status"] == "Pendente":
            v["status"] = "Pago"
            BM["caixa_pendente"] -= v["valor"]
            BM["caixa_recuperado"] += v["valor"]
            break
    return redirect('/')

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
