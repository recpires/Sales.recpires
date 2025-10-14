# PR sugerido: Adicionar PNGs gerados dos diagramas PlantUML

Use este texto como corpo do PR ao abrir um Pull Request para adicionar os PNGs gerados dos diagramas.

Título: Adicionar PNGs gerados dos diagramas PlantUML

Descrição:

- Este PR adiciona os PNGs gerados a partir dos arquivos PlantUML que estão em `docs/diagrams/`.
- Os PNGs foram produzidos pela workflow `Render PlantUML diagrams` do GitHub Actions e adicionados em `docs/diagrams/generated/`.

Como as imagens foram produzidas:
- A workflow `Render PlantUML diagrams` executa no GitHub e produz um artefato chamado `diagrams`. Baixei o artefato e comitei os PNGs neste branch.

Arquivos adicionados:
- `docs/diagrams/generated/*.png`

Observações para revisores:
- Os arquivos fonte `.puml` continuam sendo a fonte de verdade. Os PNGs gerados são artefatos de conveniência para visualização rápida no repositório.
- Se os PNGs precisarem ser atualizados, reexecute a workflow empurrando um novo commit ou executando a workflow manualmente.

Comandos que executei localmente (se aplicável):

```powershell
# Baixar artefato usando gh CLI
gh run download --name diagrams -D docs/diagrams/generated
# Comitar os arquivos
git add docs/diagrams/generated/*.png
git commit -m "Add generated PlantUML PNGs"
git push origin add/generated-diagrams
```

Se desejar que eu cuide da criação do PR e do merge, me conceda permissão para dar push a um branch ou me avise que eu preparo o branch e o corpo do PR (a revisão e merge devem ser feitos por você ou por revisores com permissão).
