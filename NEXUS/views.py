# -*- coding: utf-8 -*-
"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, redirect, url_for, session  # IMPORTANTE
from NEXUS import app
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="10.1.140.15",
        user="root",
        password="alfa0101",
        database="eplm"
    )

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

def get_evento_principal():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT evento FROM evento_principal ORDER BY cd_evento")
    eventos_principais = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return eventos_principais

def get_cidades():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT CONCAT(TRIM(c.nm_cidade), '-', TRIM(uf.sg_uf)) AS cidade_uf FROM cidade c inner JOIN uf ON (uf.cd_uf = c.cd_uf) WHERE c.nm_cidade != '' AND (uf.cd_uf IN (8,12,19)) ORDER BY c.nm_cidade")
    cidades = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return cidades

def get_linhas_esforcos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nm_linha FROM linha_esforco order by nm_linha")
    linhas = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return linhas

def get_publicos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nm_publico FROM publico_alvo order by nm_publico")
    publicos = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return publicos


@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )


@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/form2', methods=['GET', 'POST'])
def form2():
    
    eventos_principais = get_evento_principal() 
    cidades = get_cidades();

    if request.method == 'POST':
        situacao = request.form.get('situacao_evento')
        descricao = request.form.get('descricao_evento')
        data = request.form.get('data_evento')
        municipio = request.form.get('municipio_evento')
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT cd_evento FROM evento_principal where evento = %s", (situacao,))
        cdevento = cursor.fetchone()
        session['situacao_evento'] = cdevento[0]
        
        session['descricao_evento'] = descricao
        session['data_evento'] = data
        
        cursor.execute("SELECT cd_cidade FROM cidade where nm_cidade = %s", (municipio.split('-')[0],))
        cdmunicipio = cursor.fetchone()
        session['municipio_evento'] = cdmunicipio[0]
        

        if situacao and descricao and data and municipio:
            # Aqui você pode salvar ou redirecionar para o form3
            return redirect(url_for('form3'))
        else:
            return render_template('form2.html',eventos_principais=eventos_principais,cidades=cidades, erro='Preencha todos os campos obrigatórios.')

    return render_template('form2.html', eventos_principais=eventos_principais,cidades=cidades)


@app.route('/form3', methods=['GET', 'POST'])
def form3():
    
    linhas = get_linhas_esforcos()
    
    if request.method == 'POST':
        
        linha = request.form.get('linha_esforco')
        
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT cd_linha FROM linha_esforco where nm_linha = %s", (linha,))
        cdlinha = cursor.fetchone()
        session['linha_esforco'] = cdlinha[0]

        if linha:
            # Aqui você pode salvar ou redirecionar para o form3
            return redirect(url_for('form4'))
        else:
            return render_template('form3.html', linhas=linhas, erro='Preencha todos os campos obrigatórios.')

    return render_template('form3.html', linhas=linhas)

@app.route('/form4', methods=['GET', 'POST'])
def form4():
    publicos = get_publicos()

    if request.method == 'POST':
        publico_prioritario = request.form.get('publico_prioritario')


        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT cd_publico FROM publico_alvo where nm_publico = %s", (publico_prioritario,))
        cdpublico = cursor.fetchone()
        session['publico_prioritario'] = cdpublico[0]
       

        if publico_prioritario:
            return redirect(url_for('form5'))
        else:
            return render_template('form4.html', publicos=publicos, erro='Esta pergunta é obrigatória.')

    return render_template('form4.html', publicos=publicos)

