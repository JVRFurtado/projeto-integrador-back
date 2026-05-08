CREATE DATABASE IF NOT EXISTS db_ramais
DEFAULT CHARACTER SET utf8mb4
DEFAULT COLLATE utf8mb4_0900_ai_ci;
USE db_ramais;
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS ramal_depto;
DROP TABLE IF EXISTS ramal_pessoas;
DROP TABLE IF EXISTS pessoas;
DROP TABLE IF EXISTS ramais_telefonicos;
DROP TABLE IF EXISTS departamentos;
DROP TABLE IF EXISTS cargos;
SET FOREIGN_KEY_CHECKS = 1;
CREATE TABLE cargos (
idcargo INT UNSIGNED NOT NULL AUTO_INCREMENT,
txnome VARCHAR(100) NOT NULL,
dtcadcargo DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (idcargo),
UNIQUE KEY uk_cargos_txnome (txnome)
) ENGINE=InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;
CREATE TABLE departamentos (
iddepto INT UNSIGNED NOT NULL AUTO_INCREMENT,
txnomedepto VARCHAR(100) NOT NULL,
dtcaddepto DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (iddepto),
UNIQUE KEY uk_departamentos_txnomedepto (txnomedepto)
) ENGINE=InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;
CREATE TABLE ramais_telefonicos (
idramal INT UNSIGNED NOT NULL AUTO_INCREMENT,
nuramal VARCHAR(20) NOT NULL,
nuvoip VARCHAR(50) NULL,
dtedicao DATETIME NULL DEFAULT NULL,
dtcadramal DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (idramal),
UNIQUE KEY uk_ramais_telefonicos_nuramal (nuramal),
KEY idx_ramais_telefonicos_nuvoip (nuvoip)
) ENGINE=InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;
CREATE TABLE pessoas (
idpessoa INT UNSIGNED NOT NULL AUTO_INCREMENT,
txnome VARCHAR(100) NOT NULL,
txemail VARCHAR(150) NOT NULL,
txsenha VARCHAR(255) NOT NULL,
cargoid INT UNSIGNED NOT NULL,
deptoid INT UNSIGNED NOT NULL,
aotipousuario ENUM('admin', 'gestor', 'padrao') NOT NULL DEFAULT 'padrao',
dtcadpessoa DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
dtedicaopessoa DATETIME NULL DEFAULT NULL,
PRIMARY KEY (idpessoa),
UNIQUE KEY uk_pessoas_txemail (txemail),
KEY idx_pessoas_cargoid (cargoid),
KEY idx_pessoas_deptoid (deptoid),
KEY idx_pessoas_aotipousuario (aotipousuario),
CONSTRAINT fk_pessoas_cargo
FOREIGN KEY (cargoid) REFERENCES cargos (idcargo)
ON UPDATE CASCADE
ON DELETE RESTRICT,
CONSTRAINT fk_pessoas_departamento
FOREIGN KEY (deptoid) REFERENCES departamentos (iddepto)
ON UPDATE CASCADE
ON DELETE RESTRICT
) ENGINE=InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;
CREATE TABLE ramal_pessoas (
pessoaid INT UNSIGNED NOT NULL,
ramalid INT UNSIGNED NOT NULL,
dtcadramalpessoa DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (pessoaid, ramalid),
KEY idx_ramal_pessoas_ramalid (ramalid),
CONSTRAINT fk_ramal_pessoas_pessoa
FOREIGN KEY (pessoaid) REFERENCES pessoas (idpessoa)
ON UPDATE CASCADE
ON DELETE CASCADE,
CONSTRAINT fk_ramal_pessoas_ramal
FOREIGN KEY (ramalid) REFERENCES ramais_telefonicos (idramal)
ON UPDATE CASCADE
ON DELETE CASCADE
) ENGINE=InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;
CREATE TABLE ramal_depto (
deptoid INT UNSIGNED NOT NULL,
ramalid INT UNSIGNED NOT NULL,
dtcadramaldepto DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (deptoid, ramalid),
KEY idx_ramal_depto_ramalid (ramalid),
CONSTRAINT fk_ramal_depto_departamento
FOREIGN KEY (deptoid) REFERENCES departamentos (iddepto)
ON UPDATE CASCADE
ON DELETE CASCADE,
CONSTRAINT fk_ramal_depto_ramal
FOREIGN KEY (ramalid) REFERENCES ramais_telefonicos (idramal)
ON UPDATE CASCADE
ON DELETE CASCADE
) ENGINE=InnoDB
DEFAULT CHARSET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;