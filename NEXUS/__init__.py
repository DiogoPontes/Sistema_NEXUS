"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)
app.secret_key = '2025Cml$$S3cT1'  # NECESS�RIO para usar sessions

import NEXUS.conexao
import NEXUS.views
import NEXUS.routes.formularios
import NEXUS.routes.tabelas
import NEXUS.routes.metricas
import NEXUS.routes.relatorios

