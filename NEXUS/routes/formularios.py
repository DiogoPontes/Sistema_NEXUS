from datetime import datetime
from flask import render_template, request, redirect, url_for, session, jsonify  # IMPORTANTE
from NEXUS import app
from NEXUS.conexao import get_connection
import mysql.connector

def get_orgaos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM orgao ORDER BY nome")
    orgaos = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return orgaos

def get_postograd():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nm_postograd FROM postograd ORDER BY cd_postograd")
    postograds = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return postograds


def get_redes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM rede ORDER BY id")
    redes = cursor.fetchall()
    cursor.close()
    conn.close()
    return redes

def get_linhas_esforco():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT cd_linha, nm_linha FROM linha_esforco ORDER BY nm_linha")
    linhas = cursor.fetchall()
    cursor.close()
    conn.close()
    return linhas

def get_publicos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT cd_publico, nm_publico FROM publico_alvo ORDER BY nm_publico")
    publicos = cursor.fetchall()
    cursor.close()
    conn.close()
    return publicos

def get_resultados(mpce_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT r.id, r.descricao, a.tipo_avaliacao_cd FROM resultado r LEFT JOIN avaliacao a ON (a.resultado_id = r.id) WHERE r.mpce_id = %s", (mpce_id,))
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def get_produtos(mpce_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT p.id, p.descricao, p.link FROM produto p WHERE p.mpce_id = %s", (mpce_id,))
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def get_tipos_avaliacao():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT cd_avaliacao, nm_avaliacao FROM tipo_avaliacao")
    tipos = cursor.fetchall()
    conn.close()
    return tipos


@app.route('/menu')
def menu():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('menu.html')  # ou o nome real do seu HTML



@app.route('/', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT usuario.nome, tu.descricao, tu.cd_tipo, usuario.cd_usuario FROM usuario LEFT JOIN tipo_usuario tu ON (tu.cd_tipo = usuario.tipo_usuario) WHERE nome = %s AND senha = %s", (usuario, senha))
        user = cursor.fetchone()

        # Simulação da verificação de senha, ajuste se tiver campo `senha` real
        if user is not None:
            session['id_usuario'] = user[3]
            session['usuario'] = usuario
            session['perfil'] = user[1]
            session['tipo_usuario'] = user[2]
            return redirect(url_for('menu'))
        else:
            erro = "Usuário ou senha incorretos. Tente novamente."
            return render_template('login.html', erro=erro)
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))


@app.route('/home', methods=['GET', 'POST'])
def home():

    if 'usuario' not in session or 'id_usuario' not in session:
        return redirect(url_for('login'))  # ou a rota da sua tela de login
    
    usuario = session['usuario']
    id_usuario = session['id_usuario']

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT tipo_usuario FROM usuario WHERE nome = %s", (usuario,))
    resultado = cursor.fetchone()
    tipo_usuario = resultado['tipo_usuario'] if resultado else None

    # mapeamento opcional por tipo
    mapa_tipo_rede = {
        1: {"id": 1, "nome": "REDE RJ"},
        11: {"id": 1, "nome": "REDE RJ"},
        2: {"id": 2, "nome": "REDE ES"},
        12: {"id": 2, "nome": "REDE ES"},
        3: {"id": 3, "nome": "REDE MG"},
        13: {"id": 3, "nome": "REDE MG"}
    }

    rede_fixa = mapa_tipo_rede.get(tipo_usuario)
    redes = get_redes() if not rede_fixa else []

    orgaos = get_orgaos()
    postograds = get_postograd()
    
    redes = get_redes();
    linhas = get_linhas_esforco()
    publicos = get_publicos()
   
    linhas_selecionadas = request.args.getlist('linhas')
    publicos_selecionados = request.args.getlist('publicos')
    
    if request.method == 'POST':
           
        rede_id = request.form['rede']
        orgao_codigo = request.form['orgao']
        # posto = request.form['posto_grad']
        # nome = request.form['nome_relator']
        # telefone = request.form['telefone_relator']
        data = request.form['data_evento']
        acao_descricao = request.form['acoes']
        linhas = request.form.getlist('linhas')
        publicos = request.form.getlist('publicos')
        vetor_descricao = request.form['vetor_descricao']
        temas_explorar = request.form['temas_explorar']
        ideias_forca = request.form['ideias_forca']
        # produtos_descricao = request.form['produto_descricao']
        descricoes = request.form.getlist('descricao[]')
        produtos = request.form.getlist('produto[]')
        links = request.form.getlist('link[]')
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO mpce (
                    rede_id, orgao_codigo, acao_descricao, vetor_descricao, temas_explorar, ideias_forca, id_usuario
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                rede_id, orgao_codigo,acao_descricao, vetor_descricao, temas_explorar, ideias_forca, id_usuario
            ))
            ultimo_id = cursor.lastrowid
            
            cursor.execute("""
                INSERT INTO mpce_data (
                    mpce_id, data
                ) VALUES (%s, %s)
            """, (
                ultimo_id, data 
            ))
            
            for linha in linhas:
                
                cursor.execute("""
                    INSERT INTO mpce_linha_esforco (
                        mpce_id, linha_cd
                    ) VALUES (%s, %s)
                """, (
                    ultimo_id, linha 
                ))
            
            for publico in publicos:
            
                cursor.execute("""
                    INSERT INTO mpce_publico_alvo (
                        mpce_id, publico_alvo_cd
                    ) VALUES (%s, %s)
                """, (
                    ultimo_id, publico 
                ))
                
            for resultado in descricoes:
            
                cursor.execute("""
                    INSERT INTO resultado (
                        mpce_id, descricao
                    ) VALUES (%s, %s)
                """, (
                    ultimo_id, resultado 
                ))
            
            sql = """ INSERT INTO produto (mpce_id,descricao,link)
            values (%s,%s,%s)
            """
            for produto, link in zip(produtos, links):
                cursor.execute(sql,(ultimo_id,produto,link))
          
            conn.commit()

            cursor.close()
            conn.close()
            
            return redirect(url_for('tabela_mpce'))

        except Exception as e:
            return f"Erro ao salvar: {e}"
        
        
        if org and posto and nome and telefone and ciencia:
            # Aqui você pode salvar os dados, se quiser
            return redirect(url_for('form2'))
        else:
            # Faltou algum campo, renderiza de novo com erro
            return render_template('index.html',orgaos=orgaos,postograds=postograds, redes=redes,linhas=linhas,publicos=publicos,rede_fixa=rede_fixa, erro='Preencha todos os campos obrigatórios.')

       
    return render_template('index.html', orgaos=orgaos, postograds=postograds, redes=redes, linhas=linhas, publicos=publicos,rede_fixa=rede_fixa) 

