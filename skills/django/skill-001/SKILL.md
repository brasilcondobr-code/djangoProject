---
name: connected-users-module
slug: connected-users-module
version: 1.0.0
description: Implementa o módulo de usuários conectados do BrasilCondo.
category: django
---

A Skill foi dividida nas quatro etapas solicitadas: **Inspeção, Plano, Implementação e Validação**, preservando os requisitos técnicos, funcionais, arquiteturais, de segurança, testes e entregáveis do prompt original.

	```markdown
	---
	name: connected-users-module
	slug: connected-users-module
	version: 1.0.0
	description: >
	  Implementa e valida a atualização do módulo 06. Usuários Conectados
	  (connecteduser) no app system do projeto Brasil Condo, utilizando Django,
	  PostgreSQL, Django Admin, Jazzmin, Docker, Clean Architecture, DDD,
	  Service Layer, logging estruturado e testes automatizados.
	category: django
	tags:
	  - django
	  - python
	  - postgresql
	  - django-admin
	  - jazzmin
	  - docker
	  - celery
	  - rabbitmq
	  - flower
	  - ddd
	  - clean-architecture
	  - service-layer
	  - testing
	  - connected-users
	  - sessions
	  - security
	requires:
	  bins:
		- python3
		- docker
		- git
	  files:
		- manage.py
	  project:
		name: BrasilCondo
		app: system
		module: connecteduser
		module_title: "06. Usuários Conectados"
	execution:
	  mode: autonomous
	  approval_required_for:
		- destructive_database_operations
		- deleting_existing_files
		- changing_authentication
		- changing_permissions
		- changing_external_integrations
		- destructive_migrations
	  stop_on:
		- missing_project_context
		- authentication_flow_change_required
		- permission_change_required
		- destructive_migration_required
		- existing_architecture_conflict
	---
	```

# Skill: Atualização do módulo 06. Usuários Conectados

	## 1. Objetivo

		Atualizar o módulo:
			```text
			Projeto: BrasilCondo
			App: system
			Módulo: 06. Usuários Conectados
			Identificador: connecteduser
			```

		O módulo deverá apresentar, em modo **somente leitura**, os usuários atualmente conectados ao sistema Brasil Condo.

		A funcionalidade deverá acompanhar os acessos ativos em tempo real, sem exibir:
			- usuários que não estejam efetivamente conectados;
			- usuários com sessão expirada;
			- usuários inativos;
			- usuários cuja última atividade esteja fora do tempo configurado.

		A implementação deverá preservar o funcionamento existente do sistema, incluindo autenticação, autorização, Moodle, Brasil Condo e demais aplicações integradas.

---

# Regras gerais de execução

	O agente Hermes deverá:
		1. Trabalhar exclusivamente dentro do escopo do módulo `connecteduser`.
		2. Inspecionar primeiro a estrutura existente do projeto.
		3. Identificar padrões já utilizados pelo projeto antes de criar novos componentes.
		4. Não criar uma arquitetura paralela caso já exista uma arquitetura consolidada.
		5. Não alterar o mecanismo atual de autenticação.
		6. Não alterar o sistema geral de autorização.
		7. Não conceder permissões automaticamente.
		8. Não fazer refatorações fora do escopo.
		9. Não remover dados existentes.
		10. Não realizar migrations destrutivas sem aprovação explícita.
		11. Não expor senhas, tokens, cookies ou session keys completas.
		12. Não utilizar memória local do processo como fonte oficial de usuários conectados.
		13. Utilizar PostgreSQL ou outro mecanismo compartilhado já compatível com a arquitetura atual.
		14. Manter compatibilidade com múltiplos workers e múltiplos containers.
		15. Priorizar mudanças pequenas, auditáveis, reversíveis e testáveis.
		16. Usar PEP 8, Clean Code, SRP e Separation of Concerns.
		17. Registrar decisões técnicas relevantes.
		18. Ao encontrar conflito entre o prompt e a estrutura existente, adaptar a implementação sem quebrar os padrões do projeto.
		19. Se uma decisão exigir alteração de autenticação, permissões ou dados críticos, interromper a execução e solicitar aprovação.

---

# Stack tecnológica obrigatória

	A solução deverá utilizar ou permanecer compatível com:
		- Django;
		- Python;
		- PostgreSQL;
		- Django Admin;
		- Jazzmin;
		- Docker;
		- Celery;
		- RabbitMQ;
		- Flower;
		- DDD;
		- Service Layer;
		- Clean Architecture;
		- PEP 8;
		- logging estruturado;
		- testes automatizados.

	Celery, RabbitMQ e Flower devem permanecer preparados para integrações futuras, mas não devem ser introduzidos como dependência obrigatória para a consulta em tempo real caso isso não seja necessário.

---

# Princípios obrigatórios

	A implementação deverá respeitar:
		- SRP — Single Responsibility Principle;
		- Separation of Concerns;
		- Clean Code;
		- Design Patterns;
		- Fail Fast;
		- validações defensivas;
		- auditabilidade;
		- segurança no desenvolvimento;
		- otimização de consultas;
		- logging estruturado;
		- refatoração apenas dentro do escopo;
		- compatibilidade com filas assíncronas futuras;
		- escalabilidade para integração com providers externos;
		- facilidade de debugging;
		- facilidade de correção de erros;
		- compatibilidade com PostgreSQL;
		- compatibilidade com Docker;
		- preservação da autenticação e autorização atuais.

---

