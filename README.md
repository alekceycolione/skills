# Doctor AI Skill Hub

Aplicativo Streamlit para gerenciar Skills de IA localmente e executar queries via Gemini.

## Setup

```bash
cd skill-hub
pip install -r requirements.txt
cp .env.example .env
# Edite .env e adicione sua GEMINI_API_KEY
```

## Estrutura de Skills

Crie pastas dentro de `~/Documents/SkillHub/`:

```
~/Documents/SkillHub/
└── MinhaSkill/
    ├── SKILL.md          # Obrigatório: instruções da IA
    ├── CONTEXT.txt       # Opcional: dados de contexto/RAG
    └── config.json       # Opcional: {"model": "gemini-1.5-flash", "temperature": 0.7}
```

## Executar

```bash
streamlit run app.py
```
