from datetime import datetime
from flask import render_template, request, redirect, url_for, session
from NEXUS import app
from NEXUS.conexao import get_connection
import mysql.connector

@app.route('/metrica_numero_eventos', methods=['GET', 'POST'])
def metrica_numero_eventos():
    # --- Mapas de REDE (cidades) iguais aos da tabela MPCE ---
    cidades_nomes_ids = {
        'Rio de Janeiro': 1,
        'Espirito Santo': 2,
        'Minas Gerais': 3
    }

    if 'usuario' not in session or 'id_usuario' not in session:
        return redirect(url_for('login'))

    usuario = session['usuario']
    id_usuario = session['id_usuario']

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Descobre o tipo do usuário
    cursor.execute("SELECT tipo_usuario FROM usuario WHERE nome = %s", (usuario,))
    resultado = cursor.fetchone()
    tipo_usuario = resultado['tipo_usuario'] if resultado else None

    tipo_to_cidade = {
        1: 'Rio de Janeiro',
        11: 'Rio de Janeiro',
        2: 'Espirito Santo',
        12: 'Espirito Santo',
        3: 'Minas Gerais',
        13: 'Minas Gerais',
    }

    # Filtro de REDE (cidades) – fixa pela permissão do usuário, senão usa checkboxes/URL
    cidades = request.args.getlist('cidades') or list(cidades_nomes_ids.keys())

    cidades_ids = [cidades_nomes_ids[nome] for nome in cidades if nome in cidades_nomes_ids]

    # Filtro de MÊS – se não vier nada, usa o mês atual
    meses = request.args.getlist('meses')  # ex.: ['08','09']
    if not meses:
        meses = [datetime.now().strftime('%m')]

    # Monta o EXISTS por mês (usa mpce_data)
    filtros_data_sql = ""
    params_data = []
    if meses:
        filtros_data_sql = "AND EXISTS (SELECT 1 FROM mpce_data d WHERE d.mpce_id = m.id AND ("
        conds = []
        for mes in meses:
            conds.append("MONTH(d.data) = %s")
            params_data.append(int(mes))
        filtros_data_sql += " OR ".join(conds) + "))"

    # ---------------------- CONSULTAS ----------------------
    # 1) Contagem por REDE (rótulos do gráfico de pizza/barras superiores)
    labels, dados = [], []

    sql_rede = f"""
        SELECT r.nome, COUNT(*) AS total
          FROM mpce m
          LEFT JOIN rede r   ON r.id = m.rede_id
         WHERE m.arquivado = 0
           AND m.rede_id IN ({','.join(['%s'] * len(cidades_ids))})
           {filtros_data_sql}
         GROUP BY r.id
         ORDER BY total DESC
    """
    cursor.execute(sql_rede, cidades_ids + params_data)
    for row in cursor.fetchall():
        labels.append(row['nome'])
        dados.append(row['total'] or 0)

    # 2) Quantidade por Linha de Esforço (barra horizontal)
    categorias, mece = [], []

    sql_linha = f"""
        SELECT l.nm_linha AS nome,
               COUNT(DISTINCT m.id) AS mece
          FROM linha_esforco l
          LEFT JOIN mpce_linha_esforco ml ON ml.linha_cd = l.cd_linha
          LEFT JOIN mpce m               ON m.id = ml.mpce_id
         WHERE (m.id IS NOT NULL)
           AND m.arquivado = 0
           AND m.rede_id IN ({','.join(['%s'] * len(cidades_ids))})
           {filtros_data_sql}
         GROUP BY l.cd_linha
         ORDER BY l.nm_linha
    """
    cursor.execute(sql_linha, cidades_ids + params_data)
    for row in cursor.fetchall():
        categorias.append(row['nome'])
        mece.append(row['mece'] or 0)

    x_max = max(max(mece) if mece else 1, 1) * 1.5

    # 3) Quantidade por Público-Alvo (barra horizontal)
    publico, pub_mece = [], []

    sql_publico = f"""
        SELECT p.nm_publico AS nome,
               COUNT(DISTINCT m.id) AS mece
          FROM publico_alvo p
          LEFT JOIN mpce_publico_alvo pa ON pa.publico_alvo_cd = p.cd_publico
          LEFT JOIN mpce m               ON m.id = pa.mpce_id
         WHERE (m.id IS NOT NULL)
           AND m.arquivado = 0
           AND m.rede_id IN ({','.join(['%s'] * len(cidades_ids))})
           {filtros_data_sql}
         GROUP BY p.cd_publico
         ORDER BY p.nm_publico
    """
    cursor.execute(sql_publico, cidades_ids + params_data)
    for row in cursor.fetchall():
        publico.append(row['nome'])
        pub_mece.append(row['mece'] or 0)

    pub_x_max = max(max(pub_mece) if pub_mece else 1, 1) * 1.5

    cursor.close()
    conn.close()

    # Render com os filtros selecionados (para marcar os checkboxes)
    return render_template(
        'metrica_numero_eventos.html',
        labels=labels, dados=dados,
        categorias=categorias, mece=mece, x_max=x_max,
        publico=publico, pub_mece=pub_mece, pub_x_max=pub_x_max,
        cidades_selecionadas=cidades,
        meses_selecionados=meses,
        tipo_usuario=tipo_usuario,
        datetime=datetime
    )
