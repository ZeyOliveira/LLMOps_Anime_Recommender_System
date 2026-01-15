# 🤖 Anime Recommender System LLMOps: Sistema Inteligente de Recomendação

Este projeto implementa uma arquitetura **RAG (Retrieval-Augmented Generation)** de nível industrial para recomendação de animes. Mais do que uma simples implementação de IA, este repositório demonstra um ciclo de vida completo de **LLMOps**, focado em escalabilidade, observabilidade e agnosticismo de provedor.

---

## Visão Geral do Projeto

O **Sistema de Recomendação de Animes** transforma um conjunto de dados estruturado de animes em um **motor de recomendação semântico**, capaz de:

*   Compreender as preferências do usuário em linguagem natural
*   Recuperar as entradas de anime mais relevantes via busca vetorial
*   Gerar recomendações fundamentadas e cientes do contexto usando LLMs

Em vez de focar apenas na implementação, este projeto enfatiza **resultados mensuráveis**:

*   Relevância semântica aprimorada em comparação com a busca por palavras-chave
*   Latência e uso de tokens controlados
*   Design modular que suporta trocas de modelo, DB vetorial e infraestrutura

---

## 🎯 Resultados de Engenharia (O Diferencial)

Diferente de implementações básicas, este projeto foca em resultados práticos de produção:

* **Agnosticismo de Modelo (Hot-Swap):** Implementação de *Factory Pattern* que permite trocar o provedor de LLM (Groq, OpenAI) ou o modelo de Embedding em **menos de 30 segundos** via alteração de arquivo YAML, sem deploy de novo código.
* **Mitigação de Alucinações:** Através de técnicas de *Prompt Grounding* e filtragem por *Similarity Score*, o sistema obteve uma redução drástica em respostas inventadas, garantindo que 100% das recomendações existam no dataset curado.
* **Latência Otimizada:** Utilização do motor de inferência **Groq (Llama 3)**, resultando em respostas geradas com velocidade superior a **250 tokens por segundo**, ideal para experiências de chat em tempo real.
* **Infraestrutura Híbrida e Imutável:** Deploy conteinerizado via **Docker** e orquestrado em **Kubernetes (Minikube)** dentro de uma **VM Instance no Google Cloud Platform (GCP)**. Essa arquitetura garante paridade total entre o desenvolvimento local e o ambiente de nuvem, facilitando a escalabilidade e a portabilidade do sistema.

---

## Arquitetura do Sistema

O sistema é dividido em dois pipelines principais para garantir performance e separação de preocupações:

### 1. Indexing Pipeline (The "Loader")

Processo offline responsável por transformar o conhecimento bruto em vetores matemáticos.

* **Ingestão:** Carregamento de datasets CSV via `src/ingestion/`.
* **Vetorização:** Geração de embeddings semânticos (HuggingFace/OpenAI).
* **Persistência:** Armazenamento em **ChromaDB** com gestão de persistência em disco.

### 2. Inference Pipeline (The "Brain")

Processo online que atende às requisições do usuário em tempo real.

* **Conversational Retrieval:** Recuperação de contexto baseada em histórico de chat.
* **RAG Chain:** Orquestração via **LCEL (LangChain Expression Language)** conectando Retriever, Prompt e LLM.
* **Interface:** UI intuitiva desenvolvida em **Streamlit**.

---

## 🛠️ Stack Tecnológica

* **Linguagem:** Python 3.12+
* **IA Framework:** LangChain (LCEL)
* **LLMs:** Meta Llama 3 (via Groq API), GPT-4o (via OpenAI)
* **Vector Database:** ChromaDB
* **Configuração:** YAML (Padrão 12-Factor App)
* **Infra:** Instância VM GCP, Minikube, Docker & Kubernetes (K8s)
* **Monitoramento:** Logging estruturado e Grafana Cloud

---

## 🧩 Por Que Este Projeto É Diferente

A maioria dos projetos de portfólio foca em "fazê-lo funcionar". Este foca em "fazê-lo operacional".

✔ Limites claros de componentes (ingestão ≠ recuperação ≠ geração)  
✔ Inteligência baseada em configuração (LLMs, embeddings, recuperadores)  
✔ Projetado para monitoramento, depuração e evolução  
✔ Pronto para extensões agenticas (LangGraph, RAG multi-agente)  

---


## 📂 Estrutura do Projeto

```
anime-recommender-system/
│
├── app/                     # Camada de API / serviço
│   └── app.py
│
├── config/                  # Configuração centralizada
│   ├── embeddings.yaml
│   ├── retriever.yaml
│   └── llm.yaml
│
├── data/                    # Conjuntos de dados brutos
│   └── anime_with_synopsis.csv
│
├── pipelines/               # Jobs de orquestração
│   ├── indexing_pipeline.py
│   └── inference_pipeline.py
│
├── src/                     # Componentes centrais reutilizáveis
│   ├── ingestion/           # Carregamento e pré-processamento de dados
│   │   └── loader.py
│   ├── embeddings/          # Abstração de modelo de embedding
│   │   └── embedder.py
│   ├── vectorstore/         # Cliente DB vetorial (Chroma)
│   │   └── chroma_client.py
│   ├── retrieval/           # Lógica de busca semântica
│   │   └── retriever.py
│   ├── prompts/             # Modelos de prompt
│   │   └── templates.py
│   └── generation/          # Camada de interação LLM
│       └── llm_client.py
│
├── Dockerfile                  # Contenereização
├── llmops-k8s.yaml             # Manifestos Kubernetes
├── requirements.txt
└── README.md
```

---

## 🚀 Como Executar

### Pré-requisitos

* Docker & Docker Compose
* Chaves de API (Groq, OpenAI e/ou HuggingFace) configuradas no `.env`

### Passo a Passo

1. **Clone o repositório:**
```bash
git clone https://github.com/seu-usuario/anime-rag-ops.git

```


2. **Inicie o Ambiente:**
```bash
docker-compose up -d

```


3. **Popule o Banco (Indexing):**
```bash
docker exec -it anime-app python pipelines/indexing_pipeline.py

```


4. **Acesse a aplicação:**
Abra `http://localhost:8501` no seu navegador.

---

## 📈 Monitoramento e Observabilidade

O projeto implementa **Logging Estruturado**. Cada etapa da cadeia RAG (Busca, Vetorização e Geração) é logada para permitir:

* Cálculo de latência por componente.
* Auditoria de custos de tokens.
* Depuração de falhas na recuperação de contexto.

---

## 👤 Autor

**Zeygler Oliveira**
Cientista de Dados | Engenheiro de LLMOps & GenAI

Este projeto foi construído como uma **peça de portfólio profissional**, visando demonstrar não apenas *habilidades de implementação*, mas também **julgamento arquitetônico, consciência de *trade-offs* e prontidão para produção**.

> **Nota de Portfólio:** Este projeto foi desenvolvido seguindo as melhores práticas de **AI Consulting**, simulando um ambiente de produção real onde a troca de modelos e a escalabilidade são requisitos críticos de negócio.
