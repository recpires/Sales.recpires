---
name: Adicionar diagramas gerados
about: Gerar diagramas PlantUML via GitHub Actions e adicionar os PNGs gerados
---

## Objetivo

Este PR adiciona os PNGs gerados a partir dos diagramas PlantUML em `docs/diagrams/generated/` para facilitar a visualização no repositório.

## O que mudei

- Adicionei PNGs gerados pela workflow `Render PlantUML diagrams`.

## Como reproduzir (se necessário)

1. Crie uma branch e abra um PR — a workflow `Render PlantUML diagrams` será executada automaticamente.
2. Baixe o artefato `diagrams` gerado pela Action.
3. Comite os PNGs em `docs/diagrams/generated/` e faça push para o branch.

## Observações

- Os arquivos fonte `.puml` estão em `docs/diagrams/` e continuam sendo a fonte de verdade.
- Se os diagramas mudarem, reexecute a workflow e atualize os PNGs.

---

/cc @team