@app.route('/form5', methods=['GET', 'POST'])
def form5():
    tarefas_comsoc = [
        'Não se Aplica',
        'Divulgação PRÉ EVENTO em TV',
        'Divulgação PRÉ EVENTO em rádio',
        'Divulgação PRÉ EVENTO em Redes Sociais da OM (se autorizadas)',
        'Divulgação PRÉ EVENTO em Portais de notícias de parceiros',
        'Divulgação PRÉ EVENTO na página Internet da OM',
        '(RP) Brindes para parceiros, autoridades e militares',
        '(RP) Condução de cerimonial em evento (cerimonialistas)',
        '(RP) Expedição de convites',
        '(RP) Organização em geral e organização de eventos',
        '(RP) Orientação aos padrinhos de cada convidado',
        '(RP) Recepção de Autoridades',
        '(RP) Recepção do público em geral',
        '(PROD DIV) Criação de artes para material de divulgação do evento (design gráfico)',
        '(PROD DIV) Gravação de imagens (cinegrafista)',
        '(PROD DIV) Registro de imagens (fotógrafo)',
        '(PROD DIV) Produção audiovisual',
        'Divulgação PÓS EVENTO em TV',
        'Divulgação PÓS EVENTO em rádio',
        'Divulgação PÓS EVENTO em Redes Sociais de parceiros',
        'Divulgação PÓS EVENTO em Portais de notícias de parceiros',
        'Divulgação PÓS EVENTO na página Internet da OM',
        'Divulgação PÓS EVENTO em Redes Sociais da OM (se autorizadas)',
        'Outros produtos e serviços a serem executados pelo vetor COM SOC, não citados anteriormente:',
        'Assessorias de Imprensa (Nota de Esclarecimento)',
        'Assessorias de Imprensa (Coletiva de Imprensa)',
        'Assessorias de Imprensa (Produção de Press Release)'
    ]
    
    tarefas_comsoc2 = [
        'Não se Aplica',
        'Designação de porta-voz para entrevista',
        'Treinamento de porta-voz para entrevista (media training)',
        'Controle dos veículos de imprensa em evento (cerimônia, coletiva de imprensa, etc)',
        'Produção de texto para matérias/reportagens',
        'Produção de nota a imprensa (sfc)',
        'Detalhamento dos produtos e serviços demandados / Outras informações julgadas úteis: digitar no item "outro" abaixo:'
    ]
    
    relacoes_institucionais = [    
        'Não se Aplica',
        'Busca por parcerias para evento',
        'Levantamento de informações sobre parceiros',
        'Visitas de cortesia a parceiros',
        'Acolhimento de parceiros em visita (ciceronear)',
        'Acompanhamento durante a visita do parceiro',
        'Atualização das informações no banco de dados de parceiros',
        'Remessa de documento ou de convite a parceiro',
        'Tratativa simples junto aos parceiros (as tratativas complexas sobre o evento são sempre de responsabilidade do RELATOR do evento)',
        'Detalhamento dos produtos e serviços demandados / Outras informações julgadas úteis: digitar no item "outro" abaixo:'
    ]

    if request.method == 'POST':
        
        acao = request.form.get('acao')

        selecionados1 = request.form.getlist('tarefas')
        selecionados2 = request.form.getlist('tarefas2')
        selecionados3 = request.form.getlist('ri')
        outro = request.form.get('outro')
        outro2 = request.form.get('outro2')
        outro3 = request.form.get('outro3')
        
        session['tarefas'] = str(', '.join(request.form.getlist('tarefas')))
        session['tarefas2'] = str(', '.join(request.form.getlist('tarefas2')))
        session['ri'] = str(', '.join(request.form.getlist('ri')))
        
        
        if acao == 'salvar':
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO mece (
                        orgao, posotgrad, nome, telefone, evento, cidade, ciencia, linha_esforco, publico, 
                        situacao_evento, data, lista_tarefas1, descricao_evento, lista_tarefas2, lista_r1
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    session.get('organizacao_militar'),
                    session.get('posto_grad'),
                    session.get('nome_relator'),
                    session.get('telefone_relator'),
                    session.get('situacao_evento'),
                    session.get('municipio_evento'),
                    session.get('ciencia_escal'),
                    session.get('linha_esforco'),
                    session.get('publico_prioritario'),
                    'aaaaaa',
                    session.get('data_evento'),
                    session.get('lista_tarefas1'),
                    session.get('descricao_evento'),
                    session.get('lista_tarefas2'),
                    session.get('lista_r1')
                ))
                conn.commit()
                cursor.close()
                conn.close()
                
                ultimo_id = cursor.lastrowid
                session.clear()
                return redirect(url_for('tabela_mpce'))

            except Exception as e:
                return f"Erro ao salvar: {e}"

        elif acao == 'avancar':
            return redirect(url_for('form6'))

    return render_template('form5.html',
        tarefas_comsoc=tarefas_comsoc,
        tarefas_comsoc2=tarefas_comsoc2,
        relacoes_institucionais=relacoes_institucionais
    )







