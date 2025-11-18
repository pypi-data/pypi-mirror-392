# 🐳 Ontologia Docker Playground

Ambiente de desenvolvimento completo e pré-configurado com todos os serviços Ontologia. Ideal para desenvolvimento, testes e demonstrações.

## 🎯 O Que Está Incluído

### 📊 **Banco de Dados**
- **PostgreSQL** - Banco transacional principal
- **KùzuDB** - Banco de grafos para traversals
- **DuckDB** - Analytics e data warehouse
- **Redis** - Cache e real-time updates
- **Elasticsearch** - Busca avançada e full-text

### ⚙️ **Orquestração**
- **Temporal** - Workflow orchestration
- **Dagster** - Data pipeline orchestration
- **RabbitMQ** - Message queuing

### 🖥️ **Interfaces e Ferramentas**
- **Ontologia API** - API principal
- **Kibana** - Visualização Elasticsearch
- **Temporal UI** - Interface de workflows
- **Dagster UI** - Interface de pipelines
- **Redis Commander** - Interface Redis
- **Marimo** - Reactive notebooks for data science
- **Grafana** - Monitoramento e dashboards
- **Prometheus** - Métricas e monitoring

## 🚀 Quick Start

### 1. Criar Playground
```bash
# Criar ambiente playground completo
ontologia-cli playground create my-playground

# Entrar no diretório
cd my-playground
```

### 2. Iniciar Serviços
```bash
# Iniciar todos os serviços
ontologia-cli playground start

# Ou manualmente
docker-compose up -d
```

### 3. Aguardar Setup
```bash
# Verificar status dos serviços
ontologia-cli playground status

# Aguardar todos ficarem saudáveis (pode levar 2-3 minutos)
docker-compose logs -f
```

### 4. Acessar Interfaces

#### 🌐 **APIs e Aplicações**
- **Ontologia API**: http://localhost:8000/docs
- **Marimo**: http://localhost:8888
- **Streamlit Dashboard**: http://localhost:8501

#### 🔍 **Busca e Analytics**
- **Kibana**: http://localhost:5601
- **Elasticsearch**: http://localhost:9200

#### ⚙️ **Orquestração**
- **Temporal UI**: http://localhost:7233
- **Dagster UI**: http://localhost:3000

#### 🗄️ **Bancos de Dados**
- **Redis Commander**: http://localhost:8081
- **pgAdmin**: http://localhost:5050 (admin@ontologia.dev / admin123)

#### 📊 **Monitoramento**
- **Grafana**: http://localhost:3001 (admin / admin)
- **Prometheus**: http://localhost:9090

## 🛠️ **Comandos CLI**

### Gerenciamento do Playground
```bash
# Criar novo playground
ontologia-cli playground create <nome>

# Iniciar serviços
ontologia-cli playground start

# Parar serviços
ontologia-cli playground stop

# Reiniciar serviços
ontologia-cli playground restart

# Ver status
ontologia-cli playground status

# Ver logs
ontologia-cli playground logs

# Destruir playground
ontologia-cli playground destroy
```

### Desenvolvimento
```bash
# Instalar dependências de desenvolvimento
ontologia-cli playground dev setup

# Rodar testes
ontologia-cli playground dev test

# Formatar código
ontologia-cli playground dev format

# Type checking
ontologia-cli playground dev type-check
```

## 📁 **Estrutura do Playground**

```
my-playground/
├── README.md                    # Este arquivo
├── docker-compose.yml          # Todos os serviços
├── docker-compose.dev.yml      # Configurações de dev
├── docker-compose.prod.yml     # Configurações de prod
├── .env                         # Variáveis de ambiente
├── .env.example                # Template de environment
├── scripts/                     # Scripts utilitários
│   ├── setup.sh                # Setup inicial
│   ├── wait-for-services.sh    # Aguardar serviços
│   ├── load-sample-data.sh     # Carregar dados exemplo
│   └── cleanup.sh              # Limpeza
├── data/                        # Dados persistentes
│   ├── postgres/
│   ├── elasticsearch/
│   ├── kuzu/
│   ├── duckdb/
│   └── redis/
├── notebooks/                   # Marimo notebooks
│   ├── 01_introduction.py
│   ├── 02_graph_traversals.py
│   ├── 03_analytics.py
│   ├── 04_workflows.py
│   └── 05_agents.py
├── examples/                    # Exemplos de código
│   ├── basic_crud.py
│   ├── graph_queries.py
│   ├── analytics_pipeline.py
│   └── workflow_examples.py
├── monitoring/                  # Configurações de monitoring
│   ├── grafana/
│   │   └── dashboards/
│   └── prometheus/
│       └── rules/
└── docs/                        # Documentação adicional
    ├── architecture.md
    ├── development.md
    └── troubleshooting.md
```

## 🔧 **Configuração**

### Environment Variables
```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações
vim .env
```