@app.route('/get_orgaos_by_rede/<int:rede_id>')
def get_orgaos_by_rede(rede_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT codigo, nome FROM orgao WHERE rede_id = %s ORDER BY nome", (rede_id,))
    orgaos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(orgaos)

@app.route("/resultados_por_mpce/<int:mpce_id>")
def resultados_por_mpce(mpce_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            r.id,
            r.descricao,
            a.tipo_avaliacao_cd,
            ta.nm_avaliacao
        FROM resultado r
        LEFT JOIN avaliacao a ON a.resultado_id = r.id
        LEFT JOIN tipo_avaliacao ta ON ta.cd_avaliacao = a.tipo_avaliacao_cd
        WHERE r.mpce_id = %s
    """, (mpce_id,))
    resultados = cursor.fetchall()
    conn.close()
    return jsonify(resultados)

@app.route("/produtos_por_mpce/<int:mpce_id>")
def produtos_por_mpce(mpce_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, descricao,  COALESCE(link, '') AS link  FROM produto WHERE mpce_id = %s", (mpce_id,))
    produtos = cursor.fetchall()
    conn.close()
    return jsonify(produtos)

@app.route('/fidece1', methods=['GET', 'POST'])
def fidece1():
    
    orgaos = get_orgaos()
    postograds = get_postograd()
    
    # Pega o ID enviado via GET
    cd_mece = request.args.get('cd_mece')
    resultados = get_resultados(cd_mece)
    produtos = get_produtos(cd_mece)
    tipos_avaliacao = get_tipos_avaliacao()
    if cd_mece:
        session['cd_mece'] = cd_mece  # Armazena na sessão
        
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = f"""
           SELECT 
	    CONCAT(m.id,' - REDE ',r.nome) AS nome_rede, 
	    
		 (SELECT GROUP_CONCAT(d.data ORDER BY id SEPARATOR ';') 
			FROM mpce_data d WHERE d.mpce_id = m.id) AS datas,
			
		 (SELECT GROUP_CONCAT('- ',ace.descricao ORDER BY ace.cd_acao SEPARATOR ';') 
			FROM mpce_acao ac 
			LEFT JOIN acao_comunicacao_estrategica ace ON (ace.cd_acao = ac.acao_cd)
			WHERE ac.mpce_id = m.id) AS acoes,
        (SELECT GROUP_CONCAT('- ',l.nm_linha ORDER BY l.cd_linha SEPARATOR ';') 
		FROM mpce_linha_esforco le 
		LEFT JOIN linha_esforco l ON (l.cd_linha = le.linha_cd)
		WHERE le.mpce_id = m.id) AS linhas,
        	(SELECT GROUP_CONCAT(l.cod_ocecml ORDER BY l.cd_linha SEPARATOR ';') 
		FROM mpce_linha_esforco le 
		LEFT JOIN linha_esforco l ON (l.cd_linha = le.linha_cd)
		WHERE le.mpce_id = m.id) AS ocecml,
        
        		(SELECT GROUP_CONCAT('- ',p.nm_publico ORDER BY p.cd_publico SEPARATOR ';') 
		FROM mpce_publico_alvo pa 
		LEFT JOIN publico_alvo p ON (p.cd_publico = pa.publico_alvo_cd)
		WHERE pa.mpce_id = m.id) AS publicos,
       
		 m.*,
		 o.nome AS nome_orgao,
       c.nm_cidade AS nome_cidade
        FROM mpce m
        LEFT JOIN orgao o ON o.codigo = m.orgao_codigo
        LEFT JOIN cidade c ON c.cd_cidade = m.rede_id
        LEFT JOIN rede r ON (r.id = m.rede_id)
            WHERE m.id = %s
            ORDER BY m.id 
        """

        cursor.execute(sql, (cd_mece,))
        mece_lista = cursor.fetchall()
        cursor.close()
        conn.close()
    
    if request.method == 'POST':
        
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT cd_postograd FROM postograd where nm_postograd = %s", (request.form['posto_grad'],))
        cdposto = cursor.fetchone()        
        posto = cdposto[0]
        
        nome = request.form['nome_relator']
        telefone = request.form['telefone_relator']
        
        
        try:
           
            cursor.execute("""
                INSERT INTO fidece (
                    mpce_id, posto_grad_cd, nome, telefone
                ) VALUES (%s, %s, %s, %s)
            """, (
                cd_mece, posto,nome, telefone 
            ))
            
            ultimo_id = cursor.lastrowid
            
            cursor.execute("""
                 UPDATE mpce SET STATUS = 1
                    WHERE id = (%s)
            """, (cd_mece,))
            
            total2 = int(request.form.get('total_produtos', 0))

            for i in range(total2):
                produto_id = request.form.get(f'produto_id_{i}')
                descricao = request.form.get(f'descricao_produto_{i}')
                link = request.form.get(f'link_produto_{i}')
                if produto_id is not None:
                    cursor.execute("UPDATE produto SET descricao = %s, link = %s WHERE mpce_id = %s AND id = %s", (descricao, link, cd_mece, produto_id))

            conn.commit()
            cursor.close()
            conn.close()
            
            
            return redirect(url_for('form_resultado_fidece'))

        except Exception as e:
            return f"Erro ao salvar: {e}"
        
        
        
        if org and posto and nome and telefone and ciencia:
            # Aqui você pode salvar os dados, se quiser
            return redirect(url_for('fidece2'))
        else:
            # Faltou algum campo, renderiza de novo com erro
            return render_template('fidece1.html',orgaos=orgaos,postograds=postograds,mece_lista=mece_lista, resultados=resultados, produtos=produtos, tipos_avaliacao=tipos_avaliacao, url_anterior=request.referrer, erro='Preencha todos os campos obrigatórios.')

       
    return render_template('fidece1.html', orgaos=orgaos, postograds=postograds, mece_lista=mece_lista, resultados=resultados, produtos=produtos, tipos_avaliacao=tipos_avaliacao, url_anterior=request.referrer) 
       
    return render_template(
        'fidece1.html',
        orgaos=orgaos,
        postograds=postograds,
        mece_lista=mece_lista,
        resultados=resultados,
        tipos_avaliacao=tipos_avaliacao,
        url_anterior=request.referrer,
        valores_salvos=valores_salvos  # <- Adicionado aqui
    )

@app.route('/avaliar_resultado', methods=['POST'])
def avaliar_resultado():
    data = request.get_json()
    resultado_id = data.get("resultado_id")
    tipo_avaliacao_cd = data.get("tipo_avaliacao_cd")
    motivo = data.get("motivo")

    if not (resultado_id and tipo_avaliacao_cd):
        return jsonify({"success": False, "message": "Campos obrigatórios ausentes"})

    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT a.id FROM avaliacao a WHERE a.resultado_id = %s", (resultado_id,))
        resultado = cursor.fetchone()        
       
        if resultado is not None:
            cursor.execute("""
                UPDATE avaliacao set tipo_avaliacao_cd = %s, motivo = %s
                where resultado_id = %s
            """, (tipo_avaliacao_cd, motivo, resultado_id))
        else :
            cursor.execute("""
                INSERT INTO avaliacao (resultado_id, tipo_avaliacao_cd, motivo)
                VALUES (%s, %s, %s)
            """, (resultado_id, tipo_avaliacao_cd, motivo))
            

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        print("Erro ao salvar avaliação:", e)
        return jsonify({"success": False})

@app.route('/avaliacoes/<int:mpce_id>')
def consultar_avaliacoes(mpce_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.descricao, COALESCE(ta.nm_avaliacao, '') as nm_avaliacao , COALESCE(a.motivo, '') as motivo
        FROM resultado r 
        LEFT JOIN avaliacao a ON a.resultado_id = r.id
        LEFT JOIN tipo_avaliacao ta ON ta.cd_avaliacao = a.tipo_avaliacao_cd
        WHERE r.mpce_id = %s
    """, (mpce_id,))
    
    resultados = cursor.fetchall()
    conn.close()
    return jsonify(resultados)

@app.route('/produtos/<int:mpce_id>')
def listar_produtos(mpce_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.descricao, COALESCE(p.link, '') as link FROM produto p
        LEFT JOIN mpce m ON (m.id = p.mpce_id)
        WHERE p.mpce_id =  %s
    """, (mpce_id,))
    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(dados)

@app.route('/form_feedback', methods=['GET', 'POST'])
def form_feedback():
    
    fidece_lista = []
    
    orgaos = get_orgaos()
    postograds = get_postograd()
    
    # Pega o ID enviado via GET
    cd_mpce = request.args.get('mpce_id')
    if cd_mpce:
        session['mpce_id'] = cd_mpce  # Armazena na sessão
        
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = f"""
                    SELECT 
           CONCAT(m.id,' - REDE ',r.nome) AS nome_rede, 
 
               (SELECT GROUP_CONCAT(d.data ORDER BY id SEPARATOR ';') 
                  FROM mpce_data d WHERE d.mpce_id = m.id) AS datas,
		
               (SELECT GROUP_CONCAT('- ',ace.descricao ORDER BY ace.cd_acao SEPARATOR ';') 
                  FROM mpce_acao ac 
                  LEFT JOIN acao_comunicacao_estrategica ace ON (ace.cd_acao = ac.acao_cd)
                  WHERE ac.mpce_id = m.id) AS acoes,
           (SELECT GROUP_CONCAT('- ',l.nm_linha ORDER BY l.cd_linha SEPARATOR ';') 
              FROM mpce_linha_esforco le 
              LEFT JOIN linha_esforco l ON (l.cd_linha = le.linha_cd)
              WHERE le.mpce_id = m.id) AS linhas,
                  (SELECT GROUP_CONCAT(l.cod_ocecml ORDER BY l.cd_linha SEPARATOR ';') 
              FROM mpce_linha_esforco le 
              LEFT JOIN linha_esforco l ON (l.cd_linha = le.linha_cd)
              WHERE le.mpce_id = m.id) AS ocecml,
 
   		                    (SELECT GROUP_CONCAT('- ',p.nm_publico ORDER BY p.cd_publico SEPARATOR ';') 
              FROM mpce_publico_alvo pa 
              LEFT JOIN publico_alvo p ON (p.cd_publico = pa.publico_alvo_cd)
              WHERE pa.mpce_id = m.id) AS publicos,

               m.*,
               f.*,
               o.nome AS nome_orgao,
          c.nm_cidade AS nome_cidade
           FROM fidece f
           LEFT JOIN mpce m ON (m.id = f.mpce_id)
           LEFT JOIN orgao o ON o.codigo = m.orgao_codigo
           LEFT JOIN cidade c ON c.cd_cidade = m.rede_id
           LEFT JOIN rede r ON (r.id = m.rede_id)
            WHERE m.id = %s
            ORDER BY m.id 
        """

        cursor.execute(sql, (cd_mpce,))
        fidece_lista = cursor.fetchall()
        cursor.close()
        conn.close()
    
    if request.method == 'POST':
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT cd_postograd FROM postograd where nm_postograd = %s", (request.form['posto_grad'],))
        cdposto = cursor.fetchone()        
        posto = cdposto[0]

        cursor.execute("SELECT id FROM fidece where mpce_id = %s", (cd_mpce,))
        cdfidece = cursor.fetchone()        
        fidece_id = cdfidece[0]
        
        nome = request.form['nome_relator']
        telefone = request.form['telefone_relator']
        consideracoes_cce = request.form['consideracoes_cce']
        
        try:
           
            cursor.execute("""
                INSERT INTO feedback (
                    fidece_id, posto_grad_cd, nome, telefone, consideracoes_cce
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                fidece_id, posto,nome, telefone, consideracoes_cce 
            ))
            
            ultimo_id = cursor.lastrowid
            
            cursor.execute("""
                 UPDATE mpce SET STATUS = 2
                    WHERE id = (%s)
            """, (cd_mpce,))
            conn.commit()

            cursor.close()
            conn.close()
             
            
            usuario = session.get('usuario')
            perfil = session.get('perfil')
            tipo_usuario = session.get('tipo_usuario')
            session.clear()
            session['usuario'] = usuario
            session['perfil'] = perfil
            session['tipo_usuario'] = tipo_usuario
            return redirect(url_for('form_resultado_fidece'))

        except Exception as e:
            return f"Erro ao salvar: {e}"
        
        
        
        if org and posto and nome and telefone and ciencia:
            # Aqui você pode salvar os dados, se quiser
            return redirect(url_for('fidece2'))
        else:
            # Faltou algum campo, renderiza de novo com erro
            return render_template('fidece1.html',orgaos=orgaos,postograds=postograds,mece_lista=mece_lista, erro='Preencha todos os campos obrigatórios.')

       
    return render_template('form_feedback.html', orgaos=orgaos, postograds=postograds, fidece_lista=fidece_lista) 

@app.route('/form_manifestacao', methods=['GET', 'POST'])
def form_manifestacao():
    
    fidece_lista = []
    
    orgaos = get_orgaos()
    postograds = get_postograd()
    
    # Pega o ID enviado via GET
    cd_mpce = request.args.get('mpce_id')
    if cd_mpce:
        session['mpce_id'] = cd_mpce  # Armazena na sessão
        
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = f"""
                 SELECT 
                 CONCAT(m.id,' - REDE ',r.nome) AS nome_rede, 
 
                     (SELECT GROUP_CONCAT(d.data ORDER BY id SEPARATOR ';') 
                        FROM mpce_data d WHERE d.mpce_id = m.id) AS datas,
		
                     (SELECT GROUP_CONCAT('- ',ace.descricao ORDER BY ace.cd_acao SEPARATOR ';') 
                        FROM mpce_acao ac 
                        LEFT JOIN acao_comunicacao_estrategica ace ON (ace.cd_acao = ac.acao_cd)
                        WHERE ac.mpce_id = m.id) AS acoes,
                 (SELECT GROUP_CONCAT('- ',l.nm_linha ORDER BY l.cd_linha SEPARATOR ';') 
                    FROM mpce_linha_esforco le 
                    LEFT JOIN linha_esforco l ON (l.cd_linha = le.linha_cd)
                    WHERE le.mpce_id = m.id) AS linhas,
                        (SELECT GROUP_CONCAT(l.cod_ocecml ORDER BY l.cd_linha SEPARATOR ';') 
                    FROM mpce_linha_esforco le 
                    LEFT JOIN linha_esforco l ON (l.cd_linha = le.linha_cd)
                    WHERE le.mpce_id = m.id) AS ocecml,
 
 		                            (SELECT GROUP_CONCAT('- ',p.nm_publico ORDER BY p.cd_publico SEPARATOR ';') 
                    FROM mpce_publico_alvo pa 
                    LEFT JOIN publico_alvo p ON (p.cd_publico = pa.publico_alvo_cd)
                    WHERE pa.mpce_id = m.id) AS publicos,

                     m.*,
                     f.*,
                     fee.*,
                     o.nome AS nome_orgao,
                c.nm_cidade AS nome_cidade
                 FROM fidece f
                 LEFT JOIN mpce m ON (m.id = f.mpce_id)
                 LEFT JOIN orgao o ON o.codigo = m.orgao_codigo
                 LEFT JOIN cidade c ON c.cd_cidade = m.rede_id
                 LEFT JOIN rede r ON (r.id = m.rede_id)
                 left join feedback fee on (fee.fidece_id = f.id)
            WHERE m.id = %s
            ORDER BY m.id 
        """

        cursor.execute(sql, (cd_mpce,))
        feedback_lista = cursor.fetchall()
        cursor.close()
        conn.close()
    
    if request.method == 'POST':
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM fidece where mpce_id = %s", (cd_mpce,))
        cdfidece = cursor.fetchone()        
        fidece_id = cdfidece[0]
        
        manifestacao_om = request.form['manifestacao_om']
        
        try:
           
           # cursor.execute("""
           #     INSERT INTO feedback (
           #         fidece_id, posto_grad_cd, nome, telefone, consideracoes_cce
           #     ) VALUES (%s, %s, %s, %s, %s)
           # """, (
           #     fidece_id, posto,nome, telefone, consideracoes_cce 
           # ))
           # ultimo_id = cursor.lastrowid
            
            cursor.execute("""
                 UPDATE feedback SET manifestacao_om = %s
                    WHERE fidece_id = (%s)
            """, (manifestacao_om,fidece_id))
            conn.commit()
            
            cursor.execute("""
                 UPDATE mpce SET STATUS = 3
                    WHERE id = (%s)
            """, (cd_mpce,))
            conn.commit()
            

            cursor.close()
            conn.close()
             
            
            usuario = session.get('usuario')
            perfil = session.get('perfil')
            tipo_usuario = session.get('tipo_usuario')
            session.clear()
            session['usuario'] = usuario
            session['perfil'] = perfil
            session['tipo_usuario'] = tipo_usuario
            return redirect(url_for('form_resultado_fidece'))

        except Exception as e:
            return f"Erro ao salvar: {e}"
        
        
        
        if org and posto and nome and telefone and ciencia:
            # Aqui você pode salvar os dados, se quiser
            return redirect(url_for('fidece2'))
        else:
            # Faltou algum campo, renderiza de novo com erro
            return render_template('fidece1.html',orgaos=orgaos,postograds=postograds,feedback_lista=feedback_lista, erro='Preencha todos os campos obrigatórios.')

       
    return render_template('form_manifestacao.html', orgaos=orgaos, postograds=postograds, feedback_lista=feedback_lista) 

@app.route('/dados_resultados')
def dados_resultados():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, descricao, tipo_avaliacao_cd FROM resultado_estrategico")
    resultados = cursor.fetchall()

    for r in resultados:
        r["avaliacao"] = "Editar" if r["tipo_avaliacao_cd"] else "Avaliar"

    return jsonify(resultados)



@app.route('/avaliar_resultado_form/<int:resultado_id>', methods=['GET', 'POST'])
def avaliar_resultado_form(resultado_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Recupera o resultado e a avaliação atual
    cursor.execute("""
        SELECT 
            r.id,
            r.descricao,
            a.tipo_avaliacao_cd,
            a.motivo,
            r.mpce_id
        FROM resultado r
        LEFT JOIN avaliacao a ON a.resultado_id = r.id
        WHERE r.id = %s
    """, (resultado_id,))
    resultado = cursor.fetchone()

    if not resultado:
        return "Resultado não encontrado.", 404

    tipos_avaliacao = get_tipos_avaliacao()

    if request.method == 'POST':
        tipo_avaliacao_cd = request.form.get('tipo_avaliacao_cd')
        motivo = request.form.get('motivo')

        if not tipo_avaliacao_cd or not motivo:
            erro = "Preencha todos os campos."
            return render_template('form_avaliacao_resultado.html', resultado=resultado, tipos_avaliacao=tipos_avaliacao, erro=erro)

        # Atualiza ou insere
        cursor.execute("SELECT id FROM avaliacao WHERE resultado_id = %s", (resultado_id,))
        existe = cursor.fetchone()

        if existe:
            cursor.execute("""
                UPDATE avaliacao SET tipo_avaliacao_cd = %s, motivo = %s WHERE resultado_id = %s
            """, (tipo_avaliacao_cd, motivo, resultado_id))
        else:
            cursor.execute("""
                INSERT INTO avaliacao (resultado_id, tipo_avaliacao_cd, motivo)
                VALUES (%s, %s, %s)
            """, (resultado_id, tipo_avaliacao_cd, motivo))

        session['fidece_posto'] = session.get('fidece_posto', '')
        session['fidece_nome'] = session.get('fidece_nome', '')
        session['fidece_telefone'] = session.get('fidece_telefone', '')

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('fidece1', cd_mece=resultado['mpce_id']))

    cursor.close()
    conn.close()
    return render_template('form_avaliacao_resultado.html', resultado=resultado, tipos_avaliacao=tipos_avaliacao)