@app.route('/fidece2', methods=['GET', 'POST'])
def fidece2():
    
    eventos_principais = get_evento_principal() 
    cidades = get_cidades();

    if request.method == 'POST':
        numero = request.form.get('numero_evento')
        link = request.form.get('link_localizacao')
        situacao = request.form.get('situacao_evento')
        descricao = request.form.get('descricao_evento')
        data = request.form.get('data_evento')
        municipio = request.form.get('municipio_evento')
        
        conn = get_connection()
        cursor = conn.cursor()
        
        session['numero_evento'] = numero
        session['link_localizacao'] = link
        
        cursor.execute("SELECT cd_evento FROM evento_principal where evento = %s", (situacao,))
        cdevento = cursor.fetchone()
        session['situacao_evento'] = cdevento[0]
        
        session['descricao_evento'] = descricao
        session['data_evento'] = data
        
        cursor.execute("SELECT cd_cidade FROM cidade where nm_cidade = %s", (municipio.split('-')[0],))
        cdmunicipio = cursor.fetchone()
        session['municipio_evento'] = cdmunicipio[0]
        

        if situacao and descricao and data and municipio and numero and link:
            # Aqui você pode salvar ou redirecionar para o form3
            return redirect(url_for('fidece3'))
        else:
            return render_template('fidece2.html',eventos_principais=eventos_principais,cidades=cidades, erro='Preencha todos os campos obrigatórios.')

    return render_template('fidece2.html', eventos_principais=eventos_principais,cidades=cidades)


@app.route('/fidece3', methods=['GET', 'POST'])
def fidece3():
    
    linhas = get_linhas_esforcos()
    
    if request.method == 'POST':
        
        linha = request.form.get('linha_esforco')
        linha2 = request.form.get('linha_esforco2')
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT cd_linha FROM linha_esforco where nm_linha = %s", (linha,))
        cdlinha = cursor.fetchone()
        session['linha_esforco'] = cdlinha[0]
        
        cursor.execute("SELECT cd_linha FROM linha_esforco where nm_linha = %s", (linha2,))
        cdlinha2 = cursor.fetchone()
        session['linha_esforco2'] = cdlinha2[0]

        if linha:
            # Aqui você pode salvar ou redirecionar para o form3
            return redirect(url_for('fidece4'))
        else:
            return render_template('fidece3.html', linhas=linhas, erro='Preencha todos os campos obrigatórios.')

    return render_template('fidece3.html', linhas=linhas)


@app.route('/fidece4', methods=['GET', 'POST'])
def fidece4():
    publicos = get_publicos()

    if request.method == 'POST':
        
        publico_prioritario = request.form.get('publico_prioritario')
        publico_prioritario2 = request.form.get('publico_prioritario2')


        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT cd_publico FROM publico_alvo where nm_publico = %s", (publico_prioritario,))
        cdpublico = cursor.fetchone()
        session['publico_prioritario'] = cdpublico[0]
        
        cursor.execute("SELECT cd_publico FROM publico_alvo where nm_publico = %s", (publico_prioritario2,))
        cdpublico2 = cursor.fetchone()
        session['publico_prioritario2'] = cdpublico2[0]
       

        if publico_prioritario:
            return redirect(url_for('fidece5'))
        else:
            return render_template('fidece4.html', publicos=publicos, erro='Esta pergunta é obrigatória.')

    return render_template('fidece4.html', publicos=publicos)