# Etapa 1 — Inspeção

	## 1.1 Objetivo da etapa

		Antes de alterar qualquer arquivo, inspecionar o projeto Brasil Condo para compreender:
			- estrutura dos apps;
			- app `system`;
			- módulo `connecteduser`;
			- model atual;
			- mecanismo de autenticação;
			- mecanismo de sessão;
			- permissões;
			- configuração do Django Admin;
			- configuração do Jazzmin;
			- padrão de templates;
			- padrão de JavaScript;
			- padrão de testes;
			- configuração de Docker;
			- configuração de PostgreSQL;
			- configuração de Celery;
			- configuração de RabbitMQ;
			- configuração de Flower;
			- arquitetura existente;
			- convenções de nomes;
			- padrão de logging;
			- padrão de serviços, selectors e repositories.

	## 1.2 Verificações obrigatórias

		Localizar e analisar, quando existirem:
			```text
			manage.py
			settings.py
			urls.py
			models.py
			admin.py
			forms.py
			views.py
			middleware.py
			signals.py
			tasks.py
			services/
			repositories/
			selectors/
			templates/
			static/
			tests/
			Dockerfile
			docker-compose.yml
			compose.yaml
			requirements.txt
			pyproject.toml
			pytest.ini
			```

		Inspecionar especificamente:
			- model atual `connecteduser`;
			- relacionamento com o model de usuário;
			- existência de registros de conexão;
			- existência de controle por sessão;
			- uso de `django.contrib.sessions`;
			- uso de middleware de autenticação;
			- uso de `request.user`;
			- uso de `request.session.session_key`;
			- sistema atual de logout;
			- classes de permissão;
			- permissões do Django Admin;
			- menus do Jazzmin;
			- páginas administrativas similares;
			- endpoints JSON existentes;
			- mecanismos de polling ou heartbeat existentes;
			- padrões de paginação;
			- filtros e buscas já implementados;
			- padrões de tratamento de erros;
			- padrões de logging estruturado;
			- configuração de timezone;
			- existência de custom user model;
			- existência de múltiplos bancos ou providers;
			- existência de cache compartilhado, Redis ou outro backend distribuído.

	## 1.3 Comandos de inspeção

		Executar, conforme a estrutura do projeto:
			```bash
			pwd
			find . -maxdepth 3 -type f | sort
			find . -path "*/system/*" -type f | sort
			find . -iname "*connecteduser*" -o -iname "*connected_user*"
			python manage.py check
			python manage.py showmigrations
			```

		Se o projeto usar Docker, também avaliar:
			```bash
			docker compose ps
			docker compose config
			```

		Não iniciar serviços ou executar comandos destrutivos sem necessidade.

	## 1.4 Inspeção do model atual

		Avaliar se o model existente de `connecteduser` possui informações suficientes para controlar conexões.

		Verificar a existência ou necessidade dos seguintes dados:
			```text
			user
			session_key
			connected_at
			last_activity
			disconnected_at
			is_connected
			ip_address
			user_agent
			created_at
			updated_at
			```

		Não criar outro model de usuário.

		Utilizar o relacionamento com o model de usuário existente.

		Não duplicar campos que já estejam disponíveis no usuário, incluindo:
			```text
			username
			email
			is_active
			is_staff
			last_login
			groups
			```

		Avaliar se o projeto deve utilizar:
			```text
			um registro por sessão
			```

		ou:
			```text
			um registro por usuário conectado
			```

		A recomendação padrão é utilizar **um registro por sessão**, pois o mesmo usuário pode estar conectado simultaneamente por:
			```text
			Usuário A — navegador Chrome
			Usuário A — aplicativo mobile
			Usuário A — navegador Firefox
			```

	## 1.5 Inspeção da arquitetura

		Identificar se o projeto já utiliza:
			```text
			Presentation Layer
			Application Layer
			Domain Layer
			Infrastructure Layer
			```

		A estrutura sugerida, caso seja compatível com o projeto, é:
			```text
			system/
			├── models.py
			├── admin.py
			├── forms.py
			├── views.py
			├── urls.py
			├── services/
			│   └── connected_user_service.py
			├── repositories/
			│   └── connected_user_repository.py
			├── selectors/
			│   └── connected_user_selectors.py
			├── middleware/
			│   └── connected_user_middleware.py
			├── templates/
			│   └── system/
			│       └── connecteduser/
			├── static/
			│   └── system/
			│       └── connecteduser/
			│           └── connecteduser.js
			├── migrations/
			└── tests/
			```

		Essa estrutura é apenas uma referência. Adaptar à estrutura já existente.

	## 1.6 Inspeção de segurança

		Verificar:
			- como a autenticação é aplicada;
			- como as permissões são verificadas;
			- quais usuários podem acessar o módulo;
			- se o e-mail pode ser exibido para o usuário atual;
			- se os grupos podem ser exibidos para o usuário atual;
			- como o CSRF é aplicado;
			- como os endpoints JSON exigem autenticação;
			- se existem mecanismos de sanitização;
			- se os templates utilizam escape automático;
			- se há risco de XSS;
			- se há exposição de session keys;
			- se existem dados sujeitos à LGPD.

		Não alterar permissões existentes.

	## 1.7 Saída obrigatória da etapa

		Ao final da inspeção, criar um relatório ou registrar no resumo da execução contendo:
			```text
			- estrutura identificada;
			- model atual encontrado;
			- campos já existentes;
			- campos ausentes;
			- arquitetura utilizada;
			- mecanismo de autenticação;
			- mecanismo de sessão;
			- permissões aplicáveis;
			- padrões de Admin/Jazzmin;
			- padrões de testes;
			- padrões de logging;
			- necessidade ou não de migration;
			- riscos identificados;
			- decisões que precisam ser tomadas;
			```

		Antes de continuar, confirmar que a implementação pode ser realizada sem modificar indevidamente autenticação, autorização ou integrações externas.

---

