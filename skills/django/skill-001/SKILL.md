---
  name: connected-users-module
  description: Implementa e atualiza o módulo somente leitura 06. Usuários Conectados (connecteduser) no app Django system do projeto Brasil Condo, utilizando sessões válidas e atividade recente.
  version: 1.0.0
  author: Brasil Condo
  license: Proprietary
  platforms:
    - linux
  metadata:
    hermes:
      tags:
        - django
        - python
        - postgresql
        - django-admin
        - jazzmin
        - connected-users
        - sessions
        - clean-architecture
        - testing
      related_skills: []
---

# Skill: Usuários Conectados — Brasil Condo

  ## 1. Objetivo

    Atualizar o módulo `connecteduser` para exibir os usuários atualmente conectados ao sistema.

    A interface deverá apresentar os seguintes campos:

      -------------------------------------------------------------------------
      | Campo 				      | Descrição 									                    |
      |-----------------------|-----------------------------------------------|
      | Usuário 				    | Nome de usuário ou identificação do usuário	    |
      | Endereço de E-mail  | E-mail cadastrado 							                |
      | Grupos 				      | Grupos aos quais o usuário pertence 			      |
      | Ativo 				      | Indicação se o usuário está ativo 			        |
      | Membro da equipe 		| Indicação de `is_staff` 						            |
      | Último login 			  | Data e hora do último login registrado 		      |
      -------------------------------------------------------------------------


    A tela deverá ser somente leitura e não poderá permitir:
      - criação de usuários;
      - alteração de usuários;
      - exclusão de usuários;
      - alteração de grupos;
      - alteração de permissões;
      - ativação ou desativação de usuários;
      - edição do último login.

  ---

  ## 2. Regra para considerar um usuário conectado

    Não utilizar exclusivamente o campo `last_login` para determinar se um usuário está online.

    O campo `last_login` representa o último login registrado, mas não comprova que o usuário ainda está conectado.

    A solução deverá utilizar uma estratégia baseada em sessão e atividade recente.

    ## Estratégia recomendada

      Criar ou atualizar um registro de conexão por sessão, contendo informações equivalentes a:
        ```text
        Usuário
        Sessão
        Data/hora de conexão
        Data/hora da última atividade
        Data/hora do último login
        Status da conexão
        Endereço IP, se permitido pela política de segurança
        User-Agent, opcionalmente
        ```

      Um usuário será considerado conectado quando:
        ```text
        sessão válida
        E usuário autenticado
        E última atividade dentro do tempo configurado
        ```

      O tempo de expiração da atividade deverá ser configurável, por exemplo:
        ```text
        CONNECTED_USER_TIMEOUT = 5 minutos
        ```

      Esse valor não deve ser fixado diretamente no código.

    ## Considerações importantes
      - O encerramento do navegador nem sempre executa uma requisição ao servidor.
      - Por isso, não depender exclusivamente de logout para marcar o usuário como desconectado.
      - A expiração deve ser determinada por `last_activity` ou por uma regra equivalente.
      - Usuários com sessão expirada não devem aparecer na listagem.
      - Usuários inativos há mais tempo que o limite configurado não devem aparecer como conectados.
      - A solução deve funcionar corretamente em múltiplos workers e múltiplos containers.
      - Não utilizar memória local do processo como fonte oficial de usuários conectados.
      - A fonte de verdade deverá ser o PostgreSQL ou um mecanismo compartilhado compatível com a arquitetura atual.

  ---

  ## 3. Arquitetura técnica esperada
  
    A implementação deve respeitar a separação entre:
      ```text
      Presentation Layer
      Application Layer
      Domain Layer
      Infrastructure Layer
      ```

    ## Componentes sugeridos
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

      A estrutura deverá ser adaptada à estrutura já existente no projeto. Não criar uma nova arquitetura paralela caso o projeto já possua padrões consolidados.

  ---

  ## 4. Model

    Avaliar o model atual de `connecteduser` antes de realizar qualquer alteração.

    Se o model existente não possuir informações suficientes para controlar as conexões, adicionar somente os campos necessários, preservando compatibilidade com os dados atuais.

    Sugestão de campos técnicos:
      ```text
      user
      session_key
      connected_at
      last_activity
      disconnected_at
      is_connected
      ip_address, se aplicável
      user_agent, opcional
      created_at
      updated_at
      ```

    ## Regras do model
      - Utilizar relacionamento com o model de usuário existente.
      - Não criar outro model de usuário.
      - Não alterar o mecanismo atual de autenticação.
      - Não duplicar campos já disponíveis no usuário.
      - Utilizar `related_name` claro e compatível com o projeto.
      - Aplicar índices em campos utilizados para filtragem.
      - Configurar constraints adequadas.
      - Evitar registros duplicados para a mesma sessão.
      - Utilizar `UniqueConstraint` quando aplicável.
      - Definir `db_index=True` para campos consultados frequentemente.

      Exemplos de campos que podem receber índice:
        ```text
        user
        session_key
        last_activity
        is_connected
        ```

      A implementação deverá avaliar se é melhor utilizar:
        ```text
        um registro por sessão
        ```

        ou:

        ```text
        um registro por usuário conectado
        ```

      A recomendação é utilizar **um registro por sessão**, porque o mesmo usuário pode estar conectado em mais de um navegador ou dispositivo.

  ---

  ## 5. Controle de atividade

    Criar um mecanismo para registrar a atividade do usuário sem modificar o fluxo atual de autenticação.

    A solução pode utilizar:
      - middleware específico;
      - service layer;
      - signal somente se já houver padrão equivalente no projeto;
      - endpoint de heartbeat;
      - atualização em requisições autenticadas;
      - tarefa assíncrona futura com Celery.

    ## Requisitos
      - Não atualizar o banco em excesso.
      - Evitar uma gravação para cada requisição.
      - Atualizar `last_activity` somente após um intervalo configurável.
      - Utilizar operações atômicas quando necessário.
      - Evitar condições de corrida.
      - Não bloquear a requisição principal com operações desnecessárias.
      - Não registrar dados sensíveis nos logs.
      - Não alterar as permissões existentes.

    Uma estratégia recomendada é atualizar a atividade no máximo uma vez a cada determinado intervalo:
      ```text
      ACTIVITY_UPDATE_INTERVAL = 60 segundos
      ```

    O valor deverá ser configurável.

  ---

  ## 6. Service Layer

    Criar ou atualizar um serviço específico para a regra de usuários conectados.

    Exemplos de responsabilidades:
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
      - facilitar testes unitários.

    A view não deverá conter regras complexas de conexão.

  ---

  ## 7. Query e otimização
  
    A consulta dos usuários conectados deve:
      - filtrar somente sessões ativas;
      - ignorar sessões expiradas;
      - utilizar `select_related` para o usuário;
      - utilizar `prefetch_related` para grupos;
      - evitar N+1 queries;
      - ordenar por `last_activity` ou `last_login`;
      - retornar somente os campos necessários quando possível;
      - utilizar índices adequados.

    A consulta deve ser equivalente conceitualmente a:
      ```text
      is_connected = true
      AND last_activity >= limite_de_expiração
      AND user.is_active = true
      ```

    Não exibir usuários inativos ou sessões inválidas.

    Os grupos deverão ser apresentados sem executar uma consulta individual para cada usuário.


  ---

  ## 8. Interface

    Criar ou atualizar o template do módulo com os seguintes campos:
      ```text
      Usuário
      Endereço de E-mail
      Grupos
      Ativo
      Membro da equipe
      Último login
      ```

    ## Características da interface
      - Somente leitura.
      - Layout compatível com Jazzmin.
      - Responsivo.
      - Paginação.
      - Ordenação.
      - Busca por usuário e e-mail.
      - Filtro por grupo.
      - Filtro por membro da equipe.
      - Filtro por status de atividade.
      - Exibição clara de data e hora.
      - Indicação visual para usuário conectado.
      - Estado vazio quando não houver usuários conectados.
      - Mensagens de erro amigáveis.
      - Mensagens de carregamento.
      - Tratamento de falha na atualização em tempo real.

    ## Atualização em tempo real

      Implementar atualização periódica dos dados usando JavaScript.

      A solução poderá utilizar:
        ```text
        AJAX
        ```

      ou:
        ```text
        Fetch API
        ```

      Não é necessário implementar WebSocket neste momento, a menos que o projeto já possua infraestrutura pronta para isso.

      A atualização deverá:
        - consultar somente usuários conectados;
        - atualizar a tabela sem recarregar toda a página;
        - preservar filtros e paginação quando possível;
        - exibir o horário da última atualização;
        - evitar múltiplas requisições simultâneas;
        - pausar ou reduzir a frequência quando a aba estiver inativa;
        - tratar respostas HTTP 401, 403, 404 e 500;
        - cancelar requisições anteriores quando necessário;
        - evitar vazamento de timers ou listeners.

      Sugestão:
        ```text
        intervalo de atualização: 30 a 60 segundos
        ```

      O intervalo deverá ser configurável no JavaScript ou por configuração do projeto.

  ---

  ## 9. Forms

    Como a tela é somente leitura, não criar formulário de edição ou formulário CRUD tradicional para alteração dos dados.

    Caso o módulo atual já possua um `ModelForm`, avaliar sua necessidade.

    Se mantido, ele deverá:
      - impedir criação;
      - impedir alteração;
      - impedir exclusão;
      - utilizar campos desabilitados;
      - manter `help_text`;
      - manter mensagens de erro;
      - não permitir alteração via requisições manipuladas manualmente;
      - validar no backend, mesmo que o frontend esteja bloqueado.

    A segurança não deve depender de campos `disabled` no HTML.

  ---

  ## 10. Widgets, placeholders e máscaras

    Como o módulo é somente leitura:
      - não utilizar máscaras de entrada nos campos exibidos;
      - não utilizar placeholders em campos que não são editáveis;
      - utilizar widgets somente para filtros de pesquisa, se existirem;
      - aplicar escape correto para usuário, e-mail e grupos;
      - não renderizar HTML fornecido pelo usuário;
      - evitar risco de XSS.

    Para filtros de busca, utilizar:
      ```text
      placeholder="Pesquisar usuário ou e-mail..."
      ```

    Os valores apresentados na tabela devem ser tratados como dados de saída, não como campos editáveis.

  ---

  ## 11. Admin e Jazzmin

    Atualizar o Django Admin para apresentar os usuários conectados em modo somente leitura.

    O admin deverá:
      - exibir os campos solicitados;
      - impedir `add`;
      - impedir `change`;
      - impedir `delete`;
      - permitir apenas visualização;
      - configurar `list_display`;
      - configurar `list_filter`;
      - configurar `search_fields`;
      - configurar `ordering`;
      - configurar `readonly_fields`;
      - evitar consultas N+1;
      - manter compatibilidade visual com Jazzmin.

    O acesso deverá respeitar as permissões existentes.

    Não conceder novas permissões automaticamente.

    Não alterar o sistema geral de autenticação ou autorização.

  ---

  ## 12. URLs e views

    Criar ou atualizar as rotas específicas do módulo.

    Sugestão conceitual:
      ```text
      /system/connected-users/
      /system/connected-users/data/
      ```

    A rota de dados deverá:
      - exigir autenticação;
      - respeitar as permissões atuais;
      - retornar somente usuários conectados;
      - retornar JSON estruturado;
      - utilizar status HTTP apropriados;
      - não expor informações sensíveis;
      - possuir proteção CSRF quando aplicável;
      - não permitir alteração de dados via endpoint de consulta.

    A view deverá delegar a busca para um selector ou service.

  ---

  ## 13. Celery, RabbitMQ e Flower

    A primeira implementação não deve depender obrigatoriamente de Celery para exibir a listagem em tempo real.

    Entretanto, preparar a solução para tarefas assíncronas futuras, como:
      ```text
      limpeza de sessões expiradas
      remoção de registros antigos
      reconciliação de sessões
      auditoria de conexões
      métricas de usuários ativos
      ```

    Uma tarefa futura poderá executar periodicamente:
      ```text
      cleanup_stale_connected_users()
      ```

    Essa tarefa deverá ser idempotente e segura para execução repetida.

    Não criar dependência desnecessária de RabbitMQ ou Celery para uma operação que possa ser resolvida eficientemente por consulta e atualização normal.

  ---

  ## 14. Logging e auditoria

    Implementar logging estruturado para eventos relevantes:
      ```text
      connected_user_registered
      connected_user_activity_updated
      connected_user_session_expired
      connected_user_cleanup_executed
      connected_user_query_failed
      ```

    Os logs não devem registrar:
      - senhas;
      - tokens;
      - cookies;
      - session keys completas;
      - dados sensíveis desnecessários.

    Quando necessário, mascarar ou aplicar hash aos identificadores de sessão.

    Os logs deverão conter, quando aplicável:
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

  ---

  ## 15. Segurança

    A implementação deve:
      - preservar o sistema atual de autenticação;
      - respeitar as permissões existentes;
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

    O e-mail e os grupos somente deverão ser exibidos para usuários autorizados conforme as regras atuais do sistema.
  
  ---

  ## 16. Migrações

    Criar migrations somente quando necessário.

    As migrations devem:
      - ser reversíveis;
      - possuir nomes descritivos;
      - preservar dados existentes;
      - não apagar informações sem justificativa;
      - criar índices necessários;
      - criar constraints adequadas;
      - executar em ambiente Docker;
      - funcionar em PostgreSQL;
      - não depender de dados inexistentes.

    Validar com:
      ```bash
      python manage.py makemigrations
      python manage.py migrate
      python manage.py check
      ```

  ---

  ## 17. Testes obrigatórios

    Criar ou atualizar testes para:

    ## Model
      - criação de registro de conexão;
      - unicidade por sessão;
      - atualização de atividade;
      - expiração de sessão;
      - constraints;
      - índices e relacionamentos.

    ## Services
      - registro de conexão;
      - atualização idempotente;
      - expiração de conexões;
      - listagem de usuários conectados;
      - tratamento de usuário inativo;
      - tratamento de sessão inexistente;
      - tratamento de falha no banco.

    ## Views
      - usuário autenticado;
      - usuário não autenticado;
      - usuário sem permissão;
      - resposta JSON;
      - filtros;
      - paginação;
      - ausência de usuários conectados;
      - erros controlados.

    ## Admin
      - acesso somente leitura;
      - bloqueio de criação;
      - bloqueio de edição;
      - bloqueio de exclusão;
      - filtros;
      - busca;
      - ausência de N+1 queries.

    ## JavaScript
      - atualização periódica;
      - tratamento de erro;
      - resposta vazia;
      - resposta inválida;
      - status HTTP;
      - preservação dos filtros;
      - prevenção de requisições simultâneas.

  ---

  ## 18. Critérios de aceite

    ## Funcionais
      1. 	O módulo `06. Usuários Conectados (connecteduser)` está acessível.
      2. 	A tela exibe:
          - Usuário;
          - Endereço de E-mail;
          - Grupos;
          - Ativo;
          - Membro da equipe;
          - Último login.
      3. 	A tela apresenta somente usuários conectados.
      4. 	Usuários com sessão expirada não são exibidos.
      5. 	Usuários inativos não são exibidos como conectados.
      6. 	A lista é atualizada automaticamente.
      7. 	A tela é somente leitura.
      8. 	Não é possível criar, alterar ou excluir registros pela interface.
      9. 	O admin/Jazzmin funciona corretamente.
      10. A busca, paginação e filtros funcionam.
      11. O Moodle, Brasil Condo e demais aplicações não são afetados.

    ## Técnicos
      1. Executar sem erros:
        ```bash
        python manage.py check
        ```
      2. Migrações executam corretamente:
        ```bash
        python manage.py makemigrations
        python manage.py migrate
        ```
      3. Não existem consultas N+1 na listagem.
      4. A consulta utiliza índices adequados.
      5. Os testes automatizados passam.
      6. A implementação respeita PEP 8.
      7. Não há regras de negócio complexas dentro dos templates.
      8. Não há alteração na autenticação existente.
      9. Não há alteração nas permissões existentes.
      10. Não há refatorações fora do escopo.
      11. O funcionamento permanece compatível com Docker.
      12. O código possui logging e tratamento de erros adequados.

  ---

  ## 19. Observação sobre o critério “CRUD completo”

    Existe uma incompatibilidade entre:
      ```text
      CRUD completo funcionando
      ```

    e:
      ```text
      Formulário somente leitura
      ```

    Para este módulo, o critério deverá ser interpretado da seguinte forma:
      ```text
      Create: não permitido
      Read: permitido e implementado
      Update: não permitido
      Delete: não permitido
      ```

    Ou seja, o módulo deverá possuir **consulta completa**, mas não CRUD de manutenção manual.

    Caso o projeto exija tecnicamente um CRUD interno para controlar registros de sessão, ele deverá ficar restrito ao backend ou a rotinas internas, sem disponibilizar operações de criação, edição ou exclusão para o usuário da interface.

  ---

  ## 20. Entregáveis

    Entregar:
      - model atualizado, se necessário;
      - migrations;
      - service layer;
      - selectors ou repositories;
      - middleware ou mecanismo de atualização de atividade;
      - forms atualizados, quando aplicável;
      - admin atualizado;
      - configuração do Jazzmin;
      - views atualizadas;
      - URLs;
      - templates;
      - JavaScript;
      - testes automatizados;
      - configurações necessárias;
      - documentação de instalação;
      - documentação de uso;
      - resumo técnico das alterações;
      - instruções para executar no Docker;
      - instruções para executar migrations;
      - instruções para validar o funcionamento.

  ---

  ## 21. Sugestões de melhorias

    ## 1. Utilizar registro por sessão

      Em vez de guardar somente um registro por usuário, armazenar uma conexão por sessão:
        ```text
        Usuário A — navegador Chrome
        Usuário A — aplicativo mobile
        Usuário A — navegador Firefox
        ```

      Isso representa corretamente múltiplos acessos simultâneos.

    ## 2. Adicionar filtros de monitoramento

      Além dos campos obrigatórios, considerar futuramente:
        ```text
        Data/hora de conexão
        Última atividade
        Endereço IP mascarado
        Dispositivo
        Navegador
        Tempo conectado
        ```

      Esses campos devem ser avaliados conforme a política de privacidade e a LGPD.

    ## 3. Criar endpoint de heartbeat

      Se o sistema possuir páginas com poucas requisições ao backend, somente o middleware poderá não registrar atividade suficiente.

      Nesse caso, implementar um endpoint leve de heartbeat:
        ```text
        POST /system/connected-users/heartbeat/
        ```

      Esse endpoint deverá apenas atualizar a atividade da sessão atual.

    ## 4. Utilizar WebSocket futuramente

      Para uma atualização realmente instantânea, considerar:
        ```text
        Django Channels
        Redis
        WebSocket
        ```

      A solução atual com polling periódico é mais simples e adequada para a primeira versão.

    ## 5. Usar Redis em ambientes escaláveis

      Se o projeto for executado em múltiplos containers ou múltiplas réplicas, avaliar:
        ```text
        Redis para sessões ou cache de atividade
        PostgreSQL para persistência e auditoria
        ```

      A escolha deve considerar consistência, custo e volume de usuários.

    ## 6. Política de retenção

      Criar uma rotina periódica para remover conexões antigas, por exemplo:
        ```text
        Excluir registros desconectados há mais de 30 dias
        ```

      O prazo deverá ser configurável e compatível com os requisitos de auditoria.

    ## 7. Métricas

      Futuramente, disponibilizar métricas como:
        ```text
        usuários conectados agora
        pico de usuários simultâneos
        tempo médio de sessão
        acessos por condomínio
        acessos por horário
        ```

      Essas métricas podem ser integradas ao Flower, Prometheus ou Grafana.

    ## 8. Não usar `last_login` como indicador de presença

      O campo `last_login` deve ser exibido conforme solicitado, mas a presença online deverá depender de:
        ```text
        sessão válida + atividade recente
        ```

      Essa separação é essencial para evitar que usuários sejam exibidos como online mesmo horas ou dias após o último acesso.
  
  ---

