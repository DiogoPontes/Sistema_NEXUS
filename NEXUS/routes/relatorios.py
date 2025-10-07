from flask import send_file, request
from reportlab.lib.pagesizes import landscape, A4, A3
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Preformatted
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from NEXUS import app
from NEXUS.conexao import get_connection

link_style = ParagraphStyle(
    'link',
    fontSize=9,
    underline=True,
    leading=12,
    wordWrap='CJK'
)

def formatar_links(texto):
    if not texto:
        return ""
    linhas = texto.split("\n")
    saida = []
    for linha in linhas:
        if "(" in linha and linha.endswith(")"):
            # Extrai o link do formato (http://...)
            try:
                desc, url = linha.rsplit("(", 1)
                url = url.strip(")")
                saida.append(f'{desc.strip()} <link href="{url}">{url}</link>')
            except:
                saida.append(linha)
        else:
            saida.append(linha)
    return "<br/>".join(saida)



@app.route('/gerar_pdf_mpce')
def gerar_pdf_mpce():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Filtros da URL
    rede_filtro = request.args.get('rede')  # Ex: "RJ,ES"
    mes_filtro = request.args.get('mes')    # Ex: "Agosto,Setembro"
   
    # Montar cláusulas condicionais
    condicoes = []
    parametros = []

    uf_map = {
        "Rio de Janeiro": "RJ",
        "Espirito Santo": "ES",
        "Minas Gerais": "MG"
    }

    if rede_filtro:
        nomes = [x.strip() for x in rede_filtro.split(',')]
        rede_list = [uf_map.get(nome, nome) for nome in nomes]  # substitui nome por UF
        condicoes.append(f"r.nome IN ({','.join(['%s'] * len(rede_list))})")
        parametros += rede_list

    if mes_filtro:
        mes_map = {
            "Janeiro": "01", "Fevereiro": "02", "Março": "03", "Abril": "04",
            "Maio": "05", "Junho": "06", "Julho": "07", "Agosto": "08",
            "Setembro": "09", "Outubro": "10", "Novembro": "11", "Dezembro": "12"
        }
        meses = [mes_map[m] for m in mes_filtro.split(',') if m in mes_map]
        
    if meses:
        condicoes.append(
            f"""EXISTS (
                SELECT 1 FROM mpce_data d
                WHERE d.mpce_id = m.id
                AND MONTH(d.data) IN ({','.join(['%s'] * len(meses))})
            )"""
        )
        parametros += meses

    where_clause = f"WHERE {' AND '.join(condicoes)}" if condicoes else ""
    order_by = request.args.get('order_by') 
    # Whitelist p/ ORDER BY
    order_expr = "(SELECT MIN(d.data) FROM mpce_data d WHERE d.mpce_id = m.id)"  # padrão = menor_data
    order_dir = "ASC"

    if order_by:
        try:
            field, direction = order_by.split(':', 1)
            direction = direction.upper()
            if direction not in ('ASC', 'DESC'):
                direction = 'ASC'

            allowed = {
                'nome_rede':       "CONCAT(m.id,' - REDE ',r.nome)",
                'menor_data':      "(SELECT MIN(d.data) FROM mpce_data d WHERE d.mpce_id = m.id)",
                'acoes':           "(SELECT GROUP_CONCAT(ace.descricao ORDER BY ace.cd_acao SEPARATOR ' ') FROM mpce_acao ac LEFT JOIN acao_comunicacao_estrategica ace ON ace.cd_acao = ac.acao_cd WHERE ac.mpce_id = m.id)",
                'linhas':          "(SELECT GROUP_CONCAT(l.nm_linha ORDER BY l.cd_linha SEPARATOR ' ') FROM mpce_linha_esforco le LEFT JOIN linha_esforco l ON l.cd_linha = le.linha_cd WHERE le.mpce_id = m.id)",
                'publicos':        "(SELECT GROUP_CONCAT(p.nm_publico ORDER BY p.cd_publico SEPARATOR ' ') FROM mpce_publico_alvo pa LEFT JOIN publico_alvo p ON p.cd_publico = pa.publico_alvo_cd WHERE pa.mpce_id = m.id)",
                'nome_orgao':      "o.nome",
                'vetor_descricao': "m.vetor_descricao",
                'temas_explorar':  "m.temas_explorar",
                'resultados':      "(SELECT GROUP_CONCAT(descricao SEPARATOR ' ') FROM resultado WHERE mpce_id = m.id)",
                'ideias_forca':    "m.ideias_forca",
                'produtos':        "(SELECT GROUP_CONCAT(CONCAT(descricao,IF(link IS NOT NULL AND link != '', CONCAT(' ', link), '')) SEPARATOR ' ') FROM produto WHERE mpce_id = m.id)",
            }
            if field in allowed:
                order_expr = allowed[field]
                order_dir  = direction
        except Exception:
            pass


    sql = f"""
       SELECT 
             CONCAT(m.id,' - REDE ',r.nome) AS nome_rede, 
             (SELECT GROUP_CONCAT(DATE_FORMAT(d.data, '%d/%m/%Y') ORDER BY id SEPARATOR '\\n') FROM mpce_data d WHERE d.mpce_id = m.id) AS datas,
     
             (SELECT GROUP_CONCAT(CONCAT('• ', ace.descricao) ORDER BY ace.cd_acao SEPARATOR '\\n') FROM mpce_acao ac 
              LEFT JOIN acao_comunicacao_estrategica ace ON ace.cd_acao = ac.acao_cd WHERE ac.mpce_id = m.id) AS acoes,
      
             (SELECT GROUP_CONCAT(CONCAT('• ', l.nm_linha) ORDER BY l.cd_linha SEPARATOR '\\n') FROM mpce_linha_esforco le 
              LEFT JOIN linha_esforco l ON l.cd_linha = le.linha_cd WHERE le.mpce_id = m.id) AS linhas,
             (SELECT GROUP_CONCAT(CONCAT('', l.cod_ocecml) ORDER BY l.cd_linha SEPARATOR '\\n') FROM mpce_linha_esforco le 
              LEFT JOIN linha_esforco l ON l.cd_linha = le.linha_cd WHERE le.mpce_id = m.id) AS ocecml,
             (SELECT GROUP_CONCAT(CONCAT('• ',p.nm_publico) ORDER BY p.cd_publico SEPARATOR '\\n') FROM mpce_publico_alvo pa 
              LEFT JOIN publico_alvo p ON p.cd_publico = pa.publico_alvo_cd WHERE pa.mpce_id = m.id) AS publicos,
             (SELECT GROUP_CONCAT(CONCAT('• ',pa2.publico_segmentado) ORDER BY pa2.publico_alvo_cd SEPARATOR '\\n') 
              FROM mpce_publico_alvo pa2 
              LEFT JOIN publico_alvo p2 ON p2.cd_publico = pa2.publico_alvo_cd WHERE pa2.mpce_id = m.id) AS publicos_segmentado,
              m.*,
              (SELECT MIN(d.data) FROM mpce_data d WHERE d.mpce_id = m.id) AS menor_data,
             o.nome AS nome_orgao,
            (SELECT GROUP_CONCAT(CONCAT('• ', descricao) SEPARATOR '\\n') FROM resultado WHERE mpce_id = m.id) AS resultados,
            (SELECT GROUP_CONCAT(CONCAT('• ', descricao, IF(link IS NOT NULL AND link != '', CONCAT(' (', link, ')'), '')) SEPARATOR '\\n')
            FROM produto WHERE mpce_id = m.id) AS produtos
                FROM mpce m
            LEFT JOIN orgao o ON o.codigo = m.orgao_codigo
            LEFT JOIN rede r ON r.id = m.rede_id
            {where_clause}
            GROUP BY m.id
            ORDER BY {order_expr} {order_dir}, m.id
        """

    cursor.execute(sql, parametros)
    registros = cursor.fetchall()
    cursor.close()
    conn.close()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A3), rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)

    styles = getSampleStyleSheet()
    estilo_celula = ParagraphStyle(
        name='cell',
        fontSize=9,
        leading=12,
        wordWrap='LTR',
    )

    cabecalhos = [
        "NÚMERO DE PAUTA/REDE", "DATA", "AÇÃO DE COMUNICAÇÃO ESTRATÉGICA",
        "LINHA DE ESFORÇO", "OCE", "PÚBLICO-ALVO", "VETOR A ATUAR",
        "RESULTADO PRETENDIDOS", "TEMAS A EXPLORAR", "IDEIAS-FORÇA", "PRODUTOS"
    ]

    dados = [[Paragraph(h, styles['Heading5']) for h in cabecalhos]]

    for r in registros:
        linha = [
            Paragraph(r["nome_rede"] or "", estilo_celula),
            Paragraph(r["datas"] or "", estilo_celula),
            Paragraph((r["acao_descricao"] or "").replace("\n", "<br/>"), estilo_celula),
            Paragraph((r["linhas"] or "").replace("\n", "<br/>"), estilo_celula),
            Paragraph((r["ocecml"] or "").replace("\n", "<br/>"), estilo_celula),
            Paragraph((r["publicos"] or "").replace("\n", "<br/>"), estilo_celula),
            Paragraph(r["vetor_descricao"] or "", estilo_celula),
            Paragraph((r["resultados"] or "").replace("\n", "<br/>"), estilo_celula),
            Paragraph(r["temas_explorar"] or "", estilo_celula),
            Paragraph(r["ideias_forca"] or "", estilo_celula),
            Paragraph(formatar_links(r["produtos"]), link_style),
        ]
        dados.append(linha)

    tabela = Table(dados, repeatRows=1, splitByRow=True, colWidths=[75, 65, 120, 100, 32, 100, 130, 140, 120, 120])
    tabela.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))

    elementos = [
        Paragraph("<b>MPCE - Matriz de Planejamento de Comunicação Estratégica</b>", styles['Title']),
        Spacer(1, 12),
        tabela
    ]

    doc.build(elementos)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="relatorio_mpce.pdf", mimetype='application/pdf')