# Etapa 2 — Plano

	## 2.1 Objetivo da etapa

		Criar um plano técnico detalhado, baseado na inspeção real do projeto.

		O plano deverá definir:
			- modelo de dados;
			- regra de conexão;
			- controle de atividade;
			- service layer;
			- repository ou selector;
			- middleware ou heartbeat;
			- views;
			- URLs;
			- templates;
			- JavaScript;
			- Admin;
			- Jazzmin;
			- filtros;
			- paginação;
			- logging;
			- testes;
			- migrations;
			- documentação;
			- validação final.

	## 2.2 Regra funcional de usuário conectado

		Não utilizar exclusivamente `last_login` para determinar se o usuário está online.

		`last_login` representa o último login registrado, mas não comprova que o usuário ainda está conectado.

		A regra deverá ser equivalente a:
			```text
			sessão válida
			E usuário autenticado
			E usuário ativo
			E is_connected = true
			E last_activity >= limite de expiração
			```

		Conceitualmente:
			```text
			is_connected = true
			AND last_activity >= limite_de_expiração
			AND user.is_active = true
			```

		O tempo de expiração deverá ser configurável:
			```text
			CONNECTED_USER_TIMEOUT = 5 minutos
			```

		Esse valor não pode ficar fixado diretamente no código.

		O intervalo de atualização da atividade também deverá ser configurável:
			```text
			ACTIVITY_UPDATE_INTERVAL = 60 segundos
			```

		O intervalo de atualização da interface deverá ser configurável, preferencialmente entre:
			```text
			30 e 60 segundos
			```

	## 2.3 Decisão sobre registro por sessão

		Preferir um registro por sessão.

		O registro deverá relacionar:
			```text
			Usuário
			Sessão
			Data/hora de conexão
			Data/hora da última atividade
			Data/hora do último login
			Status da conexão
			Endereço IP, se permitido
			User-Agent, opcionalmente
			Data de criação
			Data de atualização
			Data de desconexão
			```

		Evitar registros duplicados para a mesma sessão.

		Utilizar `UniqueConstraint` quando aplicável.

		Utilizar índices em campos consultados frequentemente:
			```text
			user
			session_key
			last_activity
			is_connected
			```

		Utilizar `related_name` claro e compatível com o projeto.

	## 2.4 Plano de atividade

		O controle de atividade deverá:
			- não alterar o fluxo atual de autenticação;
			- registrar atividade em requisições autenticadas;
			- evitar gravação a cada requisição;
			- atualizar `last_activity` somente após o intervalo configurado;
			- usar operações atômicas quando necessário;
			- evitar condições de corrida;
			- não bloquear a requisição principal com operações desnecessárias;
			- funcionar em múltiplos workers;
			- funcionar em múltiplos containers;
			- não usar memória local como fonte oficial;
			- utilizar PostgreSQL ou mecanismo compartilhado compatível.

		Avaliar a melhor alternativa entre:
			- middleware específico;
			- service layer;
			- signal, somente se já houver padrão equivalente;
			- endpoint de heartbeat;
			- atualização em requisições autenticadas;
			- tarefa assíncrona futura com Celery.

		Se as páginas do sistema realizarem poucas requisições, considerar o endpoint:
			```text
			POST /system/connected-users/heartbeat/
			```

		Esse endpoint deverá atualizar somente a atividade da sessão atual.

	## 2.5 Plano do Service Layer

		Criar ou atualizar um serviço específico para a regra de usuários conectados.

		As responsabilidades esperadas incluem:
			```text
			register_connection()
			update_activity()
			mark_session_disconnected()
			expire_inactive_sessions()
			get_connected_users()
			cleanup_stale_sessions()
			```

		O service layer deverá:
			- centralizar as regras de negócio;
			- validar os dados recebidos;
			- evitar lógica duplicada em views, forms e templates;
			- utilizar transações quando necessário;
			- tratar falhas de persistência;
			- fornecer mensagens de erro consistentes;
			- facilitar testes unitários;
			- permitir futura execução assíncrona;
			- ser idempotente quando aplicável.

		A view não deverá conter regras complexas de conexão.

	## 2.6 Plano de consulta

		A consulta deverá:
			- filtrar somente sessões ativas;
			- ignorar sessões expiradas;
			- filtrar usuários ativos;
			- utilizar `select_related` para o usuário;
			- utilizar `prefetch_related` para grupos;
			- evitar N+1 queries;
			- ordenar por `last_activity` ou `last_login`;
			- retornar somente os campos necessários quando possível;
			- utilizar índices adequados;
			- suportar busca por usuário e e-mail;
			- suportar filtro por grupo;
			- suportar filtro por membro da equipe;
			- suportar filtro por status de atividade;
			- suportar paginação.

		Os grupos deverão ser apresentados sem uma consulta individual para cada usuário.

	## 2.7 Plano da interface

		A interface deverá ser:
			- somente leitura;
			- compatível com Jazzmin;
			- responsiva;
			- paginada;
			- ordenável;
			- pesquisável;
			- segura;
			- compatível com os padrões visuais existentes.

		Campos obrigatórios:
			```text
			Usuário
			Endereço de E-mail
			Grupos
			Ativo
			Membro da equipe
			Último login
			```

		A interface deverá possuir:
			- busca por usuário e e-mail;
			- placeholder de busca:
				```text
				Pesquisar usuário ou e-mail...
				```
			- filtro por grupo;
			- filtro por membro da equipe;
			- filtro por status de atividade;
			- indicação visual de usuário conectado;
			- estado vazio;
			- mensagens de carregamento;
			- mensagens de erro amigáveis;
			- exibição clara de data e hora;
			- horário da última atualização;
			- atualização periódica;
			- tratamento de falhas da atualização em tempo real.

		Não utilizar:
			- máscaras de entrada nos dados exibidos;
			- placeholders em campos não editáveis;
			- campos editáveis para os dados apresentados;
			- HTML fornecido pelo usuário;
			- renderização insegura de nomes, e-mails ou grupos.

	## 2.8 Plano de atualização em tempo real

		Utilizar AJAX ou Fetch API.

		Não implementar WebSocket nesta etapa, salvo se o projeto já possuir infraestrutura pronta.

		A atualização deverá:
			- consultar somente usuários conectados;
			- atualizar a tabela sem recarregar toda a página;
			- preservar filtros quando possível;
			- preservar paginação quando possível;
			- exibir o horário da última atualização;
			- impedir requisições simultâneas;
			- pausar ou reduzir a frequência quando a aba estiver inativa;
			- tratar HTTP 401;
			- tratar HTTP 403;
			- tratar HTTP 404;
			- tratar HTTP 500;
			- cancelar requisições anteriores quando necessário;
			- evitar vazamento de timers;
			- evitar vazamento de listeners;
			- tratar respostas inválidas;
			- tratar respostas vazias.

	## 2.9 Plano do Admin e Jazzmin

		O Django Admin deverá:
			- exibir os campos obrigatórios;
			- permitir somente visualização;
			- impedir criação;
			- impedir alteração;
			- impedir exclusão;
			- utilizar `list_display`;
			- utilizar `list_filter`;
			- utilizar `search_fields`;
			- utilizar `ordering`;
			- utilizar `readonly_fields`;
			- evitar N+1 queries;
			- respeitar as permissões existentes;
			- manter compatibilidade com Jazzmin;
			- não conceder novas permissões;
			- não alterar o sistema geral de autenticação ou autorização.

		Se houver `ModelForm`, avaliar se ele ainda é necessário.

		Caso seja mantido:
			- impedir criação;
			- impedir alteração;
			- impedir exclusão;
			- utilizar campos desabilitados;
			- manter `help_text`;
			- manter mensagens de erro;
			- validar no backend;
			- não confiar apenas no atributo `disabled` do HTML;
			- impedir alterações por requisições manipuladas manualmente.

	## 2.10 Plano de URLs e views

		Considerar as rotas:
			```text
			/system/connected-users/
			/system/connected-users/data/
			/system/connected-users/heartbeat/
			```

		A rota de listagem deverá:
			- exigir autenticação;
			- respeitar permissões atuais;
			- renderizar somente usuários conectados;
			- suportar filtros;
			- suportar paginação;
			- suportar ordenação;
			- exibir somente dados autorizados.

		A rota de dados deverá:
			- exigir autenticação;
			- respeitar permissões atuais;
			- retornar somente usuários conectados;
			- retornar JSON estruturado;
			- utilizar status HTTP apropriados;
			- não expor informações sensíveis;
			- possuir proteção CSRF quando aplicável;
			- ser somente leitura;
			- não permitir alteração de dados.

		A view deverá delegar a busca para selector, repository ou service.

	## 2.11 Plano de Celery, RabbitMQ e Flower

		A primeira implementação não deverá depender obrigatoriamente de Celery para exibir a listagem.

		Preparar a solução para futuras tarefas como:
			```text
			limpeza de sessões expiradas
			remoção de registros antigos
			reconciliação de sessões
			auditoria de conexões
			métricas de usuários ativos
			```

		Considerar futuramente a tarefa:
			```text
			cleanup_stale_connected_users()
			```

		Essa tarefa deverá ser:
			- idempotente;
			- segura para execução repetida;
			- compatível com Celery;
			- compatível com RabbitMQ;
			- observável no Flower.

		Não criar dependência desnecessária de RabbitMQ ou Celery para uma operação resolvida por consulta e atualização normal.

	## 2.12 Plano de logging

		Implementar logging estruturado para os eventos:
			```text
			connected_user_registered
			connected_user_activity_updated
			connected_user_session_expired
			connected_user_cleanup_executed
			connected_user_query_failed
			```

		Os logs poderão conter:
			```text
			event
			timestamp
			user_id
			request_id
			session_id_hash
			duration_ms
			status
			error_type
			```

		Nunca registrar:
			- senhas;
			- tokens;
			- cookies;
			- session keys completas;
			- dados sensíveis desnecessários.

		Quando necessário, mascarar ou aplicar hash aos identificadores de sessão.

	## 2.13 Plano de segurança

		A implementação deverá:
			- preservar o sistema atual de autenticação;
			- respeitar as permissões atuais;
			- exigir usuário autenticado;
			- validar permissões no backend;
			- não confiar em validações JavaScript;
			- proteger endpoints;
			- evitar exposição de dados sensíveis;
			- aplicar escape de saída;
			- evitar SQL Injection utilizando ORM;
			- evitar XSS;
			- evitar CSRF;
			- evitar enumeração indevida de usuários;
			- não expor sessões completas;
			- respeitar a LGPD.

		O e-mail e os grupos somente poderão ser exibidos para usuários autorizados conforme as regras atuais do sistema.

	## 2.14 Plano de migrations

		Criar migrations somente quando necessário.

		As migrations deverão ser:
			- reversíveis;
			- descritivas;
			- compatíveis com PostgreSQL;
			- compatíveis com Docker;
			- preservadoras de dados;
			- não destrutivas;
			- independentes de dados inexistentes;
			- responsáveis por criar índices necessários;
			- responsáveis por criar constraints adequadas.

	## 2.15 Plano de testes

		Planejar testes para:

			### Model
				- criação de registro de conexão;
				- unicidade por sessão;
				- atualização de atividade;
				- expiração de sessão;
				- constraints;
				- índices;
				- relacionamentos.

			### Services
				- registro de conexão;
				- atualização idempotente;
				- expiração de conexões;
				- listagem de usuários conectados;
				- usuário inativo;
				- sessão inexistente;
				- falha no banco.

			### Views
				- usuário autenticado;
				- usuário não autenticado;
				- usuário sem permissão;
				- resposta JSON;
				- filtros;
				- paginação;
				- ausência de usuários conectados;
				- erros controlados.

			### Admin
				- acesso somente leitura;
				- bloqueio de criação;
				- bloqueio de edição;
				- bloqueio de exclusão;
				- filtros;
				- busca;
				- ausência de N+1 queries.

			### JavaScript
				- atualização periódica;
				- tratamento de erro;
				- resposta vazia;
				- resposta inválida;
				- status HTTP;
				- preservação dos filtros;
				- prevenção de requisições simultâneas;
				- pausa quando a aba estiver inativa.

	## 2.16 Saída obrigatória da etapa

		Produzir um plano contendo:
			```text
			- arquivos que serão alterados;
			- arquivos que serão criados;
			- arquivos que não devem ser alterados;
			- model e migration planejados;
			- estratégia de sessão;
			- estratégia de atividade;
			- estratégia de consulta;
			- estratégia de permissões;
			- estratégia de Admin/Jazzmin;
			- estratégia de frontend;
			- estratégia de logging;
			- estratégia de testes;
			- estratégia de rollback;
			- riscos;
			- critérios de aceite;
			```

		Não iniciar a implementação sem concluir o plano.

