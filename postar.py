#!/usr/bin/env python3
"""Publica as frases estilo Notas no Instagram, com a hora da postagem na arte.

Roda no GitHub Actions (.github/workflows/postar.yml). Para cada post da agenda cuja hora já
chegou e que ainda não saiu: gera a arte NA HORA (barra do celular e data da nota 1–3 min antes
da publicação real), sobe a imagem para imagens/ deste repositório (link público que a Meta busca)
e publica pela API oficial do Instagram (graph.instagram.com).

  python3 postar.py --verificar        diz se há post vencido (o workflow só instala o Remotion se houver)
  python3 postar.py                    publica o post vencido mais antigo
  python3 postar.py --simular [--id X] gera a arte em arte/ sem subir nem publicar
  python3 postar.py --conferir         testa o token: mostra a conta e o limite de publicação
  python3 postar.py --listar           mostra a agenda e o estado de cada post
  python3 postar.py --renovar-token    renova o token (workflow mensal)

Variáveis de ambiente: IG_TOKEN, IG_USER_ID (segredos do GitHub), ARROBA, JANELA_MIN,
GITHUB_REPOSITORY (o Actions preenche). Só biblioteca padrão do Python.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

RAIZ = Path(__file__).resolve().parent
AGENDA = RAIZ / "agenda.json"
ESTADO = RAIZ / "publicados.json"
ARTE = RAIZ / "arte"
IMAGENS = RAIZ / "imagens"
FUSO = ZoneInfo("America/Sao_Paulo")
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]
GRAPH = os.environ.get("GRAPH_BASE", "https://graph.instagram.com").rstrip("/")


def log(msg: str) -> None:
    print(f"[{datetime.now(FUSO):%Y-%m-%d %H:%M:%S}] {msg}", flush=True)


def ler_json(p: Path, padrao):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else padrao


def salvar_estado(estado: dict) -> None:
    ESTADO.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def quando(post: dict) -> datetime:
    return datetime.strptime(post["quando"], "%Y-%m-%d %H:%M").replace(tzinfo=FUSO)


def vencidos(agenda: list, estado: dict, agora: datetime, janela: timedelta, marcar: bool) -> list:
    saida = []
    for p in sorted(agenda, key=quando):
        if p["id"] in estado or quando(p) > agora:
            continue
        if agora - quando(p) > janela:
            if marcar:
                estado[p["id"]] = {"situacao": "perdido", "em": agora.isoformat(timespec="seconds")}
                log(f"PERDIDO {p['id']}: passou {janela} da hora marcada")
            continue
        saida.append(p)
    return saida


def hora_da_nota(post_id: str, agora: datetime) -> datetime:
    # 1 a 3 min antes da publicação real, fixo por post (sem aleatório).
    atraso = 1 + int(hashlib.sha1(post_id.encode()).hexdigest(), 16) % 3
    return agora - timedelta(minutes=atraso)


def renderizar(post: dict, momento: datetime) -> Path:
    ARTE.mkdir(exist_ok=True)
    props = {
        "titulo": post["titulo"],
        "frase": post["frase"],
        "data": f"{momento.day} de {MESES[momento.month - 1]} de {momento.year} às {momento:%H:%M}",
        "hora": f"{momento.hour}:{momento:%M}",
        "escuro": bool(post.get("escuro", False)),
        "arroba": os.environ.get("ARROBA") or "@eduardovieira",
    }
    arq_props = ARTE / f"{post['id']}.props.json"
    arq_props.write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")
    jpg = ARTE / f"{post['id']}_{momento:%Y%m%d_%H%M}.jpg"
    # O Instagram só aceita JPEG.
    subprocess.run(["npx", "remotion", "still", "src/index.ts", "Nota", str(jpg),
                    f"--props={arq_props}", "--image-format=jpeg", "--jpeg-quality=92",
                    "--timeout=120000"], cwd=RAIZ, check=True)
    return jpg


def git(*args: str) -> None:
    subprocess.run(["git", "-C", str(RAIZ), *args], check=True)


def enviar_ao_repo(arquivos: list[Path], mensagem: str) -> None:
    git("add", *[str(a) for a in arquivos])
    git("commit", "-q", "-m", mensagem)
    for tentativa in range(4):  # se alguém editou a agenda no meio, rebase e tenta de novo
        try:
            git("pull", "-q", "--rebase")
            git("push", "-q")
            return
        except subprocess.CalledProcessError:
            time.sleep(3 + tentativa * 3)
    raise RuntimeError("não consegui enviar ao repositório")


def hospedar(jpg: Path) -> str:
    destino = IMAGENS / jpg.name
    destino.write_bytes(jpg.read_bytes())
    enviar_ao_repo([destino], f"imagem {jpg.stem}")
    repo = os.environ["GITHUB_REPOSITORY"]
    url = f"https://raw.githubusercontent.com/{repo}/main/imagens/{urllib.parse.quote(jpg.name)}"
    for _ in range(30):  # espera o link responder antes de mandar para a Meta
        try:
            with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=15) as r:
                if r.status == 200:
                    return url
        except urllib.error.URLError:
            pass
        time.sleep(3)
    raise RuntimeError(f"imagem não ficou pública a tempo: {url}")


def api(metodo: str, caminho: str, **params) -> dict:
    params["access_token"] = os.environ["IG_TOKEN"]
    dados = urllib.parse.urlencode(params)
    if metodo == "GET":
        req = urllib.request.Request(f"{GRAPH}/{caminho}?{dados}")
    else:
        req = urllib.request.Request(f"{GRAPH}/{caminho}", data=dados.encode(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        corpo = e.read().decode(errors="replace").replace(os.environ["IG_TOKEN"], "***")
        raise RuntimeError(f"API {caminho}: HTTP {e.code} {corpo}") from None


def publicar(url: str, legenda: str) -> str:
    uid = os.environ["IG_USER_ID"]
    cont = api("POST", f"{uid}/media", image_url=url, caption=legenda)["id"]
    for _ in range(30):
        st = api("GET", cont, fields="status_code").get("status_code")
        if st == "FINISHED":
            break
        if st in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"container {cont} com status {st}")
        time.sleep(4)
    return api("POST", f"{uid}/media_publish", creation_id=cont)["id"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verificar", action="store_true")
    ap.add_argument("--simular", action="store_true")
    ap.add_argument("--id")
    ap.add_argument("--conferir", action="store_true")
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--renovar-token", action="store_true")
    a = ap.parse_args()

    agenda = ler_json(AGENDA, {"posts": []})["posts"]
    estado = ler_json(ESTADO, {})
    agora = datetime.now(FUSO)
    janela = timedelta(minutes=int(os.environ.get("JANELA_MIN") or "180"))

    if a.listar:
        for p in sorted(agenda, key=quando):
            s = estado.get(p["id"], {}).get("situacao") or ("pendente" if quando(p) > agora else "vencido")
            print(f"{p['quando']}  {s:<10} {p['id']}  — {p['titulo']}")
        return 0

    if a.verificar:
        ha = bool(vencidos(agenda, dict(estado), agora, janela, marcar=False))
        if ha and not (os.environ.get("IG_TOKEN") and os.environ.get("IG_USER_ID")):
            log("há post vencido, mas IG_TOKEN/IG_USER_ID ainda não foram configurados")
            ha = False
        print("sim" if ha else "nao")
        out = os.environ.get("GITHUB_OUTPUT")
        if out:
            with open(out, "a") as f:
                f.write(f"vencido={'sim' if ha else 'nao'}\n")
        return 0

    if a.conferir:
        eu = api("GET", "me", fields="user_id,username")
        print(f"conta: @{eu.get('username')}  id: {eu.get('user_id')}")
        lim = api("GET", f"{os.environ['IG_USER_ID']}/content_publishing_limit", fields="quota_usage,config")
        print("limite de publicação:", json.dumps(lim.get("data", lim), ensure_ascii=False))
        return 0

    if a.renovar_token:
        r = api("GET", "refresh_access_token", grant_type="ig_refresh_token")
        dias = int(r.get("expires_in", 0)) // 86400
        novo = r["access_token"]
        if novo == os.environ["IG_TOKEN"]:
            log(f"token renovado, mesmo valor, vale mais {dias} dias")
        else:
            out = os.environ.get("GITHUB_OUTPUT")
            if out:
                print(f"::add-mask::{novo}")
                with open(out, "a") as f:
                    f.write(f"novo_token={novo}\n")
            log(f"token renovado com valor novo, vale {dias} dias")
        return 0

    if a.id:
        alvo = [p for p in agenda if p["id"] == a.id]
        if not alvo:
            print(f"id não encontrado: {a.id}")
            return 1
    else:
        antes = dict(estado)
        alvo = vencidos(agenda, estado, agora, janela, marcar=not a.simular)
        if estado != antes:
            salvar_estado(estado)
            enviar_ao_repo([ESTADO], "posts perdidos")

    if not alvo:
        log("nada para publicar agora")
        return 0

    p = alvo[0]  # um por execução; se dois venceram juntos, o outro sai na próxima rodada
    momento = hora_da_nota(p["id"], datetime.now(FUSO))
    jpg = renderizar(p, momento)
    if a.simular:
        log(f"SIMULADO {p['id']}: {jpg.name} (nota às {momento:%H:%M})")
        return 0
    url = hospedar(jpg)
    mid = publicar(url, p.get("legenda", ""))
    estado[p["id"]] = {"situacao": "publicado", "media_id": mid,
                       "em": datetime.now(FUSO).isoformat(timespec="seconds"),
                       "hora_na_nota": f"{momento:%H:%M}", "imagem": f"imagens/{jpg.name}"}
    salvar_estado(estado)
    enviar_ao_repo([ESTADO], f"publicado {p['id']}")
    log(f"PUBLICADO {p['id']} (nota às {momento:%H:%M}) media {mid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