@app.route('/fidece5', methods=['GET', 'POST'])
def fidece5():
    tarefas_comsoc = [
        'Não se Aplica',
        'Divulgação PRÉ EVENTO em TV',
        'Divulgação PRÉ EVENTO em rádio',
        'Divulgação PRÉ EVENTO em Redes Sociais da OM (se autorizadas)',
        'Divulgação PRÉ EVENTO em Portais de notícias de parceiros',
        'Divulgação PRÉ EVENTO na página Internet da OM',
        '(RP) Brindes para parceiros, autoridades e militares',
        '(RP) Condução de cerimonial em evento (cerimonialistas)',
        '(RP) Expedição de convites',
        '(RP) Organização em geral e organização de eventos',
        '(RP) Orientação aos padrinhos de cada convidado',
        '(RP) Recepção de Autoridades',
        '(RP) Recepção do público em geral',
        '(PROD DIV) Criação de artes para material de divulgação do evento (design gráfico)',
        '(PROD DIV) Gravação de imagens (cinegrafista)',
        '(PROD DIV) Registro de imagens (fotógrafo)',
        '(PROD DIV) Produção audiovisual',
        'Divulgação PÓS EVENTO em TV',
        'Divulgação PÓS EVENTO em rádio',
        'Divulgação PÓS EVENTO em Redes Sociais de parceiros',
        'Divulgação PÓS EVENTO em Portais de notícias de parceiros',
        'Divulgação PÓS EVENTO na página Internet da OM',
        'Divulgação PÓS EVENTO em Redes Sociais da OM (se autorizadas)',
        'Outros produtos e serviços a serem executados pelo vetor COM SOC, não citados anteriormente:',
        'Assessorias de Imprensa (Nota de Esclarecimento)',
        'Assessorias de Imprensa (Coletiva de Imprensa)',
        'Assessorias de Imprensa (Produção de Press Release)'
    ]
    
    tarefas_comsoc2 = [
        'Não se Aplica',
        'Designação de porta-voz para entrevista',
        'Treinamento de porta-voz para entrevista (media training)',
        'Controle dos veículos de imprensa em evento (cerimônia, coletiva de imprensa, etc)',
        'Produção de texto para matérias/reportagens',
        'Produção de nota a imprensa (sfc)',
        'Detalhamento dos produtos e serviços demandados / Outras informações julgadas úteis: digitar no item "outro" abaixo:'
    ]
    
    relacoes_institucionais = [    
        'Não se Aplica',
        'Busca por parcerias para evento',
        'Levantamento de informações sobre parceiros',
        'Visitas de cortesia a parceiros',
        'Acolhimento de parceiros em visita (ciceronear)',
        'Acompanhamento durante a visita do parceiro',
        'Atualização das informações no banco de dados de parceiros',
        'Remessa de documento ou de convite a parceiro',
        'Tratativa simples junto aos parceiros (as tratativas complexas sobre o evento são sempre de responsabilidade do RELATOR do evento)',
        'Detalhamento dos produtos e serviços demandados / Outras informações julgadas úteis: digitar no item "outro" abaixo:'
    ]

    if request.method == 'POST':
        
        acao = request.form.get('acao')

        selecionados1 = request.form.getlist('tarefas')
        selecionados2 = request.form.getlist('tarefas2')
        selecionados3 = request.form.getlist('ri')
        outro = request.form.get('outro')
        outro2 = request.form.get('outro2')
        outro3 = request.form.get('outro3')
        
        session['tarefas'] = str(', '.join(request.form.getlist('tarefas')))
        session['tarefas2'] = str(', '.join(request.form.getlist('tarefas2')))
        session['ri'] = str(', '.join(request.form.getlist('ri')))
        
        
        if acao == 'salvar':
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO fidece (
                        cdorgao, postograd, nome, telefone, ciencia, numero_evento, link_localizacao, situacao_evento, descricao_evento, 
                        data_evento, municipio, linha_esforco, linha_esforco2, publico, publico2, tarefas,tarefas2, ri
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    session.get('organizacao_militar'),
                    session.get('posto_grad'),
                    session.get('nome_relator'),
                    session.get('telefone_relator'),
                    session.get('ciencia_escal'),
                    session.get('numero_evento'),
                    session.get('link_localizacao'),
                    session.get('situacao_evento'),
                    session.get('descricao_evento'),
                    session.get('data_evento'),
                    session.get('municipio_evento'),
                    session.get('linha_esforco'),
                    session.get('linha_esforco2'),
                    session.get('publico_prioritario'),
                    session.get('publico_prioritario2'),
                    session.get('lista_tarefas1'),
                    session.get('lista_tarefas2'),
                    session.get('lista_r1')
                ))
                conn.commit()
                cursor.close()
                conn.close()
                
                ultimo_id = cursor.lastrowid
                session.clear()
                return redirect(url_for('form_resultado_fidece'))

            except Exception as e:
                return f"Erro ao salvar: {e}"

        elif acao == 'avancar':
            return redirect(url_for('fidece6'))

    return render_template('fidece5.html',
        tarefas_comsoc=tarefas_comsoc,
        tarefas_comsoc2=tarefas_comsoc2,
        relacoes_institucionais=relacoes_institucionais
    )









   