---

# Etapa 3 — Implementação

	## 3.1 Objetivo da etapa

		Implementar o plano aprovado respeitando a arquitetura e os padrões existentes no projeto.

		A implementação deverá ser incremental, testável e limitada ao módulo `connecteduser`.

	## 3.2 Model

		Avaliar novamente o model atual antes de modificá-lo.

		Se forem necessários novos campos, adicionar somente os campos indispensáveis, preservando compatibilidade.

		Campos possíveis:
			```text
			user
			session_key
			connected_at
			last_activity
			disconnected_at
			is_connected
			ip_address
			user_agent
			created_at
			updated_at
			```

		Regras:
			- utilizar o model de usuário existente;
			- não criar outro model de usuário;
			- não duplicar campos do usuário;
			- utilizar `related_name` claro;
			- configurar índices;
			- configurar constraints;
			- impedir duplicidade por sessão;
			- utilizar `UniqueConstraint` quando aplicável;
			- preservar dados existentes;
			- respeitar PostgreSQL;
			- manter compatibilidade com múltiplos containers.

		A fonte oficial de presença deverá ser persistente e compartilhada.

		Não utilizar memória local do processo.

	## 3.3 Migrations

		Criar migrations somente se realmente necessário.

		Executar:
			```bash
			python manage.py makemigrations
			python manage.py migrate
			```

		As migrations deverão:
			- possuir nomes descritivos;
			- ser reversíveis;
			- não apagar informações sem justificativa;
			- não depender de dados inexistentes;
			- criar índices;
			- criar constraints;
			- funcionar dentro do Docker;
			- funcionar no PostgreSQL.

		Não executar operações destrutivas automaticamente.

	## 3.4 Repository e selectors

		Criar ou atualizar repository e/ou selector conforme o padrão existente.

		A consulta deverá utilizar:
			```python
			select_related(...)
			prefetch_related(...)
			```

		quando aplicável.

		A consulta deverá:
			- filtrar `is_connected=True`;
			- filtrar `last_activity` dentro do limite;
			- filtrar `user.is_active=True`;
			- excluir sessões inválidas;
			- ordenar por `last_activity` ou `last_login`;
			- evitar N+1 queries;
			- suportar filtros;
			- suportar paginação;
			- suportar busca;
			- utilizar índices;
			- retornar somente dados necessários quando possível.

		Não colocar regra complexa de negócio no template.

	## 3.5 Service Layer

		Criar ou atualizar:
			```text
			register_connection()
			update_activity()
			mark_session_disconnected()
			expire_inactive_sessions()
			get_connected_users()
			cleanup_stale_sessions()
			```

		O serviço deverá:
			- validar dados;
			- centralizar regras;
			- ser idempotente quando aplicável;
			- utilizar transações quando necessário;
			- tratar falhas de persistência;
			- evitar condições de corrida;
			- realizar atualizações atômicas;
			- evitar duplicidade;
			- evitar escrita excessiva;
			- facilitar testes;
			- emitir logs estruturados;
			- não expor dados sensíveis.

	## 3.6 Middleware ou mecanismo de atividade

		Implementar o mecanismo mais compatível com o projeto:
			- middleware;
			- service;
			- heartbeat;
			- signal, somente se já houver padrão;
			- combinação de middleware e heartbeat;
			- tarefa futura.

		O mecanismo deverá:
			- registrar conexões autenticadas;
			- utilizar a sessão atual;
			- atualizar `last_activity`;
			- respeitar `ACTIVITY_UPDATE_INTERVAL`;
			- não escrever em todas as requisições;
			- não alterar o fluxo de autenticação;
			- não bloquear desnecessariamente as requisições;
			- operar com múltiplos workers;
			- operar com múltiplos containers;
			- não registrar dados sensíveis.

		Quando necessário, implementar:
			```text
			POST /system/connected-users/heartbeat/
			```

		Esse endpoint deverá atualizar apenas a atividade da sessão atual.

	## 3.7 Views e URLs

		Criar ou atualizar as rotas:
			```text
			/system/connected-users/
			/system/connected-users/data/
			/system/connected-users/heartbeat/
			```

		Implementar:
			- autenticação obrigatória;
			- validação de permissões;
			- respostas HTTP adequadas;
			- JSON estruturado;
			- paginação;
			- filtros;
			- ordenação;
			- busca;
			- tratamento de erros;
			- proteção CSRF quando aplicável;
			- ausência de mutação no endpoint de consulta.

		As views deverão delegar regras para service, selector ou repository.

	## 3.8 Template

		Criar ou atualizar o template compatível com Jazzmin.

		Exibir os campos:
			```text
			Usuário
			Endereço de E-mail
			Grupos
			Ativo
			Membro da equipe
			Último login
			```

		Implementar:
			- layout responsivo;
			- tabela somente leitura;
			- paginação;
			- ordenação;
			- busca por usuário e e-mail;
			- filtro por grupo;
			- filtro por membro da equipe;
			- filtro por status;
			- indicador visual de conexão;
			- estado vazio;
			- mensagens de carregamento;
			- mensagens de erro;
			- horário da última atualização;
			- escape dos valores;
			- proteção contra XSS.

		Utilizar o placeholder:
			```text
			Pesquisar usuário ou e-mail...
			```

		Não utilizar campos editáveis para os dados exibidos.

	## 3.9 JavaScript

		Implementar atualização periódica usando AJAX ou Fetch API.

		O JavaScript deverá:
			- consultar o endpoint de dados;
			- atualizar a tabela sem recarregar a página;
			- preservar filtros quando possível;
			- preservar paginação quando possível;
			- evitar requisições simultâneas;
			- cancelar requisições anteriores quando necessário;
			- pausar ou reduzir a frequência com a aba inativa;
			- tratar HTTP 401;
			- tratar HTTP 403;
			- tratar HTTP 404;
			- tratar HTTP 500;
			- tratar resposta vazia;
			- tratar resposta inválida;
			- exibir mensagens amigáveis;
			- exibir o horário da última atualização;
			- liberar timers e listeners;
			- não inserir HTML inseguro;
			- escapar dados vindos do backend quando necessário.

		Não implementar WebSocket nesta etapa, salvo infraestrutura já existente.

	## 3.10 Forms

		Como a tela é somente leitura, não criar formulário CRUD tradicional.

		Se existir um `ModelForm`, avaliar se deve ser removido, mantido ou adaptado.

		Se mantido:
			- impedir criação;
			- impedir alteração;
			- impedir exclusão;
			- utilizar campos desabilitados;
			- manter `help_text`;
			- manter mensagens de erro;
			- validar no backend;
			- não aceitar alteração por requisições manipuladas;
			- não depender somente do HTML `disabled`.

		A segurança deverá ser aplicada no backend.

	## 3.11 Admin

		Atualizar o Django Admin para modo somente leitura.

		Configurar, conforme compatível:
			```text
			list_display
			list_filter
			search_fields
			ordering
			readonly_fields
			```

		Implementar bloqueios para:
			- criação;
			- alteração;
			- exclusão;
			- alteração de grupos;
			- alteração de permissões;
			- ativação;
			- desativação;
			- edição de `last_login`.

		Evitar N+1 queries no Admin.

		Manter compatibilidade com Jazzmin.

		Respeitar permissões existentes.

		Não conceder novas permissões automaticamente.

	## 3.12 Celery, RabbitMQ e Flower

		Não tornar Celery obrigatório para a exibição da listagem.

		Preparar uma futura tarefa idempotente:
			```text
			cleanup_stale_connected_users()
			```

		A futura tarefa poderá executar:
			- limpeza de sessões expiradas;
			- remoção de registros antigos;
			- reconciliação de sessões;
			- auditoria;
			- métricas de usuários ativos.

		Se houver implementação da tarefa nesta etapa, ela não deverá substituir a consulta normal nem criar dependência desnecessária.

	## 3.13 Logging

		Implementar logging estruturado para:
			```text
			connected_user_registered
			connected_user_activity_updated
			connected_user_session_expired
			connected_user_cleanup_executed
			connected_user_query_failed
			```

		Incluir, quando aplicável:
			```text
			event
			timestamp
			user_id
			request_id
			session_id_hash
			duration_ms
			status
			error_type
			```

		Nunca incluir:
			```text
			senha
			token
			cookie
			session_key completa
			dados sensíveis desnecessários
			```

		Aplicar hash ou máscara aos identificadores de sessão.

	## 3.14 Segurança

		Garantir:
			- autenticação;
			- autorização;
			- validação no backend;
			- proteção CSRF;
			- escape de saída;
			- ausência de SQL Injection;
			- ausência de XSS;
			- ausência de enumeração indevida;
			- ausência de exposição de sessões;
			- respeito à LGPD;
			- preservação do mecanismo de login;
			- preservação das permissões;
			- ausência de dados sensíveis em logs.

		O JavaScript não deverá ser considerado mecanismo de segurança.

	## 3.15 Testes

		Criar ou atualizar testes automatizados para todos os cenários planejados.

		Usar testes de quantidade de queries quando aplicável, incluindo verificações de ausência de N+1.

		Cobrir:

			### Model
				```text
				- criação de conexão;
				- unicidade de sessão;
				- atualização de atividade;
				- expiração;
				- constraints;
				- índices;
				- relacionamentos.
				```

			### Service
				```text
				- registro;
				- idempotência;
				- expiração;
				- consulta;
				- usuário inativo;
				- sessão inexistente;
				- falha de banco.
				```

			### Views
				```text
				- usuário autenticado;
				- usuário não autenticado;
				- usuário sem permissão;
				- JSON;
				- filtros;
				- paginação;
				- lista vazia;
				- erros.
				```

			### Admin
				```text
				- acesso somente leitura;
				- bloqueio de criação;
				- bloqueio de edição;
				- bloqueio de exclusão;
				- filtros;
				- busca;
				- ausência de N+1.
				```

			### JavaScript
				```text
				- polling;
				- erro;
				- resposta vazia;
				- resposta inválida;
				- HTTP 401;
				- HTTP 403;
				- HTTP 404;
				- HTTP 500;
				- preservação de filtros;
				- prevenção de concorrência.
				```

	## 3.16 Documentação

		Criar ou atualizar documentação contendo:
			- resumo técnico;
			- arquivos alterados;
			- modelo utilizado;
			- regra de usuário conectado;
			- configuração de timeout;
			- configuração de intervalo de atividade;
			- configuração do polling;
			- instruções de instalação;
			- instruções para Docker;
			- instruções para migrations;
			- instruções para execução de testes;
			- instruções para validação;
			- limitações atuais;
			- melhorias futuras.

	## 3.17 Melhorias futuras documentadas

		Documentar como melhorias futuras:
			1. Registro por sessão para múltiplos dispositivos.
			2. Filtros adicionais:
			   - data/hora de conexão;
			   - última atividade;
			   - IP mascarado;
			   - dispositivo;
			   - navegador;
			   - tempo conectado.
			3. Endpoint de heartbeat.
			4. WebSocket com Django Channels e Redis.
			5. Redis para cache ou sessões em múltiplos containers.
			6. Política de retenção, como remoção de registros desconectados há mais de 30 dias.
			7. Métricas:
			   - usuários conectados agora;
			   - pico de usuários simultâneos;
			   - tempo médio de sessão;
			   - acessos por condomínio;
			   - acessos por horário.
			8. Integração futura com Flower, Prometheus ou Grafana.
			9. Limpeza periódica via Celery.
			10. Nunca usar `last_login` como indicador isolado de presença.

