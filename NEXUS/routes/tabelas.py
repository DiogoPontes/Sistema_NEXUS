from datetime import datetime, date
from flask import render_template, flash, request, redirect, url_for, session  # IMPORTANTE
from NEXUS import app
from NEXUS.conexao import get_connection
import mysql.connector



@app.route('/tabela_mpce')
def tabela_mpce():
    cidades_nomes_ids = {
        'Rio de Janeiro': 1,
        'Espirito Santo': 2,
        'Minas Gerais': 3
    }

    if 'usuario' not in session or 'id_usuario' not in session:
        return redirect(url_for('login'))  # ou a rota da sua tela de login
    
    usuario = session['usuario']
    id_usuario = session['id_usuario']
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
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

    if tipo_usuario in tipo_to_cidade:
        cidades = [tipo_to_cidade[tipo_usuario]]
    else:
        cidades = request.args.getlist('cidades') or list(cidades_nomes_ids.keys())

    cidades_ids = [cidades_nomes_ids[nome] for nome in cidades if nome in cidades_nomes_ids]
    
    meses = request.args.getlist('meses')  # ex: ['08', '09']
    # Se nenhum mês foi selecionado, define o mês atual como padrão
    if not meses:
        meses = [datetime.now().strftime('%m')]

    filtros_data = ""
    valores_data = []

    if meses:
        filtros_data = "AND EXISTS (SELECT 1 FROM mpce_data d WHERE d.mpce_id = m.id AND ("
        condicoes = []
        for mes in meses:
            condicoes.append("MONTH(d.data) = %s")
            valores_data.append(int(mes))
        filtros_data += " OR ".join(condicoes) + "))"

    sql = f"""
       SELECT 
        CONCAT(m.id,' - REDE ',r.nome) AS nome_rede, 
        (SELECT GROUP_CONCAT(DATE_FORMAT(d.data, '%d/%m/%Y') ORDER BY id SEPARATOR '; ') FROM mpce_data d WHERE d.mpce_id = m.id) AS datas,
        (SELECT MIN(d.data) FROM mpce_data d WHERE d.mpce_id = m.id) AS menor_data,

        (SELECT GROUP_CONCAT('- ',ace.descricao ORDER BY ace.cd_acao SEPARATOR ';') FROM mpce_acao ac 
         LEFT JOIN acao_comunicacao_estrategica ace ON ace.cd_acao = ac.acao_cd WHERE ac.mpce_id = m.id) AS acoes,
        (SELECT GROUP_CONCAT('- ',l.nm_linha ORDER BY l.cd_linha SEPARATOR ';') FROM mpce_linha_esforco le 
         LEFT JOIN linha_esforco l ON l.cd_linha = le.linha_cd WHERE le.mpce_id = m.id) AS linhas,
        (SELECT GROUP_CONCAT(l.cod_ocecml ORDER BY l.cd_linha SEPARATOR ';') FROM mpce_linha_esforco le 
         LEFT JOIN linha_esforco l ON l.cd_linha = le.linha_cd WHERE le.mpce_id = m.id) AS ocecml,
        (SELECT GROUP_CONCAT('- ',p.nm_publico ORDER BY p.cd_publico SEPARATOR ';') FROM mpce_publico_alvo pa 
         LEFT JOIN publico_alvo p ON p.cd_publico = pa.publico_alvo_cd WHERE pa.mpce_id = m.id) AS publicos,
        (SELECT GROUP_CONCAT('- ',pa2.publico_segmentado ORDER BY pa2.publico_alvo_cd SEPARATOR ';') 
         FROM mpce_publico_alvo pa2 
         LEFT JOIN publico_alvo p2 ON p2.cd_publico = pa2.publico_alvo_cd WHERE pa2.mpce_id = m.id) AS publicos_segmentado,
        m.*, o.nome AS nome_orgao, c.nm_cidade AS nome_cidade
        FROM mpce m
        LEFT JOIN orgao o ON o.codigo = m.orgao_codigo
        LEFT JOIN cidade c ON c.cd_cidade = m.rede_id
        LEFT JOIN rede r ON r.id = m.rede_id
       WHERE m.arquivado = 0 AND m.rede_id IN ({','.join(['%s'] * len(cidades_ids))})
        {filtros_data}
        ORDER BY menor_data
    """

    cursor.execute(sql, cidades_ids + valores_data)
    mece_lista = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'form_mece.html',
        mece_lista=mece_lista,
        cidades_selecionadas=cidades,
        meses_selecionados=meses,
        tipo_usuario=tipo_usuario,
        datetime=datetime
    )