@app.route('/gerar_pdf_fidece')
def gerar_pdf_fidece():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Filtros da URL
    rede_filtro = request.args.get('rede')  # Ex: "RJ,ES"
    mes_filtro = request.args.get('mes')    # Ex: "Agosto,Setembro"
   
    # Montar cláusulas condicionais
    condicoes = []
    parametros = []

    uf_map = {
        "Rio de Janeiro": "RJ",
        "Espirito Santo": "ES",
        "Minas Gerais": "MG"
    }

    if rede_filtro:
        nomes = [x.strip() for x in rede_filtro.split(',')]
        rede_list = [uf_map.get(nome, nome) for nome in nomes]  # substitui nome por UF
        condicoes.append(f"r.nome IN ({','.join(['%s'] * len(rede_list))})")
        parametros += rede_list

    if mes_filtro:
        mes_map = {
            "Janeiro": "01", "Fevereiro": "02", "Março": "03", "Abril": "04",
            "Maio": "05", "Junho": "06", "Julho": "07", "Agosto": "08",
            "Setembro": "09", "Outubro": "10", "Novembro": "11", "Dezembro": "12"
        }
        meses = [mes_map[m] for m in mes_filtro.split(',') if m in mes_map]
        
    if meses:
        condicoes.append(
            f"""EXISTS (
                SELECT 1 FROM mpce_data d
                WHERE d.mpce_id = m.id
                AND MONTH(d.data) IN ({','.join(['%s'] * len(meses))})
            )"""
        )
        parametros += meses

    meses = []  # <- garante variável inicializada

    order_by = request.args.get('order_by')
    where_clause = f"WHERE {' AND '.join(condicoes)}" if condicoes else ""
    order_expr = "(SELECT MIN(d.data) FROM mpce_data d WHERE d.mpce_id = m.id)"  # padrão
    order_dir = "ASC"

    if order_by:
        try:
            field, direction = order_by.split(':', 1)
            direction = direction.upper()
            if direction not in ('ASC', 'DESC'):
                direction = 'ASC'

            allowed = {
                'nome_rede':       "CONCAT(m.id,' - REDE ',r.nome)",
                'menor_data':      "(SELECT MIN(d.data) FROM mpce_data d WHERE d.mpce_id = m.id)",
                'acoes':           "(SELECT GROUP_CONCAT(ace.descricao ORDER BY ace.cd_acao SEPARATOR ' ') FROM mpce_acao ac LEFT JOIN acao_comunicacao_estrategica ace ON ace.cd_acao = ac.acao_cd WHERE ac.mpce_id = m.id)",
                'vetor_descricao': "m.vetor_descricao",
                'produtos':        "(SELECT GROUP_CONCAT(CONCAT(descricao,IF(link IS NOT NULL AND link != '', CONCAT(' ', link), '')) SEPARATOR ' ') FROM produto WHERE mpce_id = m.id)",
                'resultados':      "(SELECT GROUP_CONCAT(descricao SEPARATOR ' ') FROM resultado WHERE mpce_id = m.id)",
                'militar':         "CONCAT(pg.sg_postograd,' ',f.nome)",
                'consideracoes_cce': "COALESCE(fe.consideracoes_cce, '')",
                'manifestacao_om':   "COALESCE(fe.manifestacao_om, '')",
            }
            if field in allowed:
                order_expr = allowed[field]
                order_dir  = direction
        except Exception:
            pass



    sql = f"""
                   SELECT distinct
                 CONCAT(m.id,' - REDE ',r.nome) AS nome_rede,

                 (SELECT GROUP_CONCAT(DATE_FORMAT(d.data, '%d/%m/%Y') ORDER BY id SEPARATOR '; ') FROM mpce_data d WHERE d.mpce_id = m.id) AS datas,
            

                 (SELECT GROUP_CONCAT('- ',ace.descricao ORDER BY ace.cd_acao SEPARATOR ';') 
                  FROM mpce_acao ac 
                  LEFT JOIN acao_comunicacao_estrategica ace ON ace.cd_acao = ac.acao_cd
                  WHERE ac.mpce_id = m.id) AS acoes,

                 m.vetor_descricao,
                 m.status,
                 f.*,
                 COALESCE(fe.consideracoes_cce, '') as consideracoes_cce,
                 COALESCE(fe.manifestacao_om, '') as manifestacao_om,
                 (SELECT MIN(d.data) FROM mpce_data d WHERE d.mpce_id = m.id) AS menor_data,
                  CONCAT(pg.sg_postograd,' ',f.nome) AS militar,
	             (SELECT GROUP_CONCAT(CONCAT('• ', descricao) SEPARATOR '\\n') FROM resultado WHERE mpce_id = m.id) AS resultados,
	             (SELECT GROUP_CONCAT(CONCAT('• ', descricao, IF(link IS NOT NULL AND link != '', CONCAT(' (', link, ')'), '')) SEPARATOR '\\n')
 	            FROM produto WHERE mpce_id = m.id) AS produtos
               FROM fidece f
               LEFT JOIN mpce m ON m.id = f.mpce_id
               LEFT JOIN rede r ON r.id = m.rede_id
               LEFT JOIN feedback fe ON fe.fidece_id = f.id
               LEFT JOIN postograd pg ON (pg.cd_postograd = f.posto_grad_cd)
              {where_clause}
            GROUP BY m.id
            ORDER BY {order_expr} {order_dir}, m.id

        """

    cursor.execute(sql, parametros)
    registros = cursor.fetchall()
    cursor.close()
    conn.close()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A3), rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)

    styles = getSampleStyleSheet()
    estilo_celula = ParagraphStyle(
        name='cell',
        fontSize=9,
        leading=12,
        wordWrap='LTR',
    )

    cabecalhos = [
        "NÚMERO DE PAUTA/REDE", "DATA", "AÇÃO DE COMUNICAÇÃO ESTRATÉGICA",
        "VETOR A ATUAR", "PRODUTOS", "RESULTADOS", "AUTOR", "CONSIDERAÇÕES DA REDE", "MANIFESTAÇÃO DO VETOR"
    ]

    dados = [[Paragraph(h, styles['Heading5']) for h in cabecalhos]]

    for r in registros:
        linha = [
            Paragraph(r["nome_rede"] or "", estilo_celula),
            Paragraph(r["datas"] or "", estilo_celula),
            Paragraph((r["acoes"] or "").replace("\n", "<br/>"), estilo_celula),
            Paragraph(r["vetor_descricao"] or "", estilo_celula),
            Paragraph(formatar_links(r["produtos"]), link_style),
            Paragraph((r["resultados"] or "").replace("\n", "<br/>"), estilo_celula),
            Paragraph(r["militar"] or "", estilo_celula),
            Paragraph(r["consideracoes_cce"] or "", estilo_celula),
            Paragraph(r["manifestacao_om"] or "", estilo_celula),
        ]
        dados.append(linha)

    tabela = Table(dados, repeatRows=1, splitByRow=True, colWidths=[75, 65, 120, 100, 180, 180, 75, 130, 130])
    tabela.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))

    elementos = [
        Paragraph("<b>FIDECE - Ficha Descritiva de Eventos de Comunicação Estratégica</b>", styles['Title']),
        Spacer(1, 12),
        tabela
    ]

    doc.build(elementos)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="relatorio_fidece.pdf", mimetype='application/pdf')