---

# Etapa 4 — Validação

	## 4.1 Objetivo da etapa

		Validar que a implementação atende aos requisitos funcionais, técnicos, arquiteturais, de segurança e de desempenho.

		Nenhuma tarefa deverá ser considerada concluída apenas porque o código foi criado.

	## 4.2 Validação estrutural

		Confirmar a existência dos componentes necessários:
			```text
			- model atualizado, se necessário;
			- migration, se necessária;
			- service layer;
			- selector ou repository;
			- middleware ou mecanismo de atividade;
			- forms atualizados, quando aplicável;
			- admin;
			- configuração Jazzmin;
			- views;
			- URLs;
			- templates;
			- JavaScript;
			- testes;
			- documentação;
			- configurações necessárias.
			```

		Confirmar que os arquivos estão localizados nos padrões existentes do projeto.

	## 4.3 Validação do Django

		Executar:
			```bash
			python manage.py check
			```

		Quando aplicável, executar:
			```bash
			python manage.py makemigrations --check
			python manage.py showmigrations
			python manage.py migrate
			```

		Se existir validação de produção:
			```bash
			python manage.py check --deploy
			```

		Não ignorar erros ou warnings relevantes.

	## 4.4 Validação com Docker

		Executar, conforme o projeto:
			```bash
			docker compose config
			docker compose ps
			docker compose exec <servico-web> python manage.py check
			docker compose exec <servico-web> python manage.py migrate
			```

		Validar:
			- aplicação web;
			- PostgreSQL;
			- workers;
			- Celery;
			- RabbitMQ;
			- Flower;
			- rede entre containers;
			- variáveis de ambiente;
			- volume persistente;
			- migrations;
			- conexão com banco.

		Não alterar serviços não relacionados ao escopo.

	## 4.5 Validação funcional

		Confirmar que:
			1. O módulo `06. Usuários Conectados (connecteduser)` está acessível.
			2. A tela exibe:
			   - Usuário;
			   - Endereço de E-mail;
			   - Grupos;
			   - Ativo;
			   - Membro da equipe;
			   - Último login.
			3. Somente usuários conectados são exibidos.
			4. Sessões expiradas não são exibidas.
			5. Usuários inativos não são exibidos como conectados.
			6. `last_login` não é usado isoladamente.
			7. A atividade recente determina a presença.
			8. A lista é atualizada automaticamente.
			9. A tela é somente leitura.
			10. Não é possível criar registros pela interface.
			11. Não é possível alterar registros pela interface.
			12. Não é possível excluir registros pela interface.
			13. Não é possível alterar grupos.
			14. Não é possível alterar permissões.
			15. Não é possível ativar ou desativar usuários.
			16. Não é possível alterar `last_login`.
			17. O Admin funciona em modo somente leitura.
			18. Jazzmin permanece compatível.
			19. Busca funciona.
			20. Filtros funcionam.
			21. Paginação funciona.
			22. Ordenação funciona.
			23. Estado vazio funciona.
			24. Mensagens de erro funcionam.
			25. Atualização em tempo real funciona.
			26. Falhas HTTP são tratadas.
			27. O Moodle, Brasil Condo e demais aplicações não são afetados.

	## 4.6 Validação de sessões e atividade

		Testar pelo menos:
			- usuário autenticado com sessão válida;
			- usuário não autenticado;
			- sessão inexistente;
			- sessão expirada;
			- usuário ativo;
			- usuário inativo;
			- atividade dentro do timeout;
			- atividade fora do timeout;
			- múltiplas sessões do mesmo usuário;
			- múltiplos usuários no mesmo instante;
			- conexão em múltiplos workers;
			- conexão em múltiplos containers;
			- atualização idempotente;
			- encerramento de sessão;
			- ausência de requisições duplicadas;
			- ausência de gravação excessiva.

		Confirmar que a regra é equivalente a:
			```text
			sessão válida
			AND usuário autenticado
			AND usuário ativo
			AND is_connected = true
			AND last_activity >= limite configurado
			```

	## 4.7 Validação de consultas

		Confirmar:
			- uso de `select_related` para o usuário;
			- uso de `prefetch_related` para grupos;
			- ausência de N+1;
			- índices utilizados;
			- filtros aplicados no banco;
			- paginação aplicada corretamente;
			- ausência de consultas individuais para grupos;
			- ausência de dados desnecessários;
			- ordenação correta.

		Utilizar testes como:
			```python
			assertNumQueries(...)
			```

		ou mecanismo equivalente já utilizado no projeto.

	## 4.8 Validação do Admin

		Confirmar:
			- usuário autorizado consegue visualizar;
			- usuário não autenticado não consegue acessar;
			- usuário sem permissão não consegue acessar;
			- `has_add_permission()` bloqueia criação;
			- `has_change_permission()` bloqueia alteração;
			- `has_delete_permission()` bloqueia exclusão;
			- campos são somente leitura;
			- filtros funcionam;
			- busca funciona;
			- ordenação funciona;
			- não há N+1;
			- Jazzmin renderiza corretamente.

	## 4.9 Validação do frontend

		Confirmar:
			- tabela responsiva;
			- escape correto dos dados;
			- ausência de HTML inseguro;
			- estado vazio;
			- loading;
			- erro;
			- atualização periódica;
			- horário da última atualização;
			- filtros preservados;
			- paginação preservada quando possível;
			- uma única requisição ativa por vez;
			- cancelamento de requisição anterior;
			- pausa em aba inativa;
			- ausência de timers órfãos;
			- tratamento de 401, 403, 404 e 500;
			- resposta inválida tratada;
			- resposta vazia tratada.

	## 4.10 Validação de segurança

		Confirmar:
			- autenticação obrigatória;
			- autorização no backend;
			- CSRF protegido quando aplicável;
			- ausência de alteração via endpoint de consulta;
			- ausência de exposição de session key;
			- ausência de senhas nos logs;
			- ausência de tokens nos logs;
			- ausência de cookies nos logs;
			- ausência de SQL construído manualmente;
			- uso do ORM;
			- escape automático nos templates;
			- ausência de HTML fornecido pelo usuário;
			- respeito à LGPD;
			- e-mail e grupos visíveis somente para usuários autorizados.

	## 4.11 Validação de migrations

		Confirmar:
			- migration reversível;
			- migration descritiva;
			- dados existentes preservados;
			- índices criados;
			- constraints criadas;
			- PostgreSQL compatível;
			- Docker compatível;
			- ausência de operações destrutivas;
			- ausência de dependência de dados inexistentes.

	## 4.12 Execução dos testes

		Executar o comando padrão identificado no projeto.

		Possíveis comandos:
			```bash
			pytest
			```

			ou:
				```bash
				python manage.py test
				```

			ou:
				```bash
				docker compose exec <servico-web> pytest
				```

		Executar também testes específicos, quando aplicável:
			```bash
			pytest system/tests/
			```

		Verificar que todos os testes passam.

	## 4.13 Validação de qualidade

		Verificar:
			- PEP 8;
			- nomes claros;
			- responsabilidades separadas;
			- ausência de regras complexas nos templates;
			- tratamento de exceções;
			- logging estruturado;
			- ausência de informações sensíveis nos logs;
			- ausência de código morto;
			- ausência de duplicação desnecessária;
			- ausência de refatoração fora do escopo;
			- compatibilidade com padrões existentes;
			- documentação suficiente.

	## 4.14 Critérios de aceite funcionais

		A implementação somente será aceita se:
			1. O módulo estiver acessível.
			2. A tela exibir todos os campos obrigatórios.
			3. Somente usuários conectados forem exibidos.
			4. Usuários com sessão expirada não aparecerem.
			5. Usuários inativos não aparecerem como conectados.
			6. A lista for atualizada automaticamente.
			7. A interface for somente leitura.
			8. Não houver criação, alteração ou exclusão pela interface.
			9. Admin e Jazzmin funcionarem corretamente.
			10. Busca, paginação, ordenação e filtros funcionarem.
			11. O restante do sistema não for afetado.

	## 4.15 Critérios de aceite técnicos

		A implementação somente será aceita se:
			1. `python manage.py check` executar sem erros.
			2. Migrations forem geradas e aplicadas corretamente.
			3. Não houver N+1 queries.
			4. Houver índices adequados.
			5. Testes automatizados passarem.
			6. O código respeitar PEP 8.
			7. Não existirem regras complexas nos templates.
			8. A autenticação não for alterada.
			9. As permissões não forem alteradas.
			10. Não houver refatorações fora do escopo.
			11. O Docker continuar funcionando.
			12. Logging e tratamento de erros estiverem implementados.
			13. A solução funcionar em múltiplos workers e containers.
			14. A fonte de verdade não depender de memória local.
			15. `last_login` não for usado como indicador único de presença.

	## 4.16 Interpretação do CRUD

		Para este módulo, o requisito de CRUD deverá ser interpretado como:
			```text
			Create: não permitido
			Read: permitido e implementado
			Update: não permitido
			Delete: não permitido
			```

		O módulo deverá possuir consulta completa, mas não CRUD de manutenção manual.

		Caso seja necessário um CRUD interno para controlar registros de sessão, ele deverá ficar restrito ao backend ou a rotinas internas, sem disponibilizar criação, edição ou exclusão ao usuário da interface.

	## 4.17 Relatório final obrigatório

		Ao finalizar, produzir um relatório contendo:
			```text
			- resumo da implementação;
			- arquivos criados;
			- arquivos alterados;
			- migrations criadas;
			- modelo de dados adotado;
			- regra de usuário conectado;
			- timeout configurado;
			- intervalo de atualização;
			- estratégia de middleware ou heartbeat;
			- endpoints criados;
			- alterações no Admin;
			- alterações no Jazzmin;
			- testes criados;
			- comandos executados;
			- resultado de python manage.py check;
			- resultado das migrations;
			- resultado dos testes;
			- resultado da validação de N+1;
			- validação de segurança;
			- riscos remanescentes;
			- melhorias futuras;
			```

