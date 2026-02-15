# PROJECT MAP – Como o projeto está organizado

## 📦 Backend (API – FastAPI)
Responsável por regras, segurança e dados.

- app/
  - main.py → entrada da API
  - routers/ → endpoints (auth, members, events, worship, admin)
  - schemas/ → validações e contratos
  - core/ → autenticação e dependências
- execution/
  - lógica de negócio (core)
  - scripts de banco e testes
- church_app.db → banco local (dev)

## 🌐 Frontend (Web – Next.js)
Responsável pela experiência do usuário.

- app/
  - páginas (dashboard, admin, worship, etc.)
- components/
  - botões, modais, layouts
- lib/
  - api-client, auth hooks
- messages/
  - traduções (pt-BR, en, es)

## 📄 Documentação
- README.md → como rodar o projeto
- walkthrough.md → visão geral das fases
- APP_MODULES.md → o que existe no app
- PROJECT_MAP.md → como tudo se conecta
