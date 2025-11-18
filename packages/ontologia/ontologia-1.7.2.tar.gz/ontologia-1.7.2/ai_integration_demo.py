#!/usr/bin/env python3
"""
Demonstração de Integração com IA e Analytics no Ontologia Framework

Este exemplo mostra como usar as capacidades de IA e analytics
do framework Ontologia para processamento inteligente de dados.
"""

import json
import sys

# Importar pandas se disponível
try:
    import pandas as pd  # noqa: F401  # Available for future use

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("Pandas não disponível, usando dados simulados")

# Verificar se estamos no ambiente virtual do projeto
try:
    # Tente importar as dependências do projeto
    sys.path.insert(0, "/Users/kevinsaltarelli/Documents/GitHub/ontologia")

    # Imports que funcionariam com o ambiente completo
    print("🔧 Configurando ambiente de demonstração...")
    print("=" * 50)

except ImportError as e:
    print(f"⚠️  Dependências não encontradas: {e}")
    print("Este é um exemplo demonstrativo de como funcionaria a integração com IA.\n")


def demonstrate_ai_integration():
    """Demonstra as capacidades de integração com IA do Ontologia"""

    print("🤖 Integração com IA no Ontologia Framework")
    print("=" * 50)

    # 1. Detecção Automática de Schema
    print("\n1. 📊 Detecção Automática de Schema com IA:")
    print("-" * 45)

    # Dados de exemplo (simulando um DataFrame)
    sample_data = [
        {
            "employee_id": 1,
            "name": "Ana Silva",
            "email": "ana@empresa.com",
            "department": "TI",
            "salary": 8000,
            "hire_date": "2020-01-15",
        },
        {
            "employee_id": 2,
            "name": "Carlos Souza",
            "email": "carlos@empresa.com",
            "department": "RH",
            "salary": 6000,
            "hire_date": "2019-03-20",
        },
        {
            "employee_id": 3,
            "name": "Maria Santos",
            "email": "maria@empresa.com",
            "department": "TI",
            "salary": 9000,
            "hire_date": "2021-06-10",
        },
        {
            "employee_id": 4,
            "name": "João Oliveira",
            "email": "joao@empresa.com",
            "department": "Financeiro",
            "salary": 7000,
            "hire_date": "2018-11-05",
        },
        {
            "employee_id": 5,
            "name": "Paula Costa",
            "email": "paula@empresa.com",
            "department": "TI",
            "salary": 8500,
            "hire_date": "2022-02-28",
        },
    ]

    print("Dados de exemplo:")
    for i, row in enumerate(sample_data[:3]):  # Mostra apenas as 3 primeiras linhas
        print(f"  {i+1}: {row}")
    print(f"  ... e mais {len(sample_data)-3} linhas")

    print("\nAnálise automática com IA:")
    print("- employee_id: Identificador único do funcionário (chave primária)")
    print("- name: Nome completo do funcionário (texto)")
    print("- email: Email corporativo (texto, formato email)")
    print("- department: Departamento (texto, categoria)")
    print("- salary: Salário (numérico, moeda)")
    print("- hire_date: Data de contratação (data)")

    # Schema gerado automaticamente
    generated_schema = {
        "object_type": "Employee",
        "properties": {
            "id": {"dataType": "string", "required": True, "source": "employee_id"},
            "name": {"dataType": "string", "required": True, "source": "name"},
            "email": {"dataType": "string", "format": "email", "required": True, "source": "email"},
            "department": {"dataType": "string", "required": True, "source": "department"},
            "salary": {"dataType": "double", "required": True, "source": "salary"},
            "hire_date": {"dataType": "date", "required": True, "source": "hire_date"},
        },
    }

    print("\nSchema YAML gerado automaticamente:")
    print(json.dumps(generated_schema, indent=2))

    # 2. Processamento de Linguagem Natural
    print("\n\n2. 🔍 Consultas em Linguagem Natural:")
    print("-" * 40)

    natural_language_queries = [
        "Quantos funcionários temos no departamento de TI?",
        "Qual é o salário médio por departamento?",
        "Mostre os funcionários contratados nos últimos 6 meses",
        "Quem são os 3 funcionários com maior salário?",
        "Qual departamento tem o maior número de funcionários?",
    ]

    print("Exemplos de consultas em linguagem natural:")
    for query in natural_language_queries:
        print(f"  • {query}")

    print("\nConversão automática para consultas estruturadas:")
    for query in natural_language_queries:
        if "Quantos funcionários" in query and "TI" in query:
            print(f"  '{query}' → SELECT COUNT(*) FROM employees WHERE department = 'TI'")
        elif "salário médio" in query:
            print(
                f"  '{query}' → SELECT department, AVG(salary) FROM employees GROUP BY department"
            )
        elif "contratados nos últimos" in query:
            print(
                f"  '{query}' → SELECT * FROM employees WHERE hire_date >= date('now', '-6 months')"
            )
        elif "maior salário" in query:
            print(f"  '{query}' → SELECT * FROM employees ORDER BY salary DESC LIMIT 3")
        elif "maior número de funcionários" in query:
            print(
                f"  '{query}' → SELECT department, COUNT(*) as count FROM employees GROUP BY department ORDER BY count DESC LIMIT 1"
            )

    # 3. Recomendações de Relacionamentos
    print("\n\n3. 🔗 Recomendações de Relacionamentos com IA:")
    print("-" * 50)

    print("Análise inteligente dos dados para sugerir relacionamentos:")
    print("- Detectado campo 'department' → Sugerir tipo de objeto 'Department'")
    print(
        "- Detectado padrão de IDs → Sugerir relacionamento 'belongs_to' entre Employee e Department"
    )
    print(
        "- Detectado campo de salário → Sugerir relacionamento 'has_salary_history' para rastrear mudanças"
    )
    print("- Detectado campo de data → Sugerir relacionamento temporal para análises")

    suggested_relationships = {
        "belongs_to": {
            "from": "Employee",
            "to": "Department",
            "properties": ["start_date", "role"],
        },
        "manages": {
            "from": "Employee",
            "to": "Employee",
            "properties": ["start_date", "management_level"],
        },
        "has_skill": {
            "from": "Employee",
            "to": "Skill",
            "properties": ["proficiency_level", "certified"],
        },
    }

    print("\nRelacionamentos sugeridos:")
    for rel_name, rel_config in suggested_relationships.items():
        print(f"  • {rel_name}: {rel_config['from']} → {rel_config['to']}")

    # 4. Análise de Dados com DuckDB
    print("\n\n4. 📈 Analytics com DuckDB:")
    print("-" * 35)

    print("Consultas analíticas avançadas com DuckDB:")

    analytics_queries = [
        "SELECT department, COUNT(*) as num_employees, AVG(salary) as avg_salary, MAX(salary) as max_salary FROM employees GROUP BY department",
        "SELECT department, AVG(salary) as avg_salary FROM employees GROUP BY department ORDER BY avg_salary DESC",
        "SELECT DATE_TRUNC('month', hire_date) as month, COUNT(*) as hires FROM employees GROUP BY month ORDER BY month",
        "SELECT department, COUNT(*) as count FROM employees GROUP BY department",
    ]

    for query in analytics_queries:
        print(f"\nConsulta: {query}")
        print("Resultados simulados:")
        if "department" in query and "COUNT" in query and "AVG" in query:
            print("  department  | num_employees | avg_salary | max_salary")
            print("  -----------|---------------|------------|----------")
            print("  TI         | 3             | 8500       | 9000")
            print("  RH         | 1             | 6000       | 6000")
            print("  Financeiro | 1             | 7000       | 7000")
        elif "AVG(salary)" in query and "ORDER BY" in query:
            print("  department  | avg_salary")
            print("  -----------|-----------")
            print("  TI         | 8500")
            print("  Financeiro | 7000")
            print("  RH         | 6000")
        elif "DATE_TRUNC" in query:
            print("  month      | hires")
            print("  ----------|------")
            print("  2018-11-01 | 1")
            print("  2019-03-01 | 1")
            print("  2020-01-01 | 1")
            print("  2021-06-01 | 1")
            print("  2022-02-01 | 1")

    # 5. Agentes de IA Personalizados
    print("\n\n5. 🤖 Agentes de IA Personalizados:")
    print("-" * 40)

    print("Criação de agentes especializados para diferentes tarefas:")

    ai_agents = {
        "HR Analyst": {
            "description": "Análise de dados de RH e métricas de pessoal",
            "capabilities": [
                "Analisar tendências de contratação",
                "Calcular taxas de rotatividade",
                "Identificar gaps de habilidades",
                "Prever necessidades de contratação",
            ],
        },
        "Data Scientist": {
            "description": "Análise estatística e modelagem preditiva",
            "capabilities": [
                "Análise de correlação entre salário e desempenho",
                "Previsão de attrition de funcionários",
                "Segmentação de funcionários por perfil",
                "Recomendações de otimização de equipe",
            ],
        },
        "Business Analyst": {
            "description": "Análise de negócios e geração de insights",
            "capabilities": [
                "Análise de eficiência por departamento",
                "Identificação de outliers organizacionais",
                "Recomendações de reorganização",
                "Análise de custos por equipe",
            ],
        },
    }

    for agent_name, agent_config in ai_agents.items():
        print(f"\n{agent_name}:")
        print(f"  Descrição: {agent_config['description']}")
        print("  Capacidades:")
        for capability in agent_config["capabilities"]:
            print(f"    • {capability}")

    # 6. Integração com Workflows
    print("\n\n6. ⚙️ Integração com Workflows (Temporal/Dagster):")
    print("-" * 55)

    print("Exemplos de workflows automatizados:")

    workflows = [
        {
            "name": "Onboarding de Novos Funcionários",
            "description": "Processo automatizado para integração de novos funcionários",
            "steps": [
                "Detectar novo funcionário no sistema",
                "Gerar email de boas-vindas",
                "Criar tarefas no sistema de RH",
                "Alocar recursos necessários",
                "Agendar treinamentos iniciais",
            ],
        },
        {
            "name": "Análise Mensal de Desempenho",
            "description": "Análise automatizada de métricas de desempenho",
            "steps": [
                "Coletar dados de produtividade",
                "Calcular métricas de desempenho",
                "Gerar relatórios por departamento",
                "Identificar necessidades de treinamento",
                "Enviar resumo para gerentes",
            ],
        },
        {
            "name": "Atualização de Skills",
            "description": "Processo para atualizar e validar skills dos funcionários",
            "steps": [
                "Identificar skills desatualizadas",
                "Verificar certificações",
                "Sugerir treinamentos",
                "Atualizar perfis de funcionários",
                "Notificar gerentes sobre mudanças",
            ],
        },
    ]

    for workflow in workflows:
        print(f"\n{workflow['name']}:")
        print(f"  Descrição: {workflow['description']}")
        print("  Passos:")
        for i, step in enumerate(workflow["steps"], 1):
            print(f"    {i}. {step}")

    print("\n\n✅ Demonstração concluída!")
    print("=" * 50)
    print("\nPara usar estas funcionalidades com o Ontologia Framework:")
    print("1. Inicie o playground: ontologia-cli playground start")
    print("2. Acesse os notebooks Marimo em: http://localhost:8888")
    print("3. Configure as chaves de API para serviços de IA")
    print("4. Use a CLI para gerenciar ontologias: ontologia-cli --help")


if __name__ == "__main__":
    demonstrate_ai_integration()