---

# Resultado esperado

	Ao final da execução desta Skill, o projeto Brasil Condo deverá possuir o módulo `06. Usuários Conectados (connecteduser)` funcionando em modo somente leitura, com:
		- identificação correta de usuários conectados;
		- controle por sessão e atividade recente;
		- timeout configurável;
		- suporte a múltiplos dispositivos;
		- consulta otimizada;
		- ausência de N+1 queries;
		- busca;
		- filtros;
		- paginação;
		- ordenação;
		- atualização periódica;
		- Admin somente leitura;
		- compatibilidade com Jazzmin;
		- logging estruturado;
		- segurança no backend;
		- migrations reversíveis;
		- testes automatizados;
		- compatibilidade com Docker;
		- preparação para Celery, RabbitMQ, Flower, Redis e WebSocket futuros;
		- documentação de instalação, uso e validação;
		- preservação da autenticação, autorização e demais módulos do sistema.


	Para disponibilizar a Skill ao Hermes, salve o conteúdo no caminho indicado e depois atualize ou reinicie o processo do Hermes, se necessário. A validação esperada é:
		```bash
		find skills/django/skill-001 -maxdepth 2 -type f -print
		hermes skills list | grep -i connected
		```

	Como a Skill está sendo carregada como uma Skill local pelo seu ambiente, o nome exibido poderá continuar sendo definido pelo registro local, mesmo que o `name` interno do YAML seja `connected-users-module`.

	