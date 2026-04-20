# Documentação Técnica do Backend

## Sistema de Gestão de Usuários e Ramais

---

# 1. Introdução

Este documento descreve a arquitetura, implementação e funcionamento do backend de um sistema para gerenciamento de usuários e ramais institucionais. A aplicação foi desenvolvida utilizando o framework **FastAPI**, adotando princípios de APIs RESTful, autenticação baseada em tokens JWT (*JSON Web Tokens*) e persistência de dados via ORM.

O sistema permite o controle de acesso com base em perfis de usuários, garantindo segurança e integridade nas operações realizadas.

---

# 2. Tecnologias Utilizadas

O backend foi desenvolvido com as seguintes tecnologias e bibliotecas:

* **FastAPI** – framework web para construção de APIs de alto desempenho
* **Uvicorn** – servidor ASGI para execução da aplicação
* **SQLAlchemy** – ORM para manipulação do banco de dados
* **Passlib (bcrypt)** – hashing seguro de senhas
* **python-jose** – implementação de JWT para autenticação
* **python-dotenv** – gerenciamento de variáveis de ambiente

---

# 3. Configuração do Ambiente

## 3.1 Criação do ambiente virtual

```bash
python3 -m venv venv
```

## 3.2 Ativação do ambiente

* Linux/macOS:

```bash
source venv/bin/activate
```

* Windows:

```bash
venv\Scripts\activate
```

## 3.3 Instalação de dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

# 4. Variáveis de Ambiente

O sistema utiliza variáveis de ambiente para configuração sensível. Deve-se criar um arquivo `.env` com os seguintes parâmetros:

```env
DATABASE_URL=sqlite:///./database.db
SECRET_KEY=chave_secreta_segura
```

A chave secreta pode ser gerada por:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

# 5. Execução do Sistema

Antes da execução inicial, recomenda-se a criação de um usuário administrador:

```bash
python criar_user.py
```

Em seguida, o servidor pode ser iniciado com:

```bash
uvicorn main:app --reload
```

A aplicação ficará disponível em:

* API: [http://localhost:8000](http://localhost:8000)
* Documentação interativa: [http://localhost:8000/docs](http://localhost:8000/docs)

---

# 6. Arquitetura do Sistema

O sistema segue uma arquitetura monolítica simplificada, organizada em um único arquivo principal (`main.py`). Apesar de sua simplicidade, contempla os seguintes componentes:

## 6.1 Camada de Modelos (Persistência)

Implementada com SQLAlchemy, define as entidades do sistema:

* **Pessoa**: representa usuários autenticáveis
* **Ramal**: representa registros de ramais institucionais

## 6.2 Camada de Validação (Schemas)

Utiliza Pydantic para validação e normalização de dados de entrada, garantindo:

* consistência dos dados
* validação de senha mínima
* padronização de nomes de usuário

## 6.3 Camada de Autenticação

Baseada no protocolo OAuth2 com fluxo de senha (*password flow*) e uso de JWT.

São utilizados dois tipos de tokens:

* **Access Token**: curta duração (30 minutos)
* **Refresh Token**: longa duração (7 dias)

## 6.4 Camada de Segurança

Inclui:

* hashing de senhas com bcrypt
* validação de tokens JWT
* controle de acesso por tipo de usuário

---

# 7. Modelo de Dados

## 7.1 Entidade: Pessoa

| Atributo      | Tipo    | Descrição                |
| ------------- | ------- | ------------------------ |
| id            | Integer | Identificador único      |
| nome          | String  | Nome de usuário (único)  |
| senha_hash    | String  | Senha criptografada      |
| aotipousuario | String  | Perfil (admin ou padrão) |

---

## 7.2 Entidade: Ramal

| Atributo     | Tipo    | Descrição           |
| ------------ | ------- | ------------------- |
| id           | Integer | Identificador único |
| nome         | String  | Nome do responsável |
| departamento | String  | Departamento        |
| ramal        | String  | Número do ramal     |

---

# 8. Autenticação e Autorização

## 8.1 Processo de Login

O endpoint `/token` realiza autenticação do usuário e retorna tokens JWT.

## 8.2 Renovação de Token

O endpoint `/refresh` permite a obtenção de um novo access token a partir de um refresh token válido.

## 8.3 Controle de Acesso

O sistema implementa autorização baseada em papéis:

* **admin**:

  * acesso total ao sistema
* **padrao**:

  * acesso restrito à consulta

---

# 9. Endpoints da API

## 9.1 Usuário autenticado

* `GET /users/me`
  Retorna os dados do usuário logado

---

## 9.2 Gestão de Ramais

* `POST /pessoas/` – criação (admin)
* `GET /pessoas/` – listagem (autenticado)
* `PUT /pessoas/{id}` – atualização (admin)
* `DELETE /pessoas/{id}` – remoção (admin)

---

## 9.3 Gestão de Usuários

* `POST /usuarios/` – criação (admin)
* `GET /usuarios/` – listagem (admin)
* `PUT /usuarios/{id}` – atualização (admin)
* `DELETE /usuarios/{id}` – remoção (admin)

---

# 10. Regras de Negócio

O sistema implementa restrições importantes para garantir integridade:

* Um usuário não pode remover seu próprio privilégio de administrador
* O último administrador do sistema não pode ser removido
* Um usuário não pode excluir a si mesmo
* Nomes de usuário são normalizados para evitar duplicidade

---

# 11. Considerações de Segurança

As seguintes práticas foram adotadas:

* armazenamento seguro de senhas (hash bcrypt)
* uso de tokens JWT assinados
* validação de entrada de dados
* proteção de rotas via autenticação

---

# 12. Limitações e Trabalhos Futuros

Apesar de funcional, o sistema apresenta limitações estruturais:

## 12.1 Melhorias Arquiteturais

* modularização do código
* separação em camadas (controllers, services, repositories)

## 12.2 Banco de Dados

* substituição do SQLite por PostgreSQL
* uso de migrations com Alembic

## 12.3 Segurança

* implementação de rate limiting
* revogação de tokens
* auditoria de acessos

## 12.4 Testes

* criação de testes automatizados
* validação de endpoints críticos

---

# 13. Conclusão

O backend apresentado demonstra uma implementação consistente de uma API RESTful com autenticação segura e controle de acesso. A utilização de tecnologias modernas como FastAPI e JWT contribui para desempenho e escalabilidade, enquanto o uso de ORM e validação estruturada garante integridade dos dados.

A aplicação serve como base sólida para evolução para ambientes de produção, mediante adoção de melhorias arquiteturais e de segurança.