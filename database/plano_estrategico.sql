-- --------------------------------------------------------
-- Servidor:                     10.1.140.249
-- Versão do servidor:           10.1.14-MariaDB - MariaDB Server
-- OS do Servidor:               Linux
-- HeidiSQL Versão:              12.7.0.6850
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Copiando estrutura do banco de dados para plano_estrategico
CREATE DATABASE IF NOT EXISTS `plano_estrategico` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `plano_estrategico`;

-- Copiando estrutura para tabela plano_estrategico.acao_comunicacao_estrategica
CREATE TABLE IF NOT EXISTS `acao_comunicacao_estrategica` (
  `cd_acao` int(11) NOT NULL AUTO_INCREMENT,
  `descricao` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`cd_acao`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.avaliacao
CREATE TABLE IF NOT EXISTS `avaliacao` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `resultado_id` int(11) NOT NULL,
  `tipo_avaliacao_cd` int(11) NOT NULL,
  `motivo` text,
  PRIMARY KEY (`id`),
  KEY `FK_avaliacao_resultado` (`resultado_id`),
  KEY `FK_avaliacao_tipo_avaliacao` (`tipo_avaliacao_cd`),
  CONSTRAINT `FK_avaliacao_resultado` FOREIGN KEY (`resultado_id`) REFERENCES `resultado` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_avaliacao_tipo_avaliacao` FOREIGN KEY (`tipo_avaliacao_cd`) REFERENCES `tipo_avaliacao` (`cd_avaliacao`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=473 DEFAULT CHARSET=utf8;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.cidade
CREATE TABLE IF NOT EXISTS `cidade` (
  `cd_cidade` bigint(20) NOT NULL,
  `nm_cidade` varchar(60) NOT NULL,
  `nr_ddd` varchar(3) DEFAULT NULL,
  `cd_uf` bigint(20) NOT NULL DEFAULT '19',
  PRIMARY KEY (`cd_cidade`),
  KEY `fk_cidade_uf1_idx` (`cd_uf`),
  CONSTRAINT `fk_cidade_uf1` FOREIGN KEY (`cd_uf`) REFERENCES `uf` (`cd_uf`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.feedback
CREATE TABLE IF NOT EXISTS `feedback` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fidece_id` int(11) DEFAULT NULL,
  `posto_grad_cd` int(11) DEFAULT NULL,
  `nome` varchar(150) DEFAULT NULL,
  `telefone` varchar(20) DEFAULT NULL,
  `consideracoes_cce` varchar(500) DEFAULT NULL,
  `manifestacao_om` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_feedback_postograd` (`posto_grad_cd`),
  KEY `FK_feedback_mpce` (`fidece_id`) USING BTREE,
  CONSTRAINT `FK_feedback_fidece` FOREIGN KEY (`fidece_id`) REFERENCES `fidece` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_feedback_postograd` FOREIGN KEY (`posto_grad_cd`) REFERENCES `postograd` (`cd_postograd`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=86 DEFAULT CHARSET=utf8;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.fidece
CREATE TABLE IF NOT EXISTS `fidece` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mpce_id` int(11) DEFAULT NULL,
  `posto_grad_cd` int(11) DEFAULT NULL,
  `nome` varchar(150) DEFAULT NULL,
  `telefone` varchar(20) DEFAULT NULL,
  `arquivado` int(11) DEFAULT '0',
  `id_usuario` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_fidece_postograd` (`posto_grad_cd`),
  KEY `FK_fidece_mpce` (`mpce_id`),
  KEY `FK_fidece_usuario` (`id_usuario`),
  CONSTRAINT `FK_fidece_mpce` FOREIGN KEY (`mpce_id`) REFERENCES `mpce` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_fidece_postograd` FOREIGN KEY (`posto_grad_cd`) REFERENCES `postograd` (`cd_postograd`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_fidece_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`cd_usuario`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=503 DEFAULT CHARSET=utf8;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.linha_esforco
CREATE TABLE IF NOT EXISTS `linha_esforco` (
  `cd_linha` int(11) NOT NULL AUTO_INCREMENT,
  `cod_ocecml` int(11) DEFAULT NULL,
  `nm_linha` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`cd_linha`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.log_audit
CREATE TABLE IF NOT EXISTS `log_audit` (
  `id_log` int(11) NOT NULL AUTO_INCREMENT,
  `id_tabela` int(11) DEFAULT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  `data` datetime DEFAULT NULL,
  `operacao` enum('INSERT','UPDATE','DELETE','ARQUIVADO') DEFAULT NULL,
  `id_registro` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_log`) USING BTREE,
  KEY `fk_log_tabela` (`id_tabela`) USING BTREE,
  KEY `fk_uduario` (`id_usuario`) USING BTREE,
  CONSTRAINT `fk_log_tabela` FOREIGN KEY (`id_tabela`) REFERENCES `log_tabela` (`id_tabela`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_uduario` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`cd_usuario`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=2234 DEFAULT CHARSET=utf8;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.log_tabela
CREATE TABLE IF NOT EXISTS `log_tabela` (
  `id_tabela` int(11) NOT NULL,
  `tipo_tabela` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_tabela`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.mpce
CREATE TABLE IF NOT EXISTS `mpce` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rede_id` int(11) DEFAULT NULL,
  `orgao_codigo` int(11) DEFAULT NULL,
  `acao_descricao` text COLLATE utf8_unicode_ci,
  `vetor_descricao` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL,
  `temas_explorar` text COLLATE utf8_unicode_ci,
  `ideias_forca` text COLLATE utf8_unicode_ci,
  `status` int(11) DEFAULT '0' COMMENT '0 = sem nada; 1 = com fidece; 2 = com fidece e feedback',
  `arquivado` int(11) DEFAULT '0',
  `id_usuario` int(11) DEFAULT NULL,
  `posto_grad_cd` int(11) DEFAULT NULL,
  `nome` varchar(150) COLLATE utf8_unicode_ci DEFAULT NULL,
  `setor` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `FK_orgao` (`orgao_codigo`) USING BTREE,
  KEY `FK_mpce_rede` (`rede_id`),
  KEY `FK_mpce_usuario` (`id_usuario`),
  CONSTRAINT `FK_mpce_rede` FOREIGN KEY (`rede_id`) REFERENCES `rede` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `FK_mpce_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`cd_usuario`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=564 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='Matriz de Planejamento de Comunicação Estratégica';

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.mpce_acao
CREATE TABLE IF NOT EXISTS `mpce_acao` (
  `mpce_id` int(11) NOT NULL,
  `acao_cd` int(11) NOT NULL,
  PRIMARY KEY (`mpce_id`,`acao_cd`),
  KEY `acao_cd` (`acao_cd`),
  CONSTRAINT `mpce_acao_ibfk_1` FOREIGN KEY (`mpce_id`) REFERENCES `mpce` (`id`),
  CONSTRAINT `mpce_acao_ibfk_2` FOREIGN KEY (`acao_cd`) REFERENCES `acao_comunicacao_estrategica` (`cd_acao`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.mpce_data
CREATE TABLE IF NOT EXISTS `mpce_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mpce_id` int(11) DEFAULT NULL,
  `data` date DEFAULT NULL,
  `data_fim` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_mpce_data_mpce` (`mpce_id`),
  CONSTRAINT `FK_mpce_data_mpce` FOREIGN KEY (`mpce_id`) REFERENCES `mpce` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=570 DEFAULT CHARSET=utf8;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.mpce_linha_esforco
CREATE TABLE IF NOT EXISTS `mpce_linha_esforco` (
  `mpce_id` int(11) NOT NULL,
  `linha_cd` int(11) NOT NULL,
  PRIMARY KEY (`mpce_id`,`linha_cd`),
  KEY `linha_cd` (`linha_cd`),
  CONSTRAINT `mpce_linha_esforco_ibfk_1` FOREIGN KEY (`mpce_id`) REFERENCES `mpce` (`id`),
  CONSTRAINT `mpce_linha_esforco_ibfk_2` FOREIGN KEY (`linha_cd`) REFERENCES `linha_esforco` (`cd_linha`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.mpce_publico_alvo
CREATE TABLE IF NOT EXISTS `mpce_publico_alvo` (
  `mpce_id` int(11) NOT NULL,
  `publico_alvo_cd` int(11) NOT NULL,
  `publico_segmentado` text,
  PRIMARY KEY (`mpce_id`,`publico_alvo_cd`),
  KEY `publico_alvo_cd` (`publico_alvo_cd`),
  CONSTRAINT `mpce_publico_alvo_ibfk_1` FOREIGN KEY (`mpce_id`) REFERENCES `mpce` (`id`) ON DELETE CASCADE,
  CONSTRAINT `mpce_publico_alvo_ibfk_2` FOREIGN KEY (`publico_alvo_cd`) REFERENCES `publico_alvo` (`cd_publico`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.orgao
CREATE TABLE IF NOT EXISTS `orgao` (
  `codigo` int(9) NOT NULL COMMENT 'CODOM do Orgão',
  `nome` varchar(70) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `sigla` varchar(30) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `nivel_subordinacao` varchar(4) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `rm_cod` int(2) NOT NULL,
  `orgao_codigo_subordinada` int(9) DEFAULT NULL,
  `rede_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`codigo`),
  KEY `fk_orgao_subordinada` (`orgao_codigo_subordinada`),
  KEY `fk_orgao_rede` (`rede_id`),
  CONSTRAINT `FK_orgao_orgao` FOREIGN KEY (`orgao_codigo_subordinada`) REFERENCES `orgao` (`codigo`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_orgao_rede` FOREIGN KEY (`rede_id`) REFERENCES `rede` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.postograd
CREATE TABLE IF NOT EXISTS `postograd` (
  `cd_postograd` int(11) NOT NULL,
  `sg_postograd` varchar(10) NOT NULL,
  `nm_postograd` varchar(45) NOT NULL,
  `cd_forca` int(11) NOT NULL DEFAULT '1',
  `circulo_cd_circulo` int(11) NOT NULL DEFAULT '1',
  `cd_e1` int(11) NOT NULL DEFAULT '1',
  PRIMARY KEY (`cd_postograd`),
  KEY `fk_postograd_forca1_idx` (`cd_forca`),
  KEY `fk_postograd_circulo1_idx` (`circulo_cd_circulo`),
  CONSTRAINT `fk_postograd_circulo1` FOREIGN KEY (`circulo_cd_circulo`) REFERENCES `circulo` (`cd_circulo`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_postograd_forca1` FOREIGN KEY (`cd_forca`) REFERENCES `forca` (`cd_forca`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.produto
CREATE TABLE IF NOT EXISTS `produto` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mpce_id` int(11) NOT NULL,
  `descricao` text NOT NULL,
  `link` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_produto_mpce` (`mpce_id`),
  CONSTRAINT `FK_produto_mpce` FOREIGN KEY (`mpce_id`) REFERENCES `mpce` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1123 DEFAULT CHARSET=utf8;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.publico_alvo
CREATE TABLE IF NOT EXISTS `publico_alvo` (
  `cd_publico` int(11) NOT NULL AUTO_INCREMENT,
  `nm_publico` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`cd_publico`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.rede
CREATE TABLE IF NOT EXISTS `rede` (
  `id` int(11) NOT NULL,
  `nome` char(2) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.resultado
CREATE TABLE IF NOT EXISTS `resultado` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mpce_id` int(11) NOT NULL,
  `descricao` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_resultado_mpce` (`mpce_id`),
  CONSTRAINT `FK_resultado_mpce` FOREIGN KEY (`mpce_id`) REFERENCES `mpce` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=891 DEFAULT CHARSET=utf8;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.tipo_avaliacao
CREATE TABLE IF NOT EXISTS `tipo_avaliacao` (
  `cd_avaliacao` int(11) NOT NULL AUTO_INCREMENT,
  `nm_avaliacao` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`cd_avaliacao`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.tipo_usuario
CREATE TABLE IF NOT EXISTS `tipo_usuario` (
  `cd_tipo` int(11) NOT NULL AUTO_INCREMENT,
  `descricao` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`cd_tipo`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.uf
CREATE TABLE IF NOT EXISTS `uf` (
  `cd_uf` bigint(20) NOT NULL AUTO_INCREMENT,
  `sg_uf` varchar(2) NOT NULL,
  `nm_uf` varchar(60) NOT NULL,
  `cd_pais` int(11) NOT NULL DEFAULT '1',
  PRIMARY KEY (`cd_uf`),
  UNIQUE KEY `sg_uf_UNIQUE` (`sg_uf`),
  KEY `fk_uf_pais1_idx` (`cd_pais`),
  CONSTRAINT `fk_uf_pais1` FOREIGN KEY (`cd_pais`) REFERENCES `pais` (`cd_pais`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela plano_estrategico.usuario
CREATE TABLE IF NOT EXISTS `usuario` (
  `cd_usuario` int(11) NOT NULL AUTO_INCREMENT,
  `tipo_usuario` int(11) DEFAULT NULL,
  `nome` varchar(50) DEFAULT NULL,
  `senha` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`cd_usuario`),
  KEY `FK_tipo_usuario_usuario` (`tipo_usuario`),
  CONSTRAINT `FK_tipo_usuario_usuario` FOREIGN KEY (`tipo_usuario`) REFERENCES `tipo_usuario` (`cd_tipo`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para trigger plano_estrategico.fidece_excluido
SET @OLDTMP_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO';
DELIMITER //
CREATE TRIGGER `plano_estrategico`.`fidece_excluido` BEFORE DELETE ON `fidece` FOR EACH ROW BEGIN

	INSERT INTO log_audit 
	SET log_audit.id_tabela = 2,
	log_audit.id_usuario = OLD.id_usuario,
	log_audit.data = CURRENT_TIMESTAMP(),
	log_audit.operacao = 'DELETE',
	log_audit.id_registro = OLD.id;
	

END//
DELIMITER ;
SET SQL_MODE=@OLDTMP_SQL_MODE;

-- Copiando estrutura para trigger plano_estrategico.mpce_alterado
SET @OLDTMP_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO';
DELIMITER //
CREATE TRIGGER `plano_estrategico`.`mpce_alterado` AFTER UPDATE ON `mpce` FOR EACH ROW BEGIN


	if NEW.arquivado = 0 then

		INSERT INTO log_audit 
		SET log_audit.id_tabela = 1,
		log_audit.id_usuario = NEW.id_usuario,
		log_audit.data = CURRENT_TIMESTAMP(),
		log_audit.operacao = 'UPDATE',
		log_audit.id_registro = NEW.id;
		
	ELSE 
	
		INSERT INTO log_audit 
		SET log_audit.id_tabela = 1,
		log_audit.id_usuario = NEW.id_usuario,
		log_audit.data = CURRENT_TIMESTAMP(),
		log_audit.operacao = 'ARQUIVADO',
		log_audit.id_registro = NEW.id;
		
	END if;
	
END//
DELIMITER ;
SET SQL_MODE=@OLDTMP_SQL_MODE;

-- Copiando estrutura para trigger plano_estrategico.mpce_excluido
SET @OLDTMP_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO';
DELIMITER //
CREATE TRIGGER `plano_estrategico`.`mpce_excluido` BEFORE DELETE ON `mpce` FOR EACH ROW BEGIN

	INSERT INTO log_audit 
	SET log_audit.id_tabela = 1,
	log_audit.id_usuario = OLD.id_usuario,
	log_audit.data = CURRENT_TIMESTAMP(),
	log_audit.operacao = 'DELETE',
	log_audit.id_registro = OLD.id;
	

END//
DELIMITER ;
SET SQL_MODE=@OLDTMP_SQL_MODE;

-- Copiando estrutura para trigger plano_estrategico.mpce_inserido
SET @OLDTMP_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO';
DELIMITER //
CREATE TRIGGER `plano_estrategico`.`mpce_inserido` AFTER INSERT ON `mpce` FOR EACH ROW BEGIN

	INSERT INTO log_audit 
	SET log_audit.id_tabela = 1,
	log_audit.id_usuario = NEW.id_usuario,
	log_audit.data = CURRENT_TIMESTAMP(),
	log_audit.operacao = 'INSERT',
	log_audit.id_registro = NEW.id;
	

END//
DELIMITER ;
SET SQL_MODE=@OLDTMP_SQL_MODE;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