@app.route('/excluir_evento/<int:id>', methods=['GET'])
def excluir_evento(id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        
        #cursor.execute("DELETE FROM resultado WHERE mpce_id = %s", (id,))
        #cursor.execute("DELETE FROM produto WHERE mpce_id = %s", (id,))
        #cursor.execute("DELETE FROM mpce_data WHERE mpce_id = %s", (id,))
        #cursor.execute("DELETE FROM mpce_linha_esforco WHERE mpce_id = %s", (id,))
        #cursor.execute("DELETE FROM mpce_publico_alvo WHERE mpce_id = %s", (id,))
        #cursor.execute("DELETE FROM mpce WHERE id = %s", (id,))
        
        cursor.execute("UPDATE mpce SET arquivado = 1  WHERE id = %s", (id,))

        
        conn.commit()
        flash("Evento excluído com sucesso!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Erro ao excluir evento: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('tabela_mpce'))

@app.route('/excluir_fidece/<int:id>', methods=['GET'])
def excluir_fidece(id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        
        cursor.execute("SELECT id FROM resultado WHERE mpce_id = %s", (id,))
        resultados = cursor.fetchall()
        
        for resultado in resultados: 
            cursor.execute("DELETE FROM avaliacao WHERE resultado_id = %s", (resultado[0],))
        
        cursor.execute("""
            DELETE FROM feedback
            WHERE fidece_id IN (SELECT id FROM fidece WHERE mpce_id = %s)
        """, (id,))

        cursor.execute("DELETE FROM fidece WHERE mpce_id = %s", (id,))
        
        cursor.execute("UPDATE mpce SET status = 0  WHERE id = %s", (id,))

        
        conn.commit()
        flash("Fidece excluída com sucesso!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Erro ao excluir fidece: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('form_resultado_fidece'))


@app.route('/form_resultado_fidece')
def form_resultado_fidece():
    
    usuario = session.get('usuario')
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT tipo_usuario FROM usuario WHERE nome = %s", (usuario,))
    resultado = cursor.fetchone()
    tipo_usuario = resultado['tipo_usuario'] if resultado else None
    
    
    cidades_nomes_ids = {
        'Rio de Janeiro': 1,
        'Espirito Santo': 2,
        'Minas Gerais': 3
    }

    # Consulta tipo de usuário
    usuario = session.get('usuario')
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
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
    
    if tipo_usuario in tipo_to_cidade:
        cidades = [tipo_to_cidade[tipo_usuario]]
    else:
        cidades = request.args.getlist('cidades') or list(cidades_nomes_ids.keys())

    cidades_ids = [cidades_nomes_ids[nome] for nome in cidades if nome in cidades_nomes_ids]
    
    meses = request.args.getlist('meses')  # ex: ['08', '09']
    # Se nenhum mês foi selecionado, define o mês atual como padrão
    if not meses:
        meses = [datetime.now().strftime('%m')]

    filtros_data = ""
    valores_data = []

    if meses:
        filtros_data = "AND EXISTS (SELECT 1 FROM mpce_data d WHERE d.mpce_id = m.id AND ("
        condicoes = []
        for mes in meses:
            condicoes.append("MONTH(d.data) = %s")
            valores_data.append(int(mes))
        filtros_data += " OR ".join(condicoes) + "))"

    sql = f"""
        SELECT distinct
            CONCAT(m.id,' - REDE ',r.nome) AS nome_rede,
            (SELECT GROUP_CONCAT(DATE_FORMAT(d.data, '%d/%m/%Y') ORDER BY id SEPARATOR '; ') FROM mpce_data d WHERE d.mpce_id = m.id) AS datas,
            (SELECT GROUP_CONCAT('- ',ace.descricao ORDER BY ace.cd_acao SEPARATOR ';') 
             FROM mpce_acao ac 
             LEFT JOIN acao_comunicacao_estrategica ace ON ace.cd_acao = ac.acao_cd
             WHERE ac.mpce_id = m.id) AS acoes,
            (SELECT GROUP_CONCAT('- ',l.nm_linha ORDER BY l.cd_linha SEPARATOR ';') 
             FROM mpce_linha_esforco le 
             LEFT JOIN linha_esforco l ON l.cd_linha = le.linha_cd
             WHERE le.mpce_id = m.id) AS linhas,
            (SELECT GROUP_CONCAT(l.cod_ocecml ORDER BY l.cd_linha SEPARATOR ';') 
             FROM mpce_linha_esforco le 
             LEFT JOIN linha_esforco l ON l.cd_linha = le.linha_cd
             WHERE le.mpce_id = m.id) AS ocecml,
            (SELECT GROUP_CONCAT('- ',p.nm_publico ORDER BY p.cd_publico SEPARATOR ';') 
             FROM mpce_publico_alvo pa 
             LEFT JOIN publico_alvo p ON p.cd_publico = pa.publico_alvo_cd
             WHERE pa.mpce_id = m.id) AS publicos,
             (SELECT MIN(d.data) FROM mpce_data d WHERE d.mpce_id = m.id) AS menor_data,
            m.vetor_descricao,
            m.status,
            m.acao_descricao,
            f.*,
            COALESCE(fe.consideracoes_cce, '') as consideracoes_cce,
             CONCAT(pg.sg_postograd,' ',f.nome) AS militar
          FROM fidece f
          LEFT JOIN mpce m ON m.id = f.mpce_id
          LEFT JOIN rede r ON r.id = m.rede_id
          LEFT JOIN feedback fe ON fe.fidece_id = f.id
          LEFT JOIN postograd pg ON (pg.cd_postograd = f.posto_grad_cd)
         WHERE f.arquivado = 0 AND m.rede_id IN ({','.join(['%s'] * len(cidades_ids))})
        {filtros_data}
        ORDER BY menor_data 
    """

    cursor.execute(sql, cidades_ids + valores_data)
    fidece_lista = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template(
        'form_fidece.html',
        fidece_lista=fidece_lista,
        cidades_selecionadas=cidades,
        meses_selecionados=meses,
        tipo_usuario=tipo_usuario,
        usuario=usuario  # <- ESSENCIAL
    )

   
   

@app.route('/form_resultado_feedback')
def form_resultado_feedback():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
                                SELECT me.cd_mece, m.numero_evento, 
	  me.`data` AS data_mece, m.data_evento AS data_fidece,
        o2.nome AS om_mece, o.nome AS om_fidece,
        CONCAT(p2.sg_postograd, ' ', me.nome) AS nome_mece,
        CONCAT(p.sg_postograd, ' ', m.nome) AS nome_fidece,
        CONCAT(ep2.evento,' - Dia: ',me.`data`,' - ',c2.nm_cidade) AS evento_mece,
        CONCAT(ep.evento,' - Dia: ',m.data_evento,' - ',c.nm_cidade) AS evento_fidece,
        l.nm_linha AS linha_mece,
        l1.nm_linha AS linha_fidece,
        l2.nm_linha AS linha2_fidece,
        pa.nm_publico AS publico_mece,
        pa1.nm_publico AS publico_fidece,
        pa2.nm_publico AS publico2_fidece,
        me.lista_tarefas1 AS comsoc_mece,
        m.tarefas AS comsoc_fidece,
         me.lista_r1 AS ri_mece,
         m.ri AS ri_fidece,
         fb.consideracoes_cce,
         fb.manifestacao_om  
	          FROM fidece m
          LEFT JOIN mece me ON (me.cd_mece = m.numero_evento)
         LEFT JOIN orgao o ON o.codigo = m.cdorgao
         LEFT JOIN orgao o2 ON o2.codigo = me.orgao
         LEFT JOIN postograd p ON p.cd_postograd = m.postograd
         LEFT JOIN postograd p2 ON p2.cd_postograd = me.posotgrad
         LEFT JOIN cidade c ON c.cd_cidade = m.municipio
         LEFT JOIN cidade c2 ON c2.cd_cidade = me.cidade
         LEFT JOIN evento_principal ep ON ep.cd_evento = m.situacao_evento
         LEFT JOIN evento_principal ep2 ON ep2.cd_evento = me.evento
         LEFT JOIN linha_esforco l ON l.cd_linha = me.linha_esforco
         LEFT JOIN linha_esforco l1 ON l1.cd_linha = m.linha_esforco
         LEFT JOIN linha_esforco l2 ON l2.cd_linha = m.linha_esforco2
         LEFT JOIN publico_alvo pa ON pa.cd_publico = me.publico
         LEFT JOIN publico_alvo pa1 ON pa1.cd_publico = m.publico
         LEFT JOIN publico_alvo pa2 ON pa2.cd_publico = m.publico2
         LEFT JOIN feedback fb ON (fb.cd_mece = me.cd_mece)
   
         ORDER BY m.id
    """)
    fidece_lista = cursor.fetchall()
    cursor.close()
    conn.close()

    if not fidece_lista:
        return "Registro não encontrado.", 404

    return render_template('form_resultado_feedback.html', fidece_lista=fidece_lista)

@app.route('/editar_mpce/<int:id>', methods=['GET', 'POST'])
def editar_mpce(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if 'usuario' not in session or 'id_usuario' not in session:
        return redirect(url_for('login'))  # ou a rota da sua tela de login

    id_usuario = session['id_usuario']
    
    cursor.execute("SELECT codigo, nome FROM orgao ORDER BY nome")
    orgaos = cursor.fetchall()

    # Carregar todas as linhas e públicos
    cursor.execute("SELECT cd_linha, nm_linha FROM linha_esforco ORDER BY nm_linha")
    linhas_esforco = cursor.fetchall()

    cursor.execute("SELECT cd_publico, nm_publico FROM publico_alvo ORDER BY nm_publico")
    publicos_alvo = cursor.fetchall()

    # Carregar selecionados do MPCE
    cursor.execute("SELECT linha_cd FROM mpce_linha_esforco WHERE mpce_id = %s", (id,))
    linhas_selecionadas = [row['linha_cd'] for row in cursor.fetchall()]

    cursor.execute("SELECT publico_alvo_cd FROM mpce_publico_alvo WHERE mpce_id = %s", (id,))
    publicos_selecionados = [row['publico_alvo_cd'] for row in cursor.fetchall()]

    cursor.execute("""
        SELECT id,
               DATE_FORMAT(data, '%Y-%m-%d')   AS data,
               DATE_FORMAT(data_fim, '%Y-%m-%d') AS data_fim
          FROM mpce_data
         WHERE mpce_id = %s
      ORDER BY id
         LIMIT 1
    """, (id,))
    mpce_data = cursor.fetchone()
    

    cursor.execute("SELECT id, data, data_fim FROM mpce_data WHERE mpce_id = %s", (id,))
    datas = cursor.fetchall()
    if not datas:
        datas = [{'id': '', 'data': '', 'data_fim': ''}]


    if request.method == 'POST':
        # Atualiza campos do MPCE
        vetor = request.form.get('vetor_descricao')
        temas = request.form.get('temas_explorar')
        ideias = request.form.get('ideias_forca')
        acao_descricao = request.form.get('acao_descricao')
        orgao = request.form.get('orgao')
        
        data_evento = request.form.get('data_evento') or None
        data_fim    = request.form.get('data_fim') or None
        mpce_data_id = request.form.get('mpce_data_id')  # hidden

        
        linhas_esforco = request.form.getlist('linhas_esforco')
        publicos_alvo = request.form.getlist('publicos_alvo')
        
        # Limpar as relações anteriores
        cursor.execute("DELETE FROM mpce_linha_esforco WHERE mpce_id = %s", (id,))
        cursor.execute("DELETE FROM mpce_publico_alvo WHERE mpce_id = %s", (id,))

        # Inserir novas linhas
        for linha_id in linhas_esforco:
            cursor.execute("INSERT INTO mpce_linha_esforco (mpce_id, linha_cd) VALUES (%s, %s)", (id, linha_id))

        # Inserir novos públicos
        for publico_id in publicos_alvo:
            cursor.execute("INSERT INTO mpce_publico_alvo (mpce_id, publico_alvo_cd) VALUES (%s, %s)", (id, publico_id))


        status = 1 if request.form.get('status') == 'on' else 0

        cursor.execute("UPDATE mpce SET orgao_codigo = %s, acao_descricao = %s, vetor_descricao = %s, temas_explorar = %s, ideias_forca = %s, id_usuario = %s WHERE id = %s", (orgao, acao_descricao, vetor, temas, ideias, id_usuario, id))

        total = int(request.form.get('total_resultados', 0))
        
        cursor.execute("SELECT id FROM resultado WHERE mpce_id = %s", (id,))
        resultados = [row['id'] for row in cursor.fetchall()]
        
        for resultado in resultados:
              cursor.execute("DELETE from avaliacao WHERE resultado_id = %s", (resultado,))    
        
        cursor.execute("DELETE from resultado WHERE mpce_id = %s", (id,))

        for i in range(total):
            resultado_id = request.form.get(f'resultado_id_{i}')
            descricao = request.form.get(f'descricao_resultado_{i}')
            if descricao is not None:
                cursor.execute("INSERT INTO resultado (mpce_id, descricao) VALUES (%s, %s)", (id, descricao))
                
        total2 = int(request.form.get('total_produtos', 0))
        
        cursor.execute("DELETE from produto WHERE mpce_id = %s", (id,))

        for i in range(total2):
            produto_id = request.form.get(f'produto_id_{i}')
            descricao = request.form.get(f'descricao_produto_{i}')
            link = request.form.get(f'link_produto_{i}')
            if produto_id is not None:
                cursor.execute("INSERT INTO produto (mpce_id, descricao, link) VALUES (%s, %s, %s)", (id, descricao, link))

        # Upsert em mpce_data
        if mpce_data_id:
            cursor.execute("""
                UPDATE mpce_data
                   SET data = %s, data_fim = %s
                 WHERE id = %s
            """, (data_evento, data_fim, mpce_data_id))
        else:
            # Se ainda não havia linha e ao menos uma das datas foi informada
            if data_evento or data_fim:
                cursor.execute("""
                    INSERT INTO mpce_data (mpce_id, data, data_fim)
                    VALUES (%s, %s, %s)
                """, (id, data_evento, data_fim))

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('tabela_mpce'))

    # GET request: busca os dados
    cursor.execute("SELECT * FROM mpce WHERE id = %s", (id,))
    mpce = cursor.fetchone()

    cursor.execute("SELECT * FROM resultado WHERE mpce_id = %s", (id,))
    resultados = cursor.fetchall()
    
    cursor.execute("SELECT id, mpce_id, COALESCE(descricao, '') as descricao, COALESCE(link, '') as link   FROM produto WHERE mpce_id = %s", (id,))
    produtos = cursor.fetchall()

    # Garante que pelo menos um campo de resultado esteja presente
    if not resultados:
        resultados = [{'id': '', 'descricao': ''}]
        
    if not produtos:
        produtos = [{'id': '', 'descricao': '', 'link': ''}]

    cursor.close()
    conn.close()

    return render_template('form_editar_mpce.html', mpce=mpce, resultados=resultados, produtos=produtos, linhas_esforco=linhas_esforco,
    linhas_selecionadas=linhas_selecionadas,
    publicos_alvo=publicos_alvo,
    publicos_selecionados=publicos_selecionados,
    orgaos=orgaos, 
    mpce_data=mpce_data)

@app.route('/editar_fidece/<int:id>', methods=['GET', 'POST'])
def editar_fidece(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if 'usuario' not in session or 'id_usuario' not in session:
        return redirect(url_for('login'))  # ou a rota da sua tela de login

    id_usuario = session['id_usuario']
    
    
    if request.method == 'POST':
        # Atualiza campos do MPCE
        vetor = request.form.get('vetor_descricao')
        acao_descricao = request.form.get('acao_descricao')
        
        #cursor.execute("UPDATE mpce SET acao_descricao = %s, vetor_descricao = %s WHERE id = %s", (acao_descricao, vetor, id))

        #total = int(request.form.get('total_resultados', 0))
        
        #cursor.execute("SELECT id FROM resultado WHERE mpce_id = %s", (id,))
        #resultados = [row['id'] for row in cursor.fetchall()]
        
        #for resultado in resultados:
        #      cursor.execute("DELETE from avaliacao WHERE resultado_id = %s", (resultado,))    
        
        #cursor.execute("DELETE from resultado WHERE mpce_id = %s", (id,))

        #for i in range(total):
        #    resultado_id = request.form.get(f'resultado_id_{i}')
        #    descricao = request.form.get(f'descricao_resultado_{i}')
        #    if descricao is not None:
        #        cursor.execute("INSERT INTO resultado (mpce_id, descricao) VALUES (%s, %s)", (id, descricao))
                
        total2 = int(request.form.get('total_produtos', 0))
        
        cursor.execute("DELETE from produto WHERE mpce_id = %s", (id,))

        for i in range(total2):
            produto_id = request.form.get(f'produto_id_{i}')
            descricao = request.form.get(f'descricao_produto_{i}')
            link = request.form.get(f'link_produto_{i}')
            if produto_id is not None:
                cursor.execute("INSERT INTO produto (mpce_id, descricao, link) VALUES (%s, %s, %s)", (id, descricao, link))

        cursor.execute("INSERT INTO log_audit SET log_audit.id_tabela = 2, log_audit.id_usuario = %s, log_audit.data = CURRENT_TIMESTAMP(), "
		"log_audit.operacao = 'UPDATE', log_audit.id_registro = %s", (id_usuario, id))

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('form_resultado_fidece'))

    # GET request: busca os dados
    cursor.execute("SELECT * FROM mpce WHERE id = %s", (id,))
    mpce = cursor.fetchone()

    cursor.execute("SELECT * FROM resultado WHERE mpce_id = %s", (id,))
    resultados = cursor.fetchall()
    
    cursor.execute("SELECT id, mpce_id, COALESCE(descricao, '') as descricao, COALESCE(link, '') as link   FROM produto WHERE mpce_id = %s", (id,))
    produtos = cursor.fetchall()

    # Garante que pelo menos um campo de resultado esteja presente
    if not resultados:
        resultados = [{'id': '', 'descricao': ''}]
        
    if not produtos:
        produtos = [{'id': '', 'descricao': '', 'link': ''}]

    cursor.close()
    conn.close()

    return render_template('form_editar_fidece.html', mpce=mpce, resultados=resultados, produtos=produtos)



def get_resultados_por_mpce(mpce_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT descricao FROM resultado
        WHERE mpce_id = %s
    """, (mpce_id,))
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados