# Notas diárias

Frases no estilo bloco de notas, publicadas automaticamente no Instagram.
A hora na barra do celular e a data da nota são geradas **no momento da publicação** (1–3 min antes).

## Como agendar um post
Edite `agenda.json` (pelo site do GitHub ou pelo app, ícone de lápis) e acrescente um item:

```json
{
  "id": "2026-11-20-exemplo",
  "quando": "2026-11-20 07:00",
  "titulo": "bom dia",
  "frase": "Primeira linha.\n\nSegunda linha.",
  "escuro": false,
  "legenda": "Texto da legenda do post."
}
```

- `id`: único, sem espaço. `quando`: horário de Brasília. `\n\n` separa os parágrafos.
- O robô verifica a cada 10 min. O GitHub às vezes atrasa alguns minutos; a hora na arte acompanha.
- Se passar de 3 h da hora marcada sem sair, o post é marcado como "perdido" (não sai fora de hora).
- O que já saiu fica em `publicados.json`; as artes publicadas ficam em `imagens/`.

## Testar uma arte sem publicar
Aba **Actions** → "Postar nota" → **Run workflow** com "Só gerar a arte" marcado (e o `id`, se quiser).
A arte fica para baixar em "Artifacts" no fim da execução.

## Configuração (uma vez)
Em **Settings → Secrets and variables → Actions**:
- Segredos: `IG_TOKEN` (token de longa duração da API do Instagram com login do Instagram,
  permissões `instagram_business_basic` e `instagram_business_content_publish`) e `IG_USER_ID`.
- Variável: `ARROBA` (ex.: `@eduardovieira`), que aparece no rodapé da nota.
- Opcional: `JANELA_MIN` (padrão 180) e o segredo `GH_PAT`, usado só se a renovação do token devolver um valor novo.

O token é renovado automaticamente nos dias 1 e 15 (workflow "Renovar token do Instagram").