### Variáveis Principais
```bash
# Project Configuration
PROJECT_NAME=my-playground
COMPOSE_PROJECT_NAME=my-playground

# Database Configuration
POSTGRES_PORT=5432
POSTGRES_DB=ontologia
POSTGRES_USER=ontologia
POSTGRES_PASSWORD=ontologia123

# API Configuration
API_PORT=8000
API_HOST=0.0.0.0
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Feature Flags - All enabled for playground
STORAGE_MODE=sql_kuzu
ENABLE_SEARCH=true
ENABLE_WORKFLOWS=true
ENABLE_REALTIME=true
ENABLE_ORCHESTRATION=true

# External Services
ELASTICSEARCH_HOSTS=http://elasticsearch:9200
REDIS_URL=redis://:redis123@redis:6379
TEMPORAL_ADDRESS=temporal:7233
KUZU_PATH=/app/data/graph.kuzu
DUCKDB_PATH=/app/data/analytics.duckdb
```

## 📊 **Exemplos e Tutoriais**

### 📓 **Marimo Notebooks**

1. **Introduction** (`01_introduction.py`)
   - Overview do Ontologia
   - Configuração do ambiente
   - Primeiros passos com a API

2. **Graph Traversals** (`02_graph_traversals.py`)
   - Consultas de grafo
   - Análise de relacionamentos
   - Path finding algorithms

3. **Analytics** (`03_analytics.py`)
   - DuckDB analytics
   - Dagster pipelines
   - Visualização de dados

4. **Workflows** (`04_workflows.py`)
   - Temporal workflows
   - Processos assíncronos
   - Monitoramento de execuções

5. **AI Agents** (`05_agents.py`)
   - Upload drag & drop de CSV/Parquet
   - Detecção automática de schema com IA
   - Geração instantânea de ontologia
   - Consultas em linguagem natural
   - Criação de agentes personalizados

### 💻 **Exemplos de Código**

- **basic_crud.py**: Operações CRUD básicas
- **graph_queries.py**: Consultas de grafo avançadas
- **analytics_pipeline.py**: Pipeline de analytics completo
- **workflow_examples.py**: Exemplos de workflows

## 🏥 **Casos de Uso Prontos**

### Healthcare Management
```bash
# Carregar dados exemplo de healthcare
ontologia-cli playground load healthcare

# Acessar dashboard de healthcare
http://localhost:8501/healthcare
```

### Financial Analytics
```bash
# Carregar dados exemplo financeiros
ontologia-cli playground load finance

# Acessar dashboard financeiro
http://localhost:8501/finance
```

### E-commerce
```bash
# Carregar dados exemplo de e-commerce
ontologia-cli playground load ecommerce

# Acessar dashboard de e-commerce
http://localhost:8501/ecommerce
```

## 🔍 **Monitoramento e Debugging**

### Health Checks
```bash
# Verificar saúde de todos os serviços
ontologia-cli playground health

# Health check específico
curl http://localhost:8000/health
curl http://localhost:9200/_cluster/health
curl http://localhost:7233/api/v1/namespaces/default
```

### Logs
```bash
# Ver todos os logs
docker-compose logs -f

# Logs de serviço específico
docker-compose logs -f api
docker-compose logs -f temporal
docker-compose logs -f dagster
```

### Métricas
```bash
# Acessar métricas Prometheus
curl http://localhost:9090/api/v1/query?query=up

# Métricas customizadas
curl http://localhost:8000/metrics
```

## 🚨 **Troubleshooting**

### Problemas Comuns

#### Serviços não iniciam
```bash
# Verificar portas em uso
netstat -tulpn | grep :8000

# Limpar volumes e reiniciar
docker-compose down -v
docker-compose up -d
```

#### Memória insuficiente
```bash
# Aumentar memória Docker
# Docker Desktop → Settings → Resources → Memory (8GB+)

# Ou desabilitar serviços não essenciais
docker-compose stop kibana grafana prometheus
```

#### Conexões rejeitadas
```bash
# Verificar configurações de rede
docker network ls
docker network inspect ontologia-playground-network

# Resetar rede
docker-compose down
docker network prune
docker-compose up -d
```

### Performance

#### Otimização para Desenvolvimento
```bash
# Usar compose de desenvolvimento
docker-compose -f docker-compose.dev.yml up -d

# Desabilitar serviços pesados
docker-compose stop elasticsearch kibana grafana
```

#### Otimização para Produção
```bash
# Usar compose de produção
docker-compose -f docker-compose.prod.yml up -d

# Escalar serviços
docker-compose up -d --scale api=3 --scale worker=2
```

## 📚 **Documentação Adicional**

- [Architecture Guide](docs/architecture.md)
- [Development Guide](docs/development.md)
- [API Reference](http://localhost:8000/docs)
- [Troubleshooting Guide](docs/troubleshooting.md)

## 🎯 **Próximos Passos**

1. **Explorar os Notebooks**: Comece com `01_introduction.py`
2. **Testar a API**: Use http://localhost:8000/docs
3. **Criar seu Primeiro Projeto**: Use os templates do CLI
4. **Explorar Casos de Uso**: Carregue dados exemplo específicos

## 🤝 **Contribuição**

Encontrou um problema? Tem uma sugestão?

- Abra uma issue no GitHub
- Contribua com exemplos e melhorias
- Compartilhe seus casos de uso

---

**Divirta-se explorando o poder do Ontologia!** 🚀
