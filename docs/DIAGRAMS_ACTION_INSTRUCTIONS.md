# Instruções: Obter PNGs gerados pela GitHub Action

Este documento descreve passo a passo como abrir um PR para que a workflow `Render PlantUML diagrams` gere os PNGs, como baixar o artefato e como comitar os PNGs no repositório.

Pré-requisitos
- Acesso ao repositório no GitHub
- `git` instalado localmente
- (Opcional) `gh` CLI instalada e autenticada (`gh auth login`)

Passos

1) Criar uma branch local e empurrar (push) para o remoto:

```powershell
Set-Location -Path "c:\Users\rodrigo.eufrasio\Documents\Programação\_Sale.recpires"
git checkout -b add/generated-diagrams
# (Opcional) Faça uma pequena alteração ou crie um commit vazio para acionar a Action
git commit --allow-empty -m "Trigger diagram render workflow"
git push -u origin add/generated-diagrams
```

2) Abrir Pull Request

- Acesse a página do repositório no GitHub e clique em "Compare & pull request" para a branch `add/generated-diagrams`.
- Use o template de PR `diagrams.md` para facilitar a descrição (está em `.github/PULL_REQUEST_TEMPLATE/`).

3) Aguardar a Action rodar

- A workflow `Render PlantUML diagrams` será executada automaticamente.
- Aguarde a execução terminar com sucesso.

4) Baixar artefato (duas opções)

Opção A — pela interface do GitHub
- Vá para a aba "Actions" → clique na execução recente da workflow → role até a seção "Artifacts" e baixe o artefato `diagrams`.

Opção B — pela CLI `gh` (recomendado se tiver `gh` instalado)

```powershell
# Baixa o artefato e extrai em docs/diagrams/generated
gh run download --name diagrams -D docs/diagrams/generated
```

5) Verificar os PNGs e adicioná-los ao repositório local

```powershell
# Verifique os arquivos
Get-ChildItem -Path docs\diagrams\generated -File

# Adicione e comite os PNGs
git add docs/diagrams/generated/*.png
git commit -m "Add generated PlantUML PNGs"
git push origin add/generated-diagrams
```

6) Atualizar o PR

- Os PNGs agora estarão no branch do PR; atualize a descrição se necessário e solicite revisão/merge.

Observações
- A Action usa um runner Linux com Docker para renderizar os PNGs: o processo é idempotente e seguro.
- Se preferir gerar localmente (requer Docker), use os scripts `scripts\render-diagrams.ps1` ou `scripts/render-diagrams.sh`.

---

Se quiser, eu posso criar a branch e abrir o PR (preciso de permissão para push) — ou posso gerar um patch/PR com as instruções e templates prontos (o que já preparei).