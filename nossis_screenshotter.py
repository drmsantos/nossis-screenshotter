"""
╔══════════════════════════════════════════════════════════════════╗
║           AutoScreen           ║
╠══════════════════════════════════════════════════════════════════╣
║  Descrição : Faz login no IAM, navega pelo Portal NOSSIS e       ║
║              captura screenshots de todas as opções de menu.     ║
║                                                                  ║
║  Uso       : python3 nossis_screenshotter.py [ambiente] [opções] ║
║                                                                  ║
║  OPÇÕES DISPONÍVEIS                                              ║
║  ─────────────────────────────────────────────────────────────  ║
║  (sem argumentos)                                                ║
║    Abre menu interativo para selecionar o ambiente               ║
║    ex: python3 nossis_screenshotter.py                           ║
║                                                                  ║
║  <ambiente>                                                      ║
║    Executa diretamente no ambiente informado (int, hml, ...)     ║
║    ex: python3 nossis_screenshotter.py int                       ║
║                                                                  ║
║  --dry-run                                                       ║
║    Lista todas as páginas que seriam capturadas sem executar     ║
║    ex: python3 nossis_screenshotter.py int --dry-run             ║
║                                                                  ║
║  --page <nome>                                                   ║
║    Captura apenas a(s) página(s) que contenham o nome informado  ║
║    Separe múltiplas páginas com vírgula                          ║
║    ex: python3 nossis_screenshotter.py int --page OSP            ║
║    ex: python3 nossis_screenshotter.py int --page "OSP,ISP,S&R"  ║
║                                                                  ║
║  --retries <N>                                                   ║
║    Define quantas tentativas extras em caso de falha (padrão: 2) ║
║    ex: python3 nossis_screenshotter.py int --retries 3           ║
║                                                                  ║
║  --compare <dir1> <dir2>                                         ║
║    Compara screenshots entre duas pastas e gera relatório HTML   ║
║    Requer: pip3 install Pillow numpy                             ║
║    ex: python3 nossis_screenshotter.py --compare               ║
║            nossis_prints_int_1.0.7 nossis_prints_int_1.0.8      ║
║                                                                  ║
║  --all-envs                                                      ║
║    Executa em todos os ambientes em sequência                    ║
║    ex: python3 nossis_screenshotter.py --all-envs                ║
║                                                                  ║
║  --since <pasta>                                                 ║
║    Captura só páginas que mudaram desde a última execução        ║
║    ex: python3 nossis_screenshotter.py int --since nossis_prints_int_1.0.7 ║
║                                                                  ║
║  Autor     : Diego Santos <diego-f-santos@openlabs.com.br>       ║
║  Versão    : 7.0                                                 ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║  CHANGELOG                                                       ║
╠══════════════════════════════════════════════════════════════════╣
║  v7.1  · Multi-thread automático por volume de páginas           ║
║           < 10 pág → 1 thread | 10-29 → 2 | ≥ 30 → 3 threads   ║
║        · Barra de progresso por thread (Rich, cores distintas)   ║
║        · Sessão TTL de 30 min — renova login automaticamente     ║
║        · Detecção de sessão expirada via HTTP 401/403            ║
║        · PDF gerado via Pillow — sem dependência de weasyprint   ║
║        · PDF fundo branco, padrão ABNT NBR 14724                 ║
║           Margens: sup 3cm | inf 2cm | esq 3cm | dir 2cm        ║
║           Fonte: Liberation Sans 12pt | Entrelinhas: 1,5x        ║
║           Numeração: canto superior direito (sec. 5.3)           ║
║        · Validação dupla de screenshot:                          ║
║           Camada 1 — DOM: spinner, aria-busy, URL, conteúdo      ║
║           Camada 2 — Imagem: variância, % branco, spinner visual ║
║        · Status NOK quando página não carrega após retries       ║
║        · Retry com backoff progressivo (1s, 2s, 3s...)           ║
║        · Bloqueio de recursos desnecessários (fontes, analytics) ║
║        · Browser com 12 flags de performance                     ║
║        · WAIT_UNTIL=domcontentloaded (mais rápido que load)      ║
║        · wait_for_page_ready inteligente (só espera spinner real)║
║        · animations=disabled no screenshot                       ║
║        · Silencia warnings internos do Playwright                ║
║        · Detecção de versão com 3 níveis de fallback             ║
║        · Tempo extra por página configurável (EXTRA_WAIT)        ║
║                                                                  ║
║  v6.0  · Sessão/cookies salva e reutilizada entre execuções      ║
║        · Detecção de submenus expandidos (hover)                 ║
║        · Log embutido no HTML do relatório                       ║
║        · README.txt gerado na pasta de saída                     ║
║        · Modo --all-envs (todos os ambientes em sequência)       ║
║        · Modo --since (só páginas que mudaram)                   ║
║        · Detecção de erros 4xx/5xx via console do browser        ║
║                                                                  ║
║  v5.0  · Retry automático (--retries N)                          ║
║        · Screenshot parcial em caso de erro                      ║
║        · Validação pós-screenshot (URL, título, tamanho)         ║
║        · Relatório HTML com grid de imagens e badges de status   ║
║        · Modo --dry-run (lista páginas sem capturar)             ║
║        · Modo --page (captura página(s) específica(s))           ║
║        · Comparação visual entre execuções (--compare)           ║
║                                                                  ║
║  v4.0  · Menu Rich interativo com banner ASCII                   ║
║        · Suporte a múltiplos ambientes (INT, HML, ...)           ║
║        · Pasta de saída com versão extraída do modal Sobre       ║
║        · Pasta com timestamp se já existir                       ║
║        · Logging completo em logs/nossis_<env>_<ts>.log          ║
║        · Barra de progresso Rich durante capturas                ║
║                                                                  ║
║  v3.0  · Multi-ambiente via argumento CLI ou menu interativo      ║
║        · Pasta separada por ambiente                             ║
║                                                                  ║
║  v2.0  · Login IAM multi-step (username → next → password)       ║
║        · Clique no card NETWIN + link início                     ║
║        · Modal Sobre como primeiro print                         ║
║        · Spinner de carregamento — aguarda "A carregar página"   ║
║        · Tempo extra configurável por página (OSP, Viabilidade)  ║
║        · Skip de páginas por label ou URL                        ║
║        · Screenshots de debug em cada etapa do login             ║
╚══════════════════════════════════════════════════════════════════╝
"""

import re
import sys
import time
import socket
import logging
import argparse
import hashlib
import base64
import subprocess
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright, Page

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_STAMP = True
except ImportError:
    PIL_STAMP = False

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.text import Text
    from rich import box
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.align import Align
    RICH = True
except ImportError:
    RICH = False

try:
    from PIL import Image, ImageChops
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

console = Console() if RICH else None


# ══════════════════════════════════════════════════════════════════
# VALIDAÇÃO DE CONECTIVIDADE
# ══════════════════════════════════════════════════════════════════

def check_connectivity(env: dict) -> tuple[bool, str]:
    """
    Verifica se o IAM e o Portal estão acessíveis.
    Retorna (ok, mensagem).
    """
    results = []
    all_ok  = True

    for name, url in [("IAM", env["iam_url"]), ("Portal", env["portal_url"])]:
        parsed = urlparse(url)
        host   = parsed.hostname
        port   = parsed.port or (443 if parsed.scheme == "https" else 80)
        try:
            sock = socket.create_connection((host, port), timeout=5)
            sock.close()
            results.append(f"   ✓ {name} — {host}:{port} acessível")
            log.info(f"Conectividade OK: {name} {host}:{port}")
        except (socket.timeout, socket.gaierror, ConnectionRefusedError, OSError) as e:
            results.append(f"   ✗ {name} — {host}:{port} inacessível ({type(e).__name__})")
            log.error(f"Conectividade FALHOU: {name} {host}:{port} — {e}")
            all_ok = False

    msg = "\n".join(results)
    return all_ok, msg


def validate_connectivity(env: dict):
    """Valida conectividade e encerra com mensagem clara se falhar."""
    if RICH:
        console.print(f"\n[bold cyan]🔌 Verificando conectividade...[/bold cyan]")
    else:
        print("\n🔌 Verificando conectividade...")

    ok, msg = check_connectivity(env)

    if RICH:
        console.print(msg.replace("✓", "[green]✓[/green]").replace("✗", "[red]✗[/red]"))
    else:
        print(msg)

    if not ok:
        if RICH:
            msg_panel = (
                "[bold red]Não foi possível conectar aos serviços NOSSIS.[/bold red]\n\n"
                "[yellow]Possíveis causas:[/yellow]\n"
                "  • VPN não está conectada\n"
                "  • Ambiente fora do ar\n"
                "  • IP ou hostname incorreto\n\n"
                "[dim]Verifique sua conexão VPN e tente novamente.[/dim]"
            )
            console.print(Panel(
                msg_panel,
                title="[red]❌ Falha de Conectividade[/red]",
                border_style="red", padding=(1, 2)
            ))
        else:
            print("\n❌ Falha de Conectividade!")
            print("   Possíveis causas:")
            print("   • VPN não está conectada")
            print("   • Ambiente fora do ar")
            print("   • IP ou hostname incorreto")
        sys.exit(1)

    if RICH:
        console.print(f"   [green]✓ Conectividade OK[/green]\n")
    else:
        print("   ✓ Conectividade OK\n")


# ══════════════════════════════════════════════════════════════════
# WATERMARK — data/hora nos prints
# ══════════════════════════════════════════════════════════════════

def add_timestamp_watermark(filepath: Path, label: str):
    """Adiciona watermark com data/hora e label no canto do screenshot."""
    if not PIL_STAMP:
        return  # Pillow não instalado, ignora silenciosamente

    try:
        img  = Image.open(filepath).convert("RGBA")
        draw = ImageDraw.Draw(img)
        now  = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        text = f"  {label}  |  {now}  "
        W, H = img.size

        # Tenta usar fonte monospace, fallback para default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 18)
        except Exception:
            font = ImageFont.load_default()

        # Mede o texto
        bbox = draw.textbbox((0, 0), text, font=font)
        tw   = bbox[2] - bbox[0]
        th   = bbox[3] - bbox[1]
        pad  = 8

        # Fundo semitransparente no canto inferior esquerdo
        bar_x0 = 0
        bar_y0 = H - th - pad * 2
        bar_x1 = tw + pad * 2
        bar_y1 = H

        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ov_draw = ImageDraw.Draw(overlay)
        ov_draw.rectangle([bar_x0, bar_y0, bar_x1, bar_y1], fill=(0, 0, 0, 180))
        img = Image.alpha_composite(img, overlay)

        # Texto branco
        draw = ImageDraw.Draw(img)
        draw.text((pad, bar_y0 + pad), text, font=font, fill=(0, 200, 224, 255))

        img.convert("RGB").save(filepath, "PNG", optimize=False)
        log.debug(f"Watermark adicionado: {filepath.name}")
    except Exception as e:
        log.warning(f"Watermark falhou em {filepath.name}: {e}")



# ══════════════════════════════════════════════════════════════════
# SESSÃO / COOKIES
# ══════════════════════════════════════════════════════════════════

def save_session(context, env_key: str):
    """Salva cookies e storage da sessão para reusar no próximo run."""
    try:
        SESSION_DIR.mkdir(exist_ok=True)
        session_file = SESSION_DIR / f"session_{env_key}.json"
        storage = context.storage_state()
        import json
        session_file.write_text(json.dumps(storage), encoding="utf-8")
        log.info(f"Sessão salva: {session_file}")
        print_ok(f"Sessão salva → {session_file}")
    except Exception as e:
        log.warning(f"Não foi possível salvar sessão: {e}")


def load_session(env_key: str) -> dict | None:
    """Carrega sessão salva se existir e for recente (< SESSION_TTL)."""
    try:
        session_file = SESSION_DIR / f"session_{env_key}.json"
        if not session_file.exists():
            return None
        age = time.time() - session_file.stat().st_mtime
        if age > SESSION_TTL:
            mins = int(SESSION_TTL // 60)
            log.info(f"Sessão expirada (>{mins} min) — novo login necessário")
            session_file.unlink(missing_ok=True)
            return None
        remaining = int((SESSION_TTL - age) // 60)
        log.info(f"Sessão carregada: {session_file} (idade: {age/60:.0f} min, expira em {remaining} min)")
        data = json.loads(session_file.read_text(encoding="utf-8"))
        return data
    except Exception as e:
        log.warning(f"Não foi possível carregar sessão: {e}")
        return None


def clear_session(env_key: str):
    """Remove sessão salva."""
    try:
        f = SESSION_DIR / f"session_{env_key}.json"
        if f.exists():
            f.unlink()
            log.info(f"Sessão removida: {f}")
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════
# HASH DE SCREENSHOTS (para --since)
# ══════════════════════════════════════════════════════════════════

def file_hash(path: Path) -> str:
    """Retorna MD5 do arquivo."""
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()
    except Exception:
        return ""


def load_hashes(since_dir: Path) -> dict[str, str]:
    """Carrega mapa label→hash da pasta de referência."""
    hashes = {}
    for png in since_dir.glob("*.png"):
        if not png.name.startswith("debug_") and not png.name.startswith("PARCIAL_"):
            hashes[png.stem] = file_hash(png)
    return hashes


def screenshot_changed(filepath: Path, ref_hashes: dict) -> bool:
    """Retorna True se o screenshot mudou em relação à referência."""
    if not ref_hashes:
        return True
    stem = filepath.stem
    ref  = ref_hashes.get(stem)
    if not ref:
        return True  # página nova — captura
    # Tira screenshot temporário para comparar
    return True  # sempre captura, compara após


def compare_with_ref(filepath: Path, ref_dir: Path) -> bool:
    """Compara screenshot gerado com o de referência. Retorna True se mudou."""
    ref_path = ref_dir / filepath.name
    if not ref_path.exists():
        return True
    return file_hash(filepath) != file_hash(ref_path)


# ══════════════════════════════════════════════════════════════════
# DETECÇÃO DE ERROS HTTP (console do browser)
# ══════════════════════════════════════════════════════════════════

def setup_console_listener(page: Page, label_ref: list):
    """Configura listener de erros HTTP e console no browser."""
    http_errors = []

    def on_response(response):
        if response.status >= 400:
            msg = f"HTTP {response.status} em {response.url}"
            http_errors.append(msg)
            log.warning(f"[{label_ref[0]}] {msg}")

    def on_console(msg):
        if msg.type in ("error", "warning"):
            log.debug(f"[{label_ref[0]}] console.{msg.type}: {msg.text[:120]}")

    page.on("response", on_response)
    page.on("console",  on_console)
    return http_errors


# ══════════════════════════════════════════════════════════════════
# README.txt
# ══════════════════════════════════════════════════════════════════

def generate_readme(output_dir: Path, env: dict, version_tag: str,
                    results: list, elapsed: float, rep_path: Path, pdf_path):
    """Gera README.txt explicando o conteúdo da pasta."""
    now  = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    ok   = sum(1 for r in results if r["status"] == "ok")
    warn = sum(1 for r in results if r["status"] == "aviso")
    err  = sum(1 for r in results if r["status"] == "erro")

    lines = [
        "=" * 65,
        "  AutoScreen",
        "=" * 65,
        "",
        f"  Ambiente  : {env['name']}",
        f"  Versão    : {version_tag}",
        f"  Gerado em : {now}",
        f"  Duração   : {elapsed/60:.1f} min ({elapsed:.0f}s)",
        f"  Autor     : Diego Santos · diego-f-santos@openlabs.com.br",
        "",
        "-" * 65,
        "  RESUMO",
        "-" * 65,
        f"  ✓ OK     : {ok}",
        f"  ⚠ Avisos : {warn}",
        f"  ✗ Erros  : {err}",
        f"  Total    : {ok + warn + err}",
        "",
        "-" * 65,
        "  ARQUIVOS",
        "-" * 65,
        "  relatorio_*.html  → Relatório completo com todas as evidências",
    ]
    if pdf_path:
        lines.append("  relatorio_*.pdf   → Relatório em PDF para impressão/envio")
    lines += [
        "  00_sobre.png      → Modal 'Sobre' com versão do sistema",
        "  debug_*.png       → Screenshots de debug do fluxo de login",
        "  PARCIAL_*.png     → Screenshots parciais de páginas com erro",
        "",
        "-" * 65,
        "  PÁGINAS CAPTURADAS",
        "-" * 65,
    ]
    for i, r in enumerate(results, 1):
        icon = {"ok": "✓", "aviso": "⚠", "erro": "✗"}.get(r["status"], "?")
        msg  = f"  [{r.get('msg','')[:40]}]" if r.get("msg") else ""
        lines.append(f"  {icon} {i:02d}. {r['label']:<30} {r.get('time','—'):>6}{msg}")

    lines += [
        "",
        "=" * 65,
        "  Gerado por NOSSIS AutoScreen v7.1",
        "=" * 65,
    ]

    readme_path = output_dir / "README.txt"
    readme_path.write_text("\n".join(lines), encoding="utf-8")
    log.info(f"README gerado: {readme_path}")
    return readme_path


# ══════════════════════════════════════════════════════════════════
# AMBIENTES
# ══════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════
# SISTEMAS E MÓDULOS
# ══════════════════════════════════════════════════════════════════
# Estrutura: cada SISTEMA tem um IAM e credenciais.
# Cada sistema pode ter N MÓDULOS (cards no IAM que abrem portais).
#
# Para adicionar novo sistema: crie uma nova entrada em SYSTEMS.
# Para adicionar novo módulo:  adicione em "modules" do sistema.
#
# Uso CLI:
#   python3 nossis_screenshotter.py                    # menu interativo
#   python3 nossis_screenshotter.py hml netwin         # sistema + módulo direto
#   python3 nossis_screenshotter.py hml --all-modules  # todos os módulos do sistema

SYSTEMS = {
    "int": {
        "name":     "INT — Dev (V.Tal)",
        "iam_url":  "https://iam-dev-vtal.10.51.195.98.nip.io/idp/login",
        "username": "netwin",
        "password": "netwin",
        "modules": {
            "netwin": {
                "name":        "NETWIN",
                "portal_url":  "https://netwin-dev-vtal.10.51.195.98.nip.io/portal",
                "module":      "NETWIN",
                "inicio_link": "/portal",
            },
            # "sigo": {
            #     "name":        "SIGO",
            #     "portal_url":  "https://sigo-dev-vtal.10.51.195.98.nip.io/",
            #     "module":      "SIGO",
            #     "inicio_link": "/",
            # },
        },
    },
    "hml": {
        "name":     "HML — Dev (OCP Arc)",
        "iam_url":  "https://iam-nossis-dev.apps.ocparc-nprd.vtal.intra/idp/login",
        "username": "netwin",
        "password": "Netwin123456!!",
        "modules": {
            "netwin": {
                "name":        "NETWIN",
                "portal_url":  "https://netwin-nossis-dev.apps.ocparc-nprd.vtal.intra/portal",
                "module":      "NETWIN",
                "inicio_link": "/portal",
            },
            # "sigo": {
            #     "name":        "SIGO",
            #     "portal_url":  "https://sigo-nossis-dev.apps.ocparc-nprd.vtal.intra/",
            #     "module":      "SIGO",
            #     "inicio_link": "/",
            # },
            # "alarmmgr": {
            #     "name":        "ALARMMGR",
            #     "portal_url":  "https://alarmmgr-nossis-dev.apps.ocparc-nprd.vtal.intra/",
            #     "module":      "ALARMMGR",
            #     "inicio_link": "/",
            # },
        },
    },
}

# Compatibilidade: gera ENVIRONMENTS flat a partir de SYSTEMS
# Chave: "<sistema>-<modulo>" ex: "hml-netwin", "hml-sigo"
ENVIRONMENTS = {}
for sys_key, sys_val in SYSTEMS.items():
    for mod_key, mod_val in sys_val["modules"].items():
        env_key = f"{sys_key}-{mod_key}"
        ENVIRONMENTS[env_key] = {
            "name":        f"{mod_val['name']} — {sys_val['name']}",
            "iam_url":     sys_val["iam_url"],
            "portal_url":  mod_val["portal_url"],
            "username":    sys_val["username"],
            "password":    sys_val["password"],
            "module":      mod_val["module"],
            "inicio_link": mod_val.get("inicio_link", "/portal"),
            # metadados para o menu
            "_system":     sys_key,
            "_system_name":sys_val["name"],
            "_module":     mod_key,
        }
    # Atalho simples: "hml" → "hml-netwin" (primeiro módulo)
    first_mod = next(iter(sys_val["modules"]))
    ENVIRONMENTS[sys_key] = ENVIRONMENTS[f"{sys_key}-{first_mod}"]

# Exemplos de novos sistemas:
# SYSTEMS["prd"] = {
#     "name":     "PRD — Producao",
#     "iam_url":  "https://iam-prd.vtal.intra/idp/login",
#     "username": "netwin",
#     "password": "senha_prd",
#     "modules": {
#         "netwin":   {"name": "NETWIN",   "portal_url": "https://netwin-prd.vtal.intra/portal", "module": "NETWIN",   "inicio_link": "/portal"},
#         "sigo":     {"name": "SIGO",     "portal_url": "https://sigo-prd.vtal.intra/",         "module": "SIGO",     "inicio_link": "/"},
#         "alarmmgr": {"name": "ALARMMGR", "portal_url": "https://alarmmgr-prd.vtal.intra/",     "module": "ALARMMGR", "inicio_link": "/"},
#     },
# }

ENVIRONMENTS_ORIG = {  # mantém para --all-envs sem duplicatas
    k: v for k, v in ENVIRONMENTS.items()
    if "-" in k  # só chaves compostas ex: hml-netwin
}


# ══════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO GERAL
# ══════════════════════════════════════════════════════════════════
SELECTOR_MENU = "nav a, .menu a, #menu a, .sidebar a, [class*='menu'] a, [class*='nav'] a"
TIMEOUT       = 60_000   # 60s — mais agressivo; páginas lentas caem em retry
WAIT_UNTIL    = "domcontentloaded"  # mais rápido que "load"; não espera imagens/fontes externas
MAX_RETRIES   = 2

SKIP_LABELS   = ["outros módulos", "outros modulos", "segurança", "seguranca", "Funções assurance", "funcoes assurance"]
SKIP_URLS     = ["/portal#", "/portal/home", "/portal/outros"]

EXTRA_WAIT    = {
    # Páginas com mapa / GIS — carregamento pesado
    "OSP":                       10_000,
    "GISMaps":                    8_000,
    "Viabilidade":               12_000,

    # Páginas com spinner lento
    "ISP":                        5_000,
    "Visao dominio de rede":      5_000,
    "Visão domínio de rede":      5_000,
    "Armazem":                    5_000,
    "Armazém":                    5_000,
    "CPEs":                       5_000,
    "S&R":                        5_000,
    "Operacoes":                  5_000,
    "Operações":                  5_000,
    "Historico":                  5_000,
    "Histórico":                  5_000,
    "PROJETOS":                   5_000,
    "Locations":                  5_000,
    "Outside Plant":              5_000,
    "Inside Plant":               5_000,
    "Templates de equipamentos":  8_000,

    # Páginas com carregamento lento adicional
    "Recursos":                   5_000,
    "Servicos":                   5_000,
    "Serviços":                   5_000,
    "Entidades":                  5_000,

    # Paginas com carregamento muito lento
    "Armazem":                    8_000,
    "Armazém":                    8_000,
    "Reserva":                    8_000,
}

# ── Validação por texto esperado na tela ──────────────────────────
# Para cada página, define palavras-chave que DEVEM aparecer no DOM
# quando a página carregou corretamente.
# A validação é case-insensitive e basta UMA das palavras estar presente.
# Se nenhuma for encontrada → página não carregou → retry automático.
PAGE_CONTENT_CHECK = {
    "Sobre":                    ["NOSSIS ONE INVENTORY", "Versão", "Produto"],
    "Início":                   ["NOSSIS ONE INVENTORY", "Principais funcionalidades"],
    "LOCAIS":                   ["Locais físicos", "Pesquisa", "Location Manager"],
    "Locais físicos":           ["Locais físicos", "Total de registros", "Pesquisa"],
    "Divisões administrativas": ["Divisões administrativas", "Total de registros"],
    "Roteiro de endereços":     ["Roteiro de endereços", "Roteiro Brasil"],
    "OSP":                      ["OSP", "Elemento", "BRASIL"],
    "GISMaps":                  ["GISMaps", "localization", "Contexto de trabalho"],
    "ISP":                      ["ISP", "Elemento", "BRASIL"],
    "Visão domínio de rede":    ["Visão domínio", "Raiz", "Elemento"],
    "Armazém":                  ["Armazém", "Armazem", "Entidade"],
    "CPEs":                     ["CPEs", "Equipamento", "Taxonomia"],
    "S&R":                      ["S&R", "Entidade"],
    "Recursos":                 ["Recursos", "Pesquisa"],
    "Serviços":                 ["Serviços", "Servicos", "Pesquisa"],
    "Fibra ponto a ponto":      ["Fibra ponto", "Caminhos ópticos", "ORIGEM"],
    "Viabilidade":              ["Viabilidade", "Endereço", "Pesquisar"],
    "Reserva":                  ["Reserva", "Entidade"],
    "Gestão de ordens":         ["Gestão de ordens", "Pesquisa", "Serviço"],
    "Operações":                ["Operações", "Pesquisar", "Estação"],
    "Histórico":                ["Histórico", "Historico", "Operação"],
    "Carregamento Massivo":     ["Ações massivas", "Massivo", "importar"],
    "TOPOLOGIAS":               ["TOPOLOGIAS", "Topologia", "Hierarquia"],
    "PROJETOS":                 ["PROJETOS", "Projeto", "Pesquisa"],
    "Locations":                ["Locations", "Relatórios Pré-Gravados", "Pesquisa"],
    "Outside Plant":            ["Outside Plant", "Relatórios Pré-Gravados"],
    "Inside Plant":             ["Inside Plant", "Relatórios Pré-Gravados"],
    "Modelo de Cabos":          ["Modelo de Cabos", "Modelos de Cabos", "navegação"],
    "Inicializações":           ["Inicializações", "Configuração", "confirmar"],
    "Templates de equipamentos":["Templates de equipamentos", "Tipo do Equipamento"],
    "Entidades":                ["Entidades", "Pesquisa de registros", "Aplicação"],
    "CPE":                      ["CPE", "Tipo de Entidade", "Pesquisa"],
}

# Recursos a bloquear — reduz tráfego e acelera carregamento das páginas
BLOCKED_RESOURCES = ["media"]  # bloqueia vídeos (fontes liberadas — necessárias para ícones)
BLOCKED_DOMAINS   = [                  # bloqueia domínios de analytics/tracking
    "google-analytics.com", "googletagmanager.com",
    "hotjar.com", "sentry.io", "amplitude.com",
    "segment.io", "mixpanel.com",
]


def _launch_optimized_browser(playwright_instance, headless: bool = True):
    """Lança Chromium com flags de performance."""
    return playwright_instance.chromium.launch(
        headless=headless,
        args=[
            "--no-sandbox",
            "--ignore-certificate-errors",
            "--disable-web-security",
            "--disable-dev-shm-usage",       # evita crash em ambientes com pouca memória
            "--disable-gpu",                  # sem GPU em headless
            "--disable-extensions",
            "--disable-background-networking",
            "--disable-sync",
            "--disable-translate",
            "--disable-default-apps",
            "--no-first-run",
            "--no-default-browser-check",
            "--mute-audio",
        ]
    )


def _new_optimized_context(browser, session_data: dict | None = None):
    """Cria contexto com cache habilitado, bloqueio de recursos e sessão opcional."""
    ctx_args = dict(
        viewport={"width": 1920, "height": 1080},
        ignore_https_errors=True,
        java_script_enabled=True,
        bypass_csp=True,
    )
    if session_data:
        ctx_args["storage_state"] = session_data

    ctx = browser.new_context(**ctx_args)

    # Bloqueia recursos desnecessários para acelerar carregamento
    def _route_handler(route):
        req = route.request
        # Bloqueia por tipo de recurso
        if req.resource_type in BLOCKED_RESOURCES:
            route.abort()
            return
        # Bloqueia por domínio
        if any(d in req.url for d in BLOCKED_DOMAINS):
            route.abort()
            return
        route.continue_()

    ctx.route("**/*", _route_handler)
    return ctx

# Arquivo de sessão salva
SESSION_DIR = Path(".nossis_sessions")
SESSION_TTL = 30 * 60  # 30 minutos — renova login automaticamente após esse tempo

# Indicadores de página com erro/branca/login
ERROR_INDICATORS = [
    "idp/login", "error", "404", "403", "unauthorized",
    "access denied", "página não encontrada",
]


# ══════════════════════════════════════════════════════════════════
# LOGGER
# ══════════════════════════════════════════════════════════════════

log: logging.Logger = logging.getLogger("nossis")


def setup_logger(env_key: str):
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file  = log_dir / f"nossis_{env_key}_{timestamp}.log"

    log.setLevel(logging.DEBUG)
    log.handlers.clear()

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    log.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    log.addHandler(ch)

    # Silencia loggers internos do Playwright (evita "WARNING: [] HTTP 4xx" no terminal)
    for pw_logger in ("playwright", "playwright._impl", "asyncio"):
        logging.getLogger(pw_logger).setLevel(logging.ERROR)

    log.info("=" * 70)
    log.info("NOSSIS AutoScreen v7.1")
    log.info(f"Ambiente : {env_key.upper()}")
    log.info(f"Log      : {log_file.resolve()}")
    log.info("=" * 70)

    return log_file


# ══════════════════════════════════════════════════════════════════
# OUTPUT HELPERS
# ══════════════════════════════════════════════════════════════════

def print_info(msg):
    log.info(msg)
    if RICH: console.print(f"[cyan]   →[/cyan] {msg}")
    else: print(f"   → {msg}")

def print_ok(msg):
    log.info(f"✓ {msg}")
    if RICH: console.print(f"[green]   ✓[/green] {msg}")
    else: print(f"   ✓ {msg}")

def print_warn(msg):
    log.warning(msg)
    if RICH: console.print(f"[yellow]   ⚠[/yellow]  {msg}")
    else: print(f"   ⚠  {msg}")

def print_err(msg):
    log.error(msg)
    if RICH: console.print(f"[red]   ✗[/red] {msg}")
    else: print(f"   ✗ {msg}")


# ══════════════════════════════════════════════════════════════════
# MENU / BANNER
# ══════════════════════════════════════════════════════════════════

def show_banner(env: dict, output_dir: Path):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    if RICH:
        content = (
            f"[bold cyan]Ambiente :[/bold cyan] {env['name']}\n"
            f"[bold cyan]Início   :[/bold cyan] {now}\n"
            f"[bold cyan]Saída    :[/bold cyan] {output_dir}\n"
            f"[bold cyan]Autor    :[/bold cyan] Diego Santos · diego-f-santos@openlabs.com.br"
        )
        console.print(Panel(content,
            title="[bold white]AutoScreen v7.1[/bold white]",
            border_style="cyan", padding=(1, 2)))
    else:
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║       AutoScreen v7.1         ║")
        print(f"║  Ambiente : {env['name']:<53}║")
        print(f"║  Início   : {now:<53}║")
        print(f"║  Saída    : {str(output_dir):<53}║")
        print("╚══════════════════════════════════════════════════════════════════╝")
    print()


def parse_args():
    """Parse argumentos CLI."""
    parser = argparse.ArgumentParser(
        description="NOSSIS AutoScreen v7.1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python3 nossis_screenshotter.py int
  python3 nossis_screenshotter.py hml --dry-run
  python3 nossis_screenshotter.py int --page OSP
  python3 nossis_screenshotter.py int --page "OSP,ISP,S&R"
  python3 nossis_screenshotter.py --compare nossis_prints_int_1.0.7 nossis_prints_int_1.0.8
        """
    )
    parser.add_argument("env",         nargs="?",  help="Ambiente (int, hml, ...)")
    parser.add_argument("--dry-run",   action="store_true", help="Lista páginas sem capturar")
    parser.add_argument("--page",      type=str,   help="Captura só página(s) específica(s). Ex: --page OSP ou --page 'OSP,ISP'")
    parser.add_argument("--compare",   nargs=2,    metavar=("DIR1", "DIR2"), help="Compara screenshots entre duas pastas")
    parser.add_argument("--retries",   type=int,   default=MAX_RETRIES, help=f"Tentativas em caso de falha (padrão: {MAX_RETRIES})")
    parser.add_argument("--all-envs",  action="store_true", help="Executa em todos os ambientes em sequência")
    parser.add_argument("--since",     type=str,   metavar="DIR", help="Captura só páginas que mudaram desde DIR")
    parser.add_argument("--no-session",action="store_true", help="Ignora sessão salva e faz login do zero")
    return parser.parse_args()


def _show_banner():
    if not RICH:
        return
    banner_text = (
        "[bold cyan]    ___         __       _____                                [/bold cyan]\n"
        "[bold cyan]   /   | __  __/ /_____ / ___/_____________  ___  ____        [/bold cyan]\n"
        "[bold cyan]  / /| |/ / / / __/ __ \\__ \\/  ___/ ___/ _ \\/ _ \\/ __ \\  [/bold cyan] \n"
        "[bold cyan] / ___ / /_/ / /_/ /_/ /__/ / /__/ /  /  __/  __/ / / /       [/bold cyan]\n"
        "[bold cyan]/_/  |_\\__,_/\\__/\\____/____/\\___/_/   \\___/\\___/_/ /_/   [/bold cyan]\n"
        "\n"
        "[bold white]AutoScreen[/bold white] [dim]v7.1  ·  Diego Santos · diego-f-santos@openlabs.com.br[/dim]"
    )
    W = 120
    console.print()
    console.print(Panel(Align.center(banner_text), border_style="cyan", padding=(1, 4), width=W))
    console.print()


def _pick_system() -> tuple[str, dict]:
    """Passo 1: seleciona o sistema (INT, HML, PRD...)."""
    sys_keys = list(SYSTEMS.keys())

    if RICH:
        W = 120
        table = Table(box=box.ROUNDED, border_style="cyan", show_header=True,
                      header_style="bold cyan", padding=(0, 2), show_lines=True, width=W)
        table.add_column("#",       style="bold white",  justify="center", width=5,  no_wrap=True)
        table.add_column("Chave",   style="bold yellow", justify="center", width=10, no_wrap=True)
        table.add_column("Sistema", style="white",       justify="left",   width=40, no_wrap=True)
        table.add_column("IAM",     style="cyan",        justify="left",   width=55, no_wrap=True)

        for i, (k, s) in enumerate(SYSTEMS.items(), 1):
            mods = ", ".join(s["modules"].keys())
            table.add_row(str(i), k.upper(), s["name"], s["iam_url"].replace("/idp/login",""))
        table.add_section()
        table.add_row("[dim]0[/dim]", "[dim]---[/dim]", "[dim]Sair[/dim]", "")
        console.print(table)
        console.print()

        while True:
            try:
                choice = Prompt.ask(f"[bold cyan]Selecione o sistema[/bold cyan] [dim](0-{len(sys_keys)})[/dim]", default="0")
                idx = int(choice)
                if idx == 0:
                    console.print("\n[dim]Encerrando...[/dim]"); sys.exit(0)
                if 1 <= idx <= len(sys_keys):
                    key = sys_keys[idx - 1]
                    return key, SYSTEMS[key]
                console.print(f"[red]Opção inválida.[/red] Digite 0 a {len(sys_keys)}.")
            except (ValueError, EOFError):
                console.print("[red]Opção inválida.[/red]")
            except KeyboardInterrupt:
                console.print("\n[dim]Interrompido.[/dim]"); sys.exit(0)
    else:
        print("\n┌──────────────────────────────────────────┐")
        print("│   Selecione o sistema                     │")
        print("├──────────────────────────────────────────┤")
        for i, (k, s) in enumerate(SYSTEMS.items(), 1):
            print(f"│  {i}. {k.upper():<8}  {s['name']:<28} │")
        print("│  0.  Sair                                 │")
        print("└──────────────────────────────────────────┘")
        while True:
            try:
                idx = int(input(f"\nOpção [0-{len(sys_keys)}]: ").strip())
                if idx == 0: sys.exit(0)
                if 1 <= idx <= len(sys_keys):
                    k = sys_keys[idx - 1]
                    return k, SYSTEMS[k]
            except (ValueError, EOFError): pass
            except KeyboardInterrupt: sys.exit(0)
            print("Opção inválida.")


def _pick_module(sys_key: str, system: dict) -> tuple[str, dict]:
    """Passo 2: seleciona o módulo dentro do sistema escolhido."""
    mod_keys = list(system["modules"].keys())

    if RICH:
        W = 120
        console.print()
        table = Table(box=box.ROUNDED, border_style="cyan", show_header=True,
                      header_style="bold cyan", padding=(0, 2), show_lines=True, width=W)
        table.add_column("#",       style="bold white",  justify="center", width=5,  no_wrap=True)
        table.add_column("Módulo",  style="bold yellow", justify="center", width=14, no_wrap=True)
        table.add_column("Nome",    style="white",       justify="left",   width=20, no_wrap=True)
        table.add_column("Portal",  style="cyan",        justify="left",   width=71, no_wrap=True)

        for i, (k, m) in enumerate(system["modules"].items(), 1):
            table.add_row(str(i), k.upper(), m["name"], m["portal_url"])
        table.add_section()
        table.add_row("[dim]0[/dim]", "[dim]TODOS[/dim]", "[dim]Capturar todos os módulos[/dim]", "")
        table.add_row("[dim]V[/dim]", "[dim]---[/dim]",   "[dim]Voltar[/dim]", "")
        console.print(table)
        console.print()

        while True:
            try:
                choice = Prompt.ask(
                    f"[bold cyan]Selecione o módulo[/bold cyan] [dim](0=todos, V=voltar, 1-{len(mod_keys)})[/dim]",
                    default="1"
                ).strip().lower()

                if choice == "v":
                    return "__back__", {}
                idx = int(choice)
                if idx == 0:
                    console.print(f"\n[green]✓[/green] Todos os módulos de [bold]{system['name']}[/bold]\n")
                    return "__all__", {}
                if 1 <= idx <= len(mod_keys):
                    k = mod_keys[idx - 1]
                    m = system["modules"][k]
                    console.print(f"\n[green]✓[/green] [bold]{m['name']}[/bold] — {system['name']}\n")
                    return k, m
                console.print(f"[red]Opção inválida.[/red]")
            except (ValueError, EOFError):
                console.print("[red]Opção inválida.[/red]")
            except KeyboardInterrupt:
                console.print("\n[dim]Interrompido.[/dim]"); sys.exit(0)
    else:
        print(f"\n  Sistema: {system['name']}")
        print("┌──────────────────────────────────────────┐")
        print("│   Selecione o módulo                      │")
        print("├──────────────────────────────────────────┤")
        for i, (k, m) in enumerate(system["modules"].items(), 1):
            print(f"│  {i}. {k.upper():<12}  {m['portal_url']:<26} │")
        print("│  0.  Todos os módulos                     │")
        print("│  V.  Voltar                               │")
        print("└──────────────────────────────────────────┘")
        while True:
            try:
                choice = input(f"\nOpção [0-{len(mod_keys)}/V]: ").strip().lower()
                if choice == "v": return "__back__", {}
                idx = int(choice)
                if idx == 0: return "__all__", {}
                if 1 <= idx <= len(mod_keys):
                    k = mod_keys[idx - 1]
                    return k, system["modules"][k]
            except (ValueError, EOFError): pass
            except KeyboardInterrupt: sys.exit(0)
            print("Opção inválida.")


def select_environment(args) -> tuple[str, dict]:
    """
    Menu em dois passos: Sistema → Módulo.
    Suporta CLI direto: args.env = "hml" ou "hml-netwin" ou "hml netwin"
    """
    # ── CLI direto ───────────────────────────────────────────────
    if args.env:
        key = args.env.lower().strip()

        # Formato "hml-netwin" ou "hml netwin" (módulo especificado)
        for sep in ["-", " "]:
            if sep in key:
                parts    = key.split(sep, 1)
                sys_key  = parts[0]
                mod_key  = parts[1]
                if sys_key in SYSTEMS and mod_key in SYSTEMS[sys_key]["modules"]:
                    env_key = f"{sys_key}-{mod_key}"
                    return env_key, ENVIRONMENTS[env_key]

        # Formato "hml" (só sistema → usa primeiro módulo)
        if key in SYSTEMS:
            first_mod = next(iter(SYSTEMS[key]["modules"]))
            env_key   = f"{key}-{first_mod}"
            return env_key, ENVIRONMENTS[env_key]

        # Formato legado "hml-netwin" direto no ENVIRONMENTS
        if key in ENVIRONMENTS:
            return key, ENVIRONMENTS[key]

        available = list(SYSTEMS.keys()) + list(ENVIRONMENTS.keys())
        if RICH:
            console.print(f"[red]❌ '{key}' não encontrado.[/red]")
            console.print(f"   Disponíveis: [cyan]{', '.join(available)}[/cyan]")
        else:
            print(f"❌ '{key}' não encontrado. Disponíveis: {', '.join(available)}")
        sys.exit(1)

    # ── Menu interativo ──────────────────────────────────────────
    _show_banner()

    while True:
        sys_key, system = _pick_system()
        mod_key, module = _pick_module(sys_key, system)

        if mod_key == "__back__":
            continue  # volta para seleção de sistema

        if mod_key == "__all__":
            # Retorna o primeiro módulo mas sinaliza para rodar todos
            first_mod = next(iter(system["modules"]))
            args.__dict__["_run_all_modules"] = True
            args.__dict__["_system_key"]      = sys_key
            env_key = f"{sys_key}-{first_mod}"
            return env_key, ENVIRONMENTS[env_key]

        env_key = f"{sys_key}-{mod_key}"
        return env_key, ENVIRONMENTS[env_key]


# ══════════════════════════════════════════════════════════════════
# UTILITÁRIOS
# ══════════════════════════════════════════════════════════════════

def sanitize(text: str) -> str:
    text = re.sub(r'[\\/:*?"<>|]', "_", text)
    text = re.sub(r'\s+', "_", text.strip())
    return text[:80] or "pagina"


def should_skip(label: str, url: str, portal_url: str) -> bool:
    if url.rstrip("/") == portal_url.rstrip("/"): return True
    if any(s.lower() in label.lower() for s in SKIP_LABELS): return True
    if any(s.lower() in url.lower() for s in SKIP_URLS): return True
    return False


# Textos que indicam carregamento em andamento
LOADING_TEXTS = [
    "A carregar página",
    "A carregar pagina",
    "Carregando o conteúdo",
    "Carregando conteúdo",
    "Carregando...",
    "Carregando",
    "Aguarde, por favor",
    "Por favor aguarde",
    "Loading",
]

def is_page_loading(page: Page) -> str | None:
    """
    Verifica se a página ainda está carregando.
    Retorna o texto de loading encontrado ou None se estiver pronta.
    """
    for text in LOADING_TEXTS:
        try:
            el = page.query_selector(f"text={text}")
            if el and el.is_visible():
                return text
        except Exception:
            continue
    return None


def wait_for_page_ready(page: Page, label: str = "", extra_on_loading: int = 3000):
    """
    Aguarda a página estar pronta de forma inteligente:
    - Espera todos os textos de loading sumirem (até 45s)
    - Se spinner ainda visível após espera → aguarda mais extra_on_loading ms
    - Aplica wait extra configurado por página (EXTRA_WAIT)
    """
    # Aguarda qualquer texto de loading sumir
    waited_for_spinner = False
    for text in LOADING_TEXTS:
        try:
            el = page.query_selector(f"text={text}")
            if el and el.is_visible():
                page.wait_for_selector(f"text={text}", state="hidden", timeout=45_000)
                page.wait_for_timeout(300)
                waited_for_spinner = True
                break
        except Exception:
            continue

    page.wait_for_timeout(300 if waited_for_spinner else 500)

    # Wait extra para páginas configuradas
    extra = next((ms for key, ms in EXTRA_WAIT.items() if key.lower() in label.lower()), 0)
    if extra:
        print_info(f"+{extra//1000}s extra para '{label}'...")
        page.wait_for_timeout(extra)


def debug_shot(page: Page, nome: str, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        page.screenshot(path=str(output_dir / f"debug_{nome}.png"), full_page=True)
    except Exception:
        pass


def _analyze_image(filepath: Path) -> tuple[bool, str]:
    """
    Analisa o screenshot via Pillow para detectar páginas não carregadas.
    Retorna (ok, motivo).

    Técnicas usadas:
    - Uniformidade de cor: página branca/cinza sólida = não carregou
    - Variância de pixel: imagem com pouca variação = provavelmente vazia
    - Detecção de cor dominante: se >90% da imagem for de uma única cor = suspeito
    - Detecção de spinner circular: analisa região central buscando padrão radial
    """
    try:
        from PIL import Image as _Img, ImageStat
        import statistics

        if not filepath.exists() or filepath.stat().st_size < 5_000:
            return False, "Arquivo muito pequeno ou inexistente"

        img = _Img.open(filepath).convert("RGB")
        w, h = img.size

        # ── A. Variância geral da imagem ────────────────────────
        # Página com pouca variação = branca, cinza ou de cor sólida
        stat = ImageStat.Stat(img)
        # stddev de cada canal R, G, B
        stddev_avg = sum(stat.stddev) / 3
        if stddev_avg < 3:  # só marca se for quase completamente uniforme
            return False, f"Imagem sem variacao (stddev={stddev_avg:.1f}) — pagina branca/solida"

        # ── B. Cor dominante na região central ──────────────────
        # Recorta 50% central e verifica se é quase uniforme
        cx1, cy1 = w // 4, h // 4
        cx2, cy2 = 3 * w // 4, 3 * h // 4
        center   = img.crop((cx1, cy1, cx2, cy2))
        c_stat   = ImageStat.Stat(center)
        c_std    = sum(c_stat.stddev) / 3
        if c_std < 6:
            return False, f"Centro da imagem uniforme (stddev={c_std:.1f}) — conteudo nao carregou"

        # ── C. Proporção de pixels brancos/cinzas ───────────────
        # Amostra uma grade de pixels e conta quantos são quase brancos
        sample_step = max(1, w // 40)
        total = white = 0
        for px in range(0, w, sample_step):
            for py in range(0, h, sample_step):
                r, g, b = img.getpixel((px, py))
                total += 1
                # pixel quase branco: todos canais > 240
                if r > 240 and g > 240 and b > 240:
                    white += 1
        white_pct = (white / total * 100) if total > 0 else 0
        if white_pct > 97:  # só marca se for quase 100% branca
            return False, f"Imagem {white_pct:.0f}% branca — pagina nao renderizou"

        # Detecção de spinner visual removida — causa falsos positivos
        # em páginas com layout de painel lateral (centro naturalmente uniforme)

        return True, "ok"

    except ImportError:
        return True, "ok (Pillow nao disponivel)"
    except Exception as e:
        log.debug(f"Analise de imagem falhou: {e}")
        return True, "ok (analise ignorada)"


def validate_screenshot(page: Page, filepath: Path) -> tuple[bool, str]:
    """
    Validação completa em duas camadas:
    1. DOM/Browser — spinner, aria-busy, conteúdo, URL
    2. Imagem      — análise visual via Pillow (variância, cor dominante, spinner)
    """
    # ── CAMADA 1: Validação via DOM ──────────────────────────────

    # 1. URL suspeita (redirecionou para login/erro)
    current_url = page.url.lower()
    for indicator in ERROR_INDICATORS:
        if indicator in current_url:
            return False, f"URL suspeita: {page.url}"

    # 2. Título com erro
    try:
        title = page.title().lower()
        for indicator in ["error", "404", "403", "acesso negado", "not found"]:
            if indicator in title:
                return False, f"Titulo suspeito: {page.title()}"
    except Exception:
        pass

    # 3. Spinner visível por texto
    try:
        loading_texts = [
            "text=A carregar página",
            "text=A carregar pagina",
            "text=Carregando o conteúdo",
            "text=Carregando",
            "text=Loading",
            "text=Por favor aguarde",
        ]
        for sel in loading_texts:
            try:
                el = page.query_selector(sel)
                if el and el.is_visible():
                    return False, f"Spinner visivel: '{sel}'"
            except Exception:
                continue
    except Exception:
        pass

    # 4. Spinner visível por classe (via JS puro)
    try:
        # Classes de layout que contêm "loading" no nome mas NÃO são spinners
        FALSE_POSITIVE_CLASSES = [
            "loading-block",    # bloco de layout fixo do portal
            "loading-bar",      # barra decorativa
            "loading-container",
        ]

        spinner_found = page.evaluate("""() => {
            // Só busca elementos pequenos (spinners são tipicamente < 200x200px)
            // e que não sejam elementos de layout estrutural
            const candidates = document.querySelectorAll(
                '.spinner, .loader, [class*="spinner"], [class*="loader"]'
            );
            for (const el of candidates) {
                const s   = window.getComputedStyle(el);
                const rect = el.getBoundingClientRect();
                if (s.display !== 'none' && s.visibility !== 'hidden'
                        && s.opacity !== '0' && el.offsetParent !== null
                        && rect.width < 300 && rect.height < 300) {
                    return el.className || el.tagName;
                }
            }
            return null;
        }""")
        if spinner_found:
            # Ignora classes conhecidas como falso positivo
            is_fp = any(fp in str(spinner_found) for fp in FALSE_POSITIVE_CLASSES)
            if not is_fp:
                return False, f"Spinner visivel: '{spinner_found}'"
    except Exception:
        pass

    # 5. aria-busy ativo
    try:
        busy = page.evaluate("""() => document.querySelectorAll('[aria-busy="true"]').length""")
        if busy > 0:
            return False, f"{busy} elemento(s) aria-busy=true"
    except Exception:
        pass

    # 6. Conteúdo mínimo no body
    try:
        body_len = page.evaluate(
            "() => document.body ? document.body.innerText.trim().length : 0"
        )
        if body_len < 30:
            return False, f"Conteudo insuficiente ({body_len} chars)"
    except Exception:
        pass

    # ── CAMADA 2: Validação visual via Pillow ────────────────────
    # Só aplica análise de imagem se o arquivo for muito pequeno
    # (evita falsos positivos em páginas com layout lateral ou centro vazio)
    if filepath.exists() and filepath.stat().st_size < 15_000:
        img_ok, img_motivo = _analyze_image(filepath)
        if not img_ok:
            return False, f"Imagem: {img_motivo}"

    return True, "ok"


def capture_with_retry(page: Page, url: str, filepath: Path, label: str, retries: int) -> tuple[bool, str]:
    """
    Navega, espera carregamento e tira screenshot com retry automático.
    Retorna (sucesso, motivo_erro).
    """
    last_error = ""
    for attempt in range(1 + retries):
        try:
            if attempt > 0:
                print_warn(f"Retry {attempt}/{retries} para '{label}'...")
                page.wait_for_timeout(1000 * attempt)  # backoff: 1s, 2s, 3s...

            page.goto(url, wait_until=WAIT_UNTIL, timeout=TIMEOUT)
            wait_for_page_ready(page, label)

            # ── Verifica loading ANTES de tirar o screenshot ────────
            # Se ainda há texto de carregamento → aguarda mais antes de capturar
            loading_check_rounds = 3
            for _ in range(loading_check_rounds):
                still_loading = is_page_loading(page)
                if not still_loading:
                    break
                extra_wait = 5_000 if attempt == 0 else 8_000
                print_warn(f"Pagina '{label}' ainda carregando ('{still_loading}') — aguardando +{extra_wait//1000}s...")
                log.warning(f"Loading detectado antes do screenshot [{label}]: '{still_loading}' — +{extra_wait}ms")
                page.wait_for_timeout(extra_wait)
                # Tenta esperar o elemento sumir
                try:
                    page.wait_for_selector(f"text={still_loading}", state="hidden", timeout=15_000)
                    page.wait_for_timeout(500)
                except Exception:
                    pass

            # Screenshot
            page.screenshot(path=str(filepath), full_page=True, animations="disabled")

            # ── Validação pós-screenshot ────────────────────────────
            ok, motivo = validate_screenshot(page, filepath)
            if not ok:
                log.warning(f"Validacao [{label}] tentativa {attempt+1}: {motivo}")
                if attempt < retries:
                    extra_retry = 5_000 + (attempt * 3_000)  # 5s, 8s, 11s...
                    print_warn(f"Pagina incompleta '{label}' — aguardando +{extra_retry//1000}s e retentando... ({motivo})")
                    # Se redirecionou para login, navega de volta ao portal antes de retentar
                    if "idp/login" in page.url.lower():
                        try:
                            # Tenta navegar direto para a URL — se sessão ainda válida funciona
                            page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT)
                        except Exception:
                            pass
                    else:
                        page.wait_for_timeout(extra_retry)
                    last_error = motivo
                    continue
                else:
                    log.error(f"Validacao falhou apos {1+retries} tentativas [{label}]: {motivo}")
                    return True, f"NOK: {motivo}"

            return True, "ok"

        except Exception as e:
            last_error = str(e)
            log.error(f"Tentativa {attempt+1}/{1+retries} falhou para '{label}': {e}")
            try:
                partial_path = filepath.parent / f"PARCIAL_{filepath.name}"
                page.screenshot(path=str(partial_path), full_page=True)
                log.info(f"Screenshot parcial: {partial_path.name}")
            except Exception:
                pass

    return False, last_error


# ══════════════════════════════════════════════════════════════════
# CAPTURA PARALELA (multi-thread)
# ══════════════════════════════════════════════════════════════════

def calc_threads(n_pages: int) -> int:
    """
    Calcula número de threads baseado no total de páginas.
      < 10 páginas → 1 thread
      10–19        → 2 threads
      20–29        → 2 threads  (evita sobrecarga em portais lentos)
      >= 30        → 3 threads
    Limita a 3 para não sobrecarregar o portal.
    """
    if n_pages < 10:
        return 1
    elif n_pages < 30:
        return 2
    else:
        return 3


def _worker_capture(worker_id: int, items: list, output_dir: Path,
                    env: dict, session_file: Path, retries: int,
                    results_list: list, lock: threading.Lock,
                    http_errors_map: dict) -> None:
    """
    Worker que roda em thread separada:
    - abre browser próprio com sessão compartilhada
    - captura cada item da sua fatia
    - adiciona resultados na lista compartilhada (com lock)
    """
    from playwright.sync_api import sync_playwright

    try:
        session_data = json.loads(session_file.read_text()) if session_file.exists() else None
    except Exception:
        session_data = None

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--ignore-certificate-errors",
                  "--disable-web-security"]
        )
        ctx_args = dict(
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True,
        )
        if session_data:
            ctx_args["storage_state"] = session_data

        ctx  = browser.new_context(**ctx_args)
        page = ctx.new_page()

        # listener de erros HTTP
        local_http_errors: dict = {}

        def _on_resp(response):
            if response.status >= 400:
                label_key = getattr(_on_resp, "_current_label", "?")
                local_http_errors.setdefault(label_key, []).append(
                    f"HTTP {response.status}: {response.url[:80]}"
                )
        page.on("response", _on_resp)

        for item in items:
            label    = item["label"]
            url      = item["url"]
            idx      = item["_idx"]
            filename = f"{idx:02d}_{sanitize(label)}.png"
            filepath = output_dir / filename
            _on_resp._current_label = label

            t0 = time.time()
            log.info(f"[worker-{worker_id}] [{idx}] {label} → {url}")

            ok, msg = capture_with_retry(page, url, filepath, label, retries)
            elapsed_p = time.time() - t0

            if ok:
                add_timestamp_watermark(filepath, label)
                http_err  = local_http_errors.get(label, [])
                extra_msg = (" | " + "; ".join(http_err[:2])) if http_err else ""
                status    = "aviso" if (msg.startswith("AVISO") or http_err) else "ok"
                final_msg = (msg if msg.startswith("AVISO") else "") + extra_msg
                result = {"label": label, "file": str(filepath),
                          "status": status, "time": f"{elapsed_p:.1f}s",
                          "msg": final_msg.strip(" |").strip(), "_idx": idx}
                log.info(f"[worker-{worker_id}] ✓ {filename} ({elapsed_p:.1f}s)")
            else:
                result = {"label": label, "file": str(filepath),
                          "status": "erro", "time": f"{elapsed_p:.1f}s",
                          "msg": msg, "_idx": idx}
                log.error(f"[worker-{worker_id}] ✗ {label}: {msg}")

            with lock:
                results_list.append(result)
                # merge erros HTTP
                for k, v in local_http_errors.items():
                    http_errors_map.setdefault(k, []).extend(v)

        page.close()
        ctx.close()
        browser.close()


def parallel_capture(to_capture: list, output_dir: Path, env: dict,
                     session_file: Path, retries: int,
                     http_errors_map: dict) -> list:
    """
    Divide to_capture em chunks e roda N threads em paralelo.
    Cada thread tem sua própria barra de progresso Rich.
    Retorna lista de resultados ordenada por índice original.
    """
    n         = len(to_capture)
    n_threads = calc_threads(n)

    # Injeta índice global em cada item
    for i, item in enumerate(to_capture, 1):
        item["_idx"] = i

    if n_threads == 1:
        return []   # sinaliza para usar o loop sequencial

    # Divide em chunks balanceados (round-robin para distribuição uniforme)
    chunks = [[] for _ in range(n_threads)]
    for i, item in enumerate(to_capture):
        chunks[i % n_threads].append(item)

    if RICH:
        console.print(
            f"\n[bold cyan]⚡ Multi-thread:[/bold cyan] "
            f"[white]{n} páginas → {n_threads} threads "
            f"(~{n//n_threads} páginas cada)[/white]\n"
        )
    else:
        print(f"\n⚡ Multi-thread: {n} páginas → {n_threads} threads (~{n//n_threads} cada)")

    log.info(f"Multi-thread: {n} páginas / {n_threads} threads")

    results_list: list = []
    lock               = threading.Lock()

    if RICH:
        # ── Barras de progresso por thread ───────────────────────
        THREAD_COLORS = ["cyan", "magenta", "yellow", "green"]

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold]{task.description}[/bold]"),
            BarColumn(bar_width=28),
            TaskProgressColumn(),
            TextColumn("[dim]{task.fields[label]}[/dim]"),
            console=console,
            transient=False,
        ) as progress:

            # Cria uma task por thread
            tasks = {}
            for wid, chunk in enumerate(chunks, 1):
                if not chunk:
                    continue
                color = THREAD_COLORS[(wid - 1) % len(THREAD_COLORS)]
                tasks[wid] = progress.add_task(
                    f"[{color}]Thread {wid}[/{color}]",
                    total=len(chunk),
                    label="iniciando..."
                )

            def _worker_with_progress(worker_id, chunk):
                """Worker que atualiza a task Rich de sua thread."""
                task_id = tasks[worker_id]
                from playwright.sync_api import sync_playwright

                try:
                    sd = json.loads(session_file.read_text()) if session_file.exists() else None
                except Exception:
                    sd = None

                with sync_playwright() as p:
                    br  = _launch_optimized_browser(p)
                    ctx = _new_optimized_context(br, sd)
                    page = ctx.new_page()

                    local_http: dict = {}
                    def _on_resp(r):
                        if r.status >= 400:
                            lbl = getattr(_on_resp, "_lbl", "?")
                            local_http.setdefault(lbl, []).append(
                                f"HTTP {r.status}: {r.url[:80]}")
                    page.on("response", _on_resp)

                    for item in chunk:
                        label    = item["label"]
                        url      = item["url"]
                        idx      = item["_idx"]
                        filename = f"{idx:02d}_{sanitize(label)}.png"
                        filepath = output_dir / filename
                        _on_resp._lbl = label

                        progress.update(task_id, label=label[:30])
                        t0 = time.time()
                        log.info(f"[T{worker_id}] [{idx}] {label} → {url}")

                        # Verifica se sessão expirou antes de capturar
                        if "idp/login" in page.url.lower():
                            log.warning(f"[T{worker_id}] Sessão expirada — tentando reconectar...")
                            try:
                                page.goto(env["portal_url"], wait_until="domcontentloaded", timeout=30_000)
                            except Exception:
                                pass

                        ok, msg = capture_with_retry(page, url, filepath, label, retries)
                        elapsed_p = time.time() - t0

                        if ok:
                            add_timestamp_watermark(filepath, label)
                            http_err  = local_http.get(label, [])
                            extra_msg = (" | " + "; ".join(http_err[:2])) if http_err else ""
                            status    = "nok" if msg.startswith("NOK") else ("aviso" if (msg.startswith("AVISO") or http_err) else "ok")
                            final_msg = (msg if msg.startswith("AVISO") else "") + extra_msg
                            result    = {"label": label, "file": str(filepath),
                                         "status": status, "time": f"{elapsed_p:.1f}s",
                                         "msg": final_msg.strip(" |").strip(), "_idx": idx}
                            log.info(f"[T{worker_id}] ✓ {filename} ({elapsed_p:.1f}s)")
                        else:
                            result = {"label": label, "file": str(filepath),
                                      "status": "erro", "time": f"{elapsed_p:.1f}s",
                                      "msg": msg, "_idx": idx}
                            log.error(f"[T{worker_id}] ✗ {label}: {msg}")

                        with lock:
                            results_list.append(result)
                            for k, v in local_http.items():
                                http_errors_map.setdefault(k, []).extend(v)

                        progress.advance(task_id)

                    page.close(); ctx.close(); br.close()

            # Dispara threads
            threads = []
            for wid, chunk in enumerate(chunks, 1):
                if not chunk:
                    continue
                t = threading.Thread(target=_worker_with_progress,
                                     args=(wid, chunk), daemon=True,
                                     name=f"nossis-worker-{wid}")
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

    else:
        # ── Fallback sem Rich — progresso simples no terminal ─────
        def _worker_simple(worker_id, chunk):
            from playwright.sync_api import sync_playwright
            try:
                sd = json.loads(session_file.read_text()) if session_file.exists() else None
            except Exception:
                sd = None

            with sync_playwright() as p:
                br  = _launch_optimized_browser(p)
                ctx = _new_optimized_context(br, sd)
                page = ctx.new_page()

                for item in chunk:
                    label    = item["label"]
                    idx      = item["_idx"]
                    filename = f"{idx:02d}_{sanitize(label)}.png"
                    filepath = output_dir / filename
                    t0 = time.time()
                    # Verifica se sessão expirou (redirecionou para IAM login)
                    if "idp/login" in page.url.lower():
                        log.warning(f"[T{worker_id}] Sessão expirada durante captura — tentando reconectar...")
                        try:
                            page.goto(env["portal_url"], wait_until="domcontentloaded", timeout=30_000)
                            if "idp/login" in page.url.lower():
                                log.error(f"[T{worker_id}] Sessão inválida — não foi possível reconectar")
                        except Exception:
                            pass

                    ok, msg = capture_with_retry(page, url, filepath, label, retries)
                    elapsed_p = time.time() - t0
                    status = "ok" if ok else "erro"
                    icon   = "✓" if ok else "✗"
                    with lock:
                        results_list.append({"label": label, "file": str(filepath),
                                              "status": status, "time": f"{elapsed_p:.1f}s",
                                              "msg": msg, "_idx": idx})
                        print(f"  [T{worker_id}] {icon} {label:<30} {elapsed_p:.1f}s")

                page.close(); ctx.close(); br.close()

        threads = []
        for wid, chunk in enumerate(chunks, 1):
            if not chunk:
                continue
            t = threading.Thread(target=_worker_simple, args=(wid, chunk),
                                 daemon=True, name=f"nossis-worker-{wid}")
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    # Ordena pelo índice original
    results_list.sort(key=lambda r: r["_idx"])
    return results_list


# ══════════════════════════════════════════════════════════════════
# COMPARAÇÃO DE SCREENSHOTS
# ══════════════════════════════════════════════════════════════════

def compare_screenshots(dir1: str, dir2: str):
    """Compara screenshots entre duas pastas e gera relatório HTML de diferenças."""
    p1, p2 = Path(dir1), Path(dir2)

    if not p1.exists() or not p2.exists():
        print_err(f"Pastas não encontradas: {dir1}, {dir2}")
        sys.exit(1)

    if not PIL_AVAILABLE:
        print_err("Pillow não instalado. Rode: pip3 install Pillow numpy")
        sys.exit(1)

    if RICH:
        console.print(f"\n[bold cyan]🔍 Comparando screenshots...[/bold cyan]")
        console.print(f"   [dim]Dir 1:[/dim] {p1.resolve()}")
        console.print(f"   [dim]Dir 2:[/dim] {p2.resolve()}\n")
    else:
        print(f"\n🔍 Comparando: {dir1} vs {dir2}")

    files1 = {f.name: f for f in p1.glob("*.png") if not f.name.startswith("debug_")}
    files2 = {f.name: f for f in p2.glob("*.png") if not f.name.startswith("debug_")}

    all_files = sorted(set(files1) | set(files2))
    results   = []

    for fname in all_files:
        f1, f2 = files1.get(fname), files2.get(fname)

        if not f1:
            results.append({"file": fname, "status": "novo",    "diff_pct": None, "msg": "Só em DIR2"})
            continue
        if not f2:
            results.append({"file": fname, "status": "removido","diff_pct": None, "msg": "Só em DIR1"})
            continue

        # Compara pixels
        try:
            img1 = Image.open(f1).convert("RGB")
            img2 = Image.open(f2).convert("RGB")

            if img1.size != img2.size:
                img2 = img2.resize(img1.size, Image.LANCZOS)

            arr1  = np.array(img1, dtype=np.int16)
            arr2  = np.array(img2, dtype=np.int16)
            diff  = np.abs(arr1 - arr2)
            pct   = float((diff > 10).any(axis=2).mean() * 100)

            if pct < 1:
                status = "igual"
            elif pct < 10:
                status = "pequena"
            else:
                status = "grande"

            results.append({"file": fname, "status": status, "diff_pct": pct,
                             "f1": str(f1.resolve()), "f2": str(f2.resolve())})
        except Exception as e:
            results.append({"file": fname, "status": "erro", "diff_pct": None, "msg": str(e)})

    # Gera relatório HTML
    out_dir  = Path("comparacoes")
    out_dir.mkdir(exist_ok=True)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_html = out_dir / f"comparacao_{ts}.html"

    _generate_compare_html(out_html, dir1, dir2, results)

    # Exibe resumo
    igual    = sum(1 for r in results if r["status"] == "igual")
    pequena  = sum(1 for r in results if r["status"] == "pequena")
    grande   = sum(1 for r in results if r["status"] == "grande")
    novo     = sum(1 for r in results if r["status"] == "novo")
    removido = sum(1 for r in results if r["status"] == "removido")

    if RICH:
        table = Table(box=box.ROUNDED, border_style="cyan", show_header=True,
                      header_style="bold cyan", padding=(0, 2))
        table.add_column("Arquivo",   width=35)
        table.add_column("Status",    width=12, justify="center")
        table.add_column("Diferença", width=12, justify="right")

        for r in results:
            status = r["status"]
            color  = {"igual": "dim", "pequena": "yellow", "grande": "red",
                      "novo": "green", "removido": "red", "erro": "red"}.get(status, "white")
            diff   = f"{r['diff_pct']:.1f}%" if r.get("diff_pct") is not None else r.get("msg", "—")
            table.add_row(f"[{color}]{r['file']}[/{color}]",
                          f"[{color}]{status}[/{color}]",
                          f"[{color}]{diff}[/{color}]")
        console.print(table)

        summary = (
            f"[dim]Iguais  :[/dim] {igual}    "
            f"[yellow]Pequenas:[/yellow] {pequena}    "
            f"[red]Grandes :[/red] {grande}    "
            f"[green]Novos   :[/green] {novo}    "
            f"[red]Removidos:[/red] {removido}\n"
            f"[bold cyan]Relatório:[/bold cyan] {out_html.resolve()}"
        )
        console.print(Panel(summary, border_style="cyan", padding=(0, 2)))
    else:
        for r in results:
            diff = f"{r['diff_pct']:.1f}%" if r.get("diff_pct") is not None else ""
            print(f"  {r['status']:>10}  {r['file']}  {diff}")
        print(f"\nRelatório: {out_html.resolve()}")


def _generate_compare_html(out_html: Path, dir1: str, dir2: str, results: list):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    rows = ""
    for r in results:
        status = r["status"]
        color  = {"igual": "#4caf50", "pequena": "#ff9800", "grande": "#f44336",
                  "novo": "#2196f3", "removido": "#9e9e9e", "erro": "#f44336"}.get(status, "#fff")
        diff   = f"{r['diff_pct']:.1f}%" if r.get("diff_pct") is not None else r.get("msg", "—")
        img1   = f'<img src="{r.get("f1","")}" style="max-width:100%;border-radius:4px">' if r.get("f1") else "<em>—</em>"
        img2   = f'<img src="{r.get("f2","")}" style="max-width:100%;border-radius:4px">' if r.get("f2") else "<em>—</em>"
        rows += f"""
        <tr>
            <td><strong>{r['file']}</strong></td>
            <td><span style="background:{color};padding:3px 10px;border-radius:12px;color:#fff;font-size:12px">{status}</span></td>
            <td style="text-align:right">{diff}</td>
            <td>{img1}</td>
            <td>{img2}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<title>Comparação NOSSIS — {now}</title>
<style>
  body {{ font-family: monospace; background:#1a1a2e; color:#e0e0e0; margin:0; padding:20px }}
  h1   {{ color:#00b5cc; border-bottom:1px solid #333; padding-bottom:10px }}
  .meta{{ color:#888; font-size:13px; margin-bottom:20px }}
  table{{ width:100%; border-collapse:collapse; font-size:13px }}
  th   {{ background:#0f3460; color:#00b5cc; padding:10px; text-align:left; position:sticky; top:0 }}
  td   {{ padding:8px; border-bottom:1px solid #2a2a4a; vertical-align:top }}
  tr:hover td {{ background:#1e2a4a }}
  img  {{ max-height:200px; object-fit:cover }}
</style>
</head>
<body>
<h1>🔍 Comparação de Screenshots</h1>
<div class="meta">
  Gerado em: {now}<br>
  DIR 1: {dir1}<br>
  DIR 2: {dir2}
</div>
<table>
  <thead><tr><th>Arquivo</th><th>Status</th><th>Diferença</th><th>DIR 1</th><th>DIR 2</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
</body>
</html>"""
    out_html.write_text(html, encoding="utf-8")


# ══════════════════════════════════════════════════════════════════
# RELATÓRIO HTML
# ══════════════════════════════════════════════════════════════════

def generate_report(output_dir: Path, env: dict, version_tag: str,
                    results: list, elapsed: float, log_file: Path):
    """Gera relatorio.html completo (capa + lista + evidências) + PDF."""
    now      = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    now_file = datetime.now().strftime("%Y%m%d_%H%M%S")
    ok    = sum(1 for r in results if r["status"] == "ok")
    warn  = sum(1 for r in results if r["status"] == "aviso")
    err   = sum(1 for r in results if r["status"] == "erro")
    total = ok + warn + err
    ok_pct = int(ok / total * 100) if total else 0

    STATUS_COLOR = {"ok": "#00c896", "aviso": "#ffb300", "erro": "#ff4757", "nok": "#ff4757"}
    STATUS_ICON  = {"ok": "✓", "aviso": "⚠", "erro": "✗", "nok": "✗"}
    STATUS_LABEL = {"ok": "OK", "aviso": "Aviso", "erro": "Erro", "nok": "NOK"}

    # ── helpers ──────────────────────────────────────────────────
    def img_b64(path):
        p = Path(path)
        if p.exists():
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return ""

    # ── Capa ─────────────────────────────────────────────────────
    cover = f"""
<section class="cover">
  <div class="cover-inner">
    <div class="cover-brand">
      <div class="cover-logo-wrap">
        <span class="cover-logo-n">N</span>OSSIS
        <span class="cover-logo-one">ONE</span>
      </div>
      <div class="cover-logo-sub">INVENTORY</div>
    </div>

    <div class="cover-divider"></div>

    <h1 class="cover-title">Relatório de Evidências</h1>
    <p class="cover-subtitle">AutoScreen · v7.1</p>

    <div class="cover-meta-grid">
      <div class="cover-meta-item">
        <span class="cover-meta-label">Ambiente</span>
        <span class="cover-meta-value">{env["name"]}</span>
      </div>
      <div class="cover-meta-item">
        <span class="cover-meta-label">Versão</span>
        <span class="cover-meta-value ver-tag">{version_tag}</span>
      </div>
      <div class="cover-meta-item">
        <span class="cover-meta-label">Gerado em</span>
        <span class="cover-meta-value">{now}</span>
      </div>
      <div class="cover-meta-item">
        <span class="cover-meta-label">Duração</span>
        <span class="cover-meta-value">{elapsed/60:.1f} min ({elapsed:.0f}s)</span>
      </div>
      <div class="cover-meta-item full">
        <span class="cover-meta-label">Pasta</span>
        <span class="cover-meta-value small">{output_dir.resolve()}</span>
      </div>
      <div class="cover-meta-item full">
        <span class="cover-meta-label">Autor</span>
        <span class="cover-meta-value">Diego Santos &nbsp;·&nbsp; diego-f-santos@openlabs.com.br</span>
      </div>
    </div>

    <div class="cover-stats-row">
      <div class="cover-stat ok">
        <div class="cover-stat-n">{ok}</div>
        <div class="cover-stat-l">OK</div>
      </div>
      <div class="cover-stat warn">
        <div class="cover-stat-n">{warn}</div>
        <div class="cover-stat-l">Avisos</div>
      </div>
      <div class="cover-stat err">
        <div class="cover-stat-n">{err}</div>
        <div class="cover-stat-l">Erros</div>
      </div>
      <div class="cover-stat total">
        <div class="cover-stat-n">{total}</div>
        <div class="cover-stat-l">Total</div>
      </div>
    </div>

    <div class="cover-progress-wrap">
      <div class="cover-progress-bar">
        <div class="cover-progress-fill" style="width:{ok_pct}%"></div>
      </div>
      <span class="cover-progress-label">{ok_pct}% de sucesso</span>
    </div>
  </div>
</section>
"""

    # ── Tabela resumo ─────────────────────────────────────────────
    rows = ""
    for i, r in enumerate(results, 1):
        sc    = STATUS_COLOR.get(r["status"], "#888")
        si    = STATUS_ICON.get(r["status"], "?")
        sl    = STATUS_LABEL.get(r["status"], r["status"])
        msg   = f'<div class="row-warn">⚠ {r["msg"]}</div>' if r.get("msg") else ""
        rows += f"""
      <tr class="row-{r['status']}">
        <td class="td-num">{i:02d}</td>
        <td class="td-label"><span class="row-label">{r["label"]}</span>{msg}</td>
        <td class="td-status">
          <span class="status-pill" style="background:{sc}22;color:{sc};border-color:{sc}">
            {si} {sl}
          </span>
        </td>
        <td class="td-time">{r.get("time","—")}</td>
      </tr>"""

    summary = f"""
<section class="page-section">
  <div class="section-header">
    <span class="section-icon">📋</span>
    <span class="section-title">Resumo das Capturas</span>
    <span class="section-count">{total} páginas</span>
  </div>
  <table class="summary-table">
    <thead>
      <tr>
        <th style="width:50px">#</th>
        <th>Página</th>
        <th style="width:110px;text-align:center">Status</th>
        <th style="width:90px;text-align:center">Tempo</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</section>
"""

    # ── Evidências — 2 por página ────────────────────────────────
    def build_ev_card(i, r):
        b64     = img_b64(r.get("file", ""))
        img_src = f"data:image/png;base64,{b64}" if b64 else ""
        sc      = STATUS_COLOR.get(r["status"], "#888")
        si      = STATUS_ICON.get(r["status"], "?")
        sl      = STATUS_LABEL.get(r["status"], r["status"])
        msg_div = f'<div class="ev-warn">⚠ {r["msg"]}</div>' if r.get("msg") else ""
        if img_src:
            img_html = f'<a href="{img_src}" target="_blank"><img src="{img_src}" class="ev-img"></a>'
        else:
            img_html = '<div class="ev-no-img">📷 Sem imagem</div>'
        return f"""<div class="ev-item" id="ev-{i}">
  <div class="ev-header">
    <span class="ev-num">#{i:02d}</span>
    <span class="ev-title">{r["label"]}</span>
    <span class="ev-pill" style="background:{sc}22;color:{sc};border-color:{sc}">{si} {sl}</span>
    <span class="ev-time">⏱ {r.get("time","—")}</span>
    {msg_div}
  </div>
  <div class="ev-img-wrap">{img_html}</div>
</div>"""

    # Agrupa resultados em pares — cada página tem 2 evidências
    pages_html = ""
    pairs = [results[i:i+2] for i in range(0, len(results), 2)]
    page_num = 3  # capa=1, resumo=2, evidências a partir de 3
    for pair in pairs:
        cards_html = ""
        for j, r in enumerate(pair):
            idx = results.index(r) + 1
            cards_html += build_ev_card(idx, r)
        pages_html += f"""
<div class="ev-page" data-page="{page_num}">
  {cards_html}
</div>
"""
        page_num += 1

    evidence = f"""
<section class="page-section">
  <div class="section-header">
    <span class="section-icon">🖼</span>
    <span class="section-title">Evidências</span>
    <span class="section-count">{total} capturas</span>
  </div>
</section>
{pages_html}
"""

    # ── CSS ───────────────────────────────────────────────────────
    css = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    :root {
      --bg:       #0b0b18;
      --bg2:      #11112a;
      --bg3:      #181830;
      --border:   #252545;
      --cyan:     #00c8e0;
      --cyan2:    #00e5ff;
      --text:     #e8e8f0;
      --muted:    #6060a0;
      --ok:       #00c896;
      --warn:     #ffb300;
      --err:      #ff4757;
      --font:     'Inter', sans-serif;
      --mono:     'JetBrains Mono', monospace;
    }

    * { box-sizing:border-box; margin:0; padding:0 }
    body { font-family:var(--font); background:var(--bg); color:var(--text); line-height:1.6 }
    a { color:inherit; text-decoration:none }

    /* ── CAPA ── */
    .cover {
      min-height:100vh;
      background: linear-gradient(160deg, #0b0b18 0%, #090920 40%, #0a1530 100%);
      display:flex; align-items:center; justify-content:center;
      padding:60px 40px; position:relative; overflow:hidden;
    }
    .cover::before {
      content:'';
      position:absolute; inset:0;
      background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(0,200,224,.08) 0%, transparent 70%);
      pointer-events:none;
    }
    .cover-inner {
      max-width:680px; width:100%; text-align:center; position:relative;
    }
    .cover-brand { margin-bottom:32px }
    .cover-logo-wrap {
      font-family:var(--mono); font-size:64px; font-weight:700;
      color:var(--cyan); letter-spacing:-1px; line-height:1;
    }
    .cover-logo-n { color:#fff }
    .cover-logo-one {
      font-size:22px; font-weight:600; color:#fff;
      vertical-align:super; margin-left:6px; opacity:.7;
    }
    .cover-logo-sub {
      font-family:var(--mono); font-size:13px; letter-spacing:6px;
      color:var(--muted); margin-top:4px; text-transform:uppercase;
    }
    .cover-divider {
      width:60px; height:2px;
      background:linear-gradient(90deg, transparent, var(--cyan), transparent);
      margin:24px auto;
    }
    .cover-title {
      font-size:30px; font-weight:700; color:#fff; margin-bottom:6px;
    }
    .cover-subtitle { font-size:14px; color:var(--muted); margin-bottom:36px }

    .cover-meta-grid {
      display:grid; grid-template-columns:1fr 1fr; gap:0;
      background:var(--bg2); border:1px solid var(--border);
      border-radius:12px; overflow:hidden; margin-bottom:28px; text-align:left;
    }
    .cover-meta-item {
      padding:12px 18px; border-bottom:1px solid var(--border);
      display:flex; flex-direction:column; gap:2px;
    }
    .cover-meta-item.full { grid-column:span 2 }
    .cover-meta-label { font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:1px }
    .cover-meta-value { font-size:14px; font-weight:500; color:var(--text) }
    .cover-meta-value.small { font-size:11px; font-family:var(--mono); color:var(--muted) }
    .ver-tag {
      font-family:var(--mono); color:var(--cyan);
      background:rgba(0,200,224,.1); padding:2px 8px; border-radius:4px;
      display:inline-block; font-size:13px;
    }

    .cover-stats-row {
      display:flex; gap:12px; justify-content:center; margin-bottom:20px;
    }
    .cover-stat {
      flex:1; background:var(--bg2); border:1px solid var(--border);
      border-radius:10px; padding:16px 10px; text-align:center;
    }
    .cover-stat-n { font-size:40px; font-weight:800; line-height:1 }
    .cover-stat-l { font-size:12px; color:var(--muted); margin-top:4px }
    .cover-stat.ok   .cover-stat-n { color:var(--ok) }
    .cover-stat.warn .cover-stat-n { color:var(--warn) }
    .cover-stat.err  .cover-stat-n { color:var(--err) }
    .cover-stat.total .cover-stat-n { color:var(--cyan) }

    .cover-progress-wrap { display:flex; align-items:center; gap:12px }
    .cover-progress-bar {
      flex:1; height:6px; background:var(--bg3); border-radius:3px; overflow:hidden;
    }
    .cover-progress-fill {
      height:100%; border-radius:3px;
      background:linear-gradient(90deg, var(--ok), var(--cyan));
      transition:width .5s;
    }
    .cover-progress-label { font-size:12px; color:var(--muted); white-space:nowrap }

    /* ── CONTEÚDO ── */
    .page-section { max-width:1200px; margin:0 auto; padding:48px 36px }

    .section-header {
      display:flex; align-items:center; gap:12px;
      border-bottom:2px solid var(--border); padding-bottom:16px; margin-bottom:24px;
    }
    .section-icon { font-size:20px }
    .section-title { font-size:20px; font-weight:700; color:var(--cyan); flex:1 }
    .section-count {
      font-size:12px; background:var(--bg3); border:1px solid var(--border);
      border-radius:20px; padding:4px 14px; color:var(--muted);
    }

    /* ── TABELA RESUMO ── */
    .summary-table { width:100%; border-collapse:collapse; font-size:14px }
    .summary-table th {
      background:var(--bg3); color:var(--cyan); padding:12px 16px;
      font-weight:600; text-align:left; border-bottom:2px solid var(--border);
      font-size:12px; text-transform:uppercase; letter-spacing:.5px;
    }
    .summary-table td { padding:12px 16px; border-bottom:1px solid var(--border) }
    .summary-table tr:hover td { background:rgba(255,255,255,.02) }
    .td-num { font-family:var(--mono); font-size:12px; color:var(--muted); text-align:center }
    .td-label { font-weight:500 }
    .td-status { text-align:center }
    .td-time { font-family:var(--mono); font-size:12px; color:var(--muted); text-align:center }
    .row-label { display:block }
    .row-warn { font-size:11px; color:var(--warn); margin-top:2px }
    .status-pill {
      display:inline-block; padding:3px 12px; border-radius:20px;
      font-size:11px; font-weight:600; border:1px solid;
    }

    /* ── EVIDÊNCIAS ── */
    .ev-item {
      background:var(--bg2); border:1px solid var(--border);
      border-radius:14px; overflow:hidden; margin-bottom:32px;
      transition:border-color .2s;
    }
    .ev-item:hover { border-color:var(--cyan) }

    .ev-header {
      display:flex; align-items:center; gap:12px; flex-wrap:wrap;
      padding:16px 20px; border-bottom:1px solid var(--border);
      background:var(--bg3);
    }
    .ev-num {
      font-family:var(--mono); font-size:12px; color:var(--muted);
      background:var(--bg); border:1px solid var(--border);
      border-radius:6px; padding:2px 8px;
    }
    .ev-title { font-size:16px; font-weight:700; flex:1; color:#fff }
    .ev-pill {
      display:inline-block; padding:3px 14px; border-radius:20px;
      font-size:12px; font-weight:600; border:1px solid;
    }
    .ev-time { font-family:var(--mono); font-size:12px; color:var(--muted) }
    .ev-warn { font-size:12px; color:var(--warn); width:100%; margin-top:4px }

    .ev-img-wrap { padding:20px; background:var(--bg) }
    .ev-img {
      width:100%; max-height:720px; object-fit:contain; object-position:top;
      border-radius:8px; display:block;
      box-shadow: 0 4px 24px rgba(0,0,0,.5);
      cursor:zoom-in;
    }
    .ev-img:hover { transform:scale(1.005); transition:.2s }
    .ev-no-img {
      height:200px; display:flex; align-items:center; justify-content:center;
      color:var(--muted); font-size:14px; background:var(--bg3); border-radius:8px;
    }

    /* ── PÁGINA DE EVIDÊNCIAS (2 por página) ── */
    .ev-page {
      max-width:1200px; margin:0 auto; padding:24px 36px;
      display:flex; flex-direction:column; gap:24px;
    }

    /* ── PAGE BREAK — apenas no print ── */
    .page-break { display:none }

    /* ── PRINT ── */
    @media print {
      body { background:#fff !important; color:#000 !important }

      .cover {
        background:#fff !important;
        min-height:unset;
        page-break-after: always !important;
        break-after: page !important;
      }
      .cover::before { display:none }
      .cover-logo-wrap { color:#005a6e !important }
      .cover-logo-one  { color:#333 !important }
      .cover-logo-sub  { color:#777 !important }
      .cover-title     { color:#000 !important }
      .cover-subtitle  { color:#555 !important }
      .cover-divider   { background:#005a6e !important }
      .cover-progress-bar { background:#ddd !important }
      .section-title   { color:#005a6e !important }

      .page-section {
        page-break-after: always;
        break-after: page;
      }

      .ev-page {
        page-break-after: always;
        break-after: page;
        padding: 12px 20px;
        gap: 16px;
      }
      .ev-page:last-of-type {
        page-break-after: auto;
        break-after: auto;
      }

      .ev-item {
        break-inside: avoid;
        page-break-inside: avoid;
        border: 1px solid #ccc !important;
        background: #fff !important;
        margin-bottom: 12px;
      }
      .ev-header   { background:#f5f5f5 !important; color:#000 !important; border-color:#ddd !important }
      .ev-title    { color:#000 !important }
      .ev-num      { background:#eee !important; color:#333 !important; border-color:#ccc !important }
      .ev-time     { color:#555 !important }
      .ev-img-wrap { background:#fff !important; padding:8px !important }
      .ev-img      { max-height:460px !important; width:100%; object-fit:contain !important }

      .summary-table th { background:#f0f0f0 !important; color:#005a6e !important }
      .summary-table td { color:#000 !important; border-color:#ddd !important }
      .td-num           { color:#666 !important }
      .td-time          { color:#666 !important }

      .cover-meta-grid   { background:#f9f9f9 !important; border-color:#ddd !important }
      .cover-meta-item   { border-color:#ddd !important }
      .cover-meta-label  { color:#666 !important }
      .cover-meta-value  { color:#000 !important }
      .cover-meta-value.small { color:#555 !important }
      .ver-tag           { background:#e6f7fa !important; color:#005a6e !important }
      .cover-stat        { background:#f5f5f5 !important; border-color:#ddd !important }
      .cover-stat-l      { color:#555 !important }
      .cover-stat.ok   .cover-stat-n { color:#007a5e !important }
      .cover-stat.warn .cover-stat-n { color:#b37a00 !important }
      .cover-stat.err  .cover-stat-n { color:#c0392b !important }
      .cover-stat.total .cover-stat-n { color:#005a6e !important }
      .cover-progress-bar  { background:#e0e0e0 !important }
      .cover-progress-label { color:#555 !important }

      @page {
        size: A4;
        margin: 15mm 12mm 22mm 12mm;
        @bottom-center {
          content: "NOSSIS ONE INVENTORY  ·  Página " counter(page) " de " counter(pages);
          font-size: 9pt; color: #666; font-family: monospace;
        }
      }
    }
    """

    # ── Lightbox JS ──────────────────────────────────────────────
    js = """
    // Numeração de páginas visível no rodapé (para HTML)
    const totalPages = document.querySelectorAll('.page-break').length + 1;
    document.querySelectorAll('.ev-page').forEach(p => {
      const n = p.dataset.page;
      const footer = document.createElement('div');
      footer.style.cssText = 'text-align:center;font-size:11px;color:#6060a0;font-family:monospace;padding:8px 0 4px;border-top:1px solid #252545;margin-top:8px';
      footer.textContent = `NOSSIS ONE INVENTORY  ·  Página ${n}`;
      p.appendChild(footer);
    });

    document.querySelectorAll('.ev-img').forEach(img => {
      img.addEventListener('click', () => {
        const ov = document.createElement('div');
        ov.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,.95);display:flex;align-items:center;justify-content:center;z-index:9999;cursor:zoom-out;padding:24px';
        const i = document.createElement('img');
        i.src = img.src;
        i.style.cssText = 'max-width:95vw;max-height:95vh;border-radius:10px;box-shadow:0 0 80px rgba(0,200,224,.2)';
        ov.appendChild(i);
        ov.addEventListener('click', () => ov.remove());
        document.addEventListener('keydown', e => e.key === 'Escape' && ov.remove(), {once:true});
        document.body.appendChild(ov);
      });
    });
    """

    # ── HTML final ───────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="pt" data-env="{env["name"]}" data-version="{version_tag}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Relatório NOSSIS — {env["name"]} · v{version_tag} · {now}</title>
<style>{css}</style>
</head>
<body>
{cover}
{summary}
{evidence}
<script>{js}</script>
</body>
</html>"""

    report_path = output_dir / f"relatorio_{now_file}.html"
    report_path.write_text(html, encoding="utf-8")
    log.info(f"Relatório HTML: {report_path}")

    # ── PDF via Pillow (PNG → PDF direto, sem CSS print, sem Playwright) ──
    pdf_path = None
    try:
        from PIL import Image as PILImage, ImageDraw, ImageFont
        import textwrap

        pdf_out  = output_dir / f"relatorio_{now_file}.pdf"

        # ABNT NBR 14724 -- Dimensoes e margens
        # A4: 210 x 297 mm a 150 DPI
        DPI      = 150
        MM       = DPI / 25.4          # pixels por mm
        A4_W     = int(210 * MM)       # ~1240 px
        A4_H     = int(297 * MM)       # ~1753 px

        # Margens ABNT (mm -> px)
        M_TOP    = int(30 * MM)        # superior  : 3 cm
        M_BOT    = int(20 * MM)        # inferior  : 2 cm
        M_LEFT   = int(30 * MM)        # esquerda  : 3 cm
        M_RIGHT  = int(20 * MM)        # direita   : 2 cm

        # Area util de texto
        TEXT_W   = A4_W - M_LEFT - M_RIGHT
        TEXT_H   = A4_H - M_TOP  - M_BOT

        # Tamanhos de fonte ABNT
        # 1pt = 1/72 polegada; @ 150 DPI -> 1pt = 2.08 px
        PT       = DPI / 72.0
        F_BODY   = int(12 * PT)        # 12pt -- corpo do texto
        F_SMALL  = int(10 * PT)        # 10pt -- legendas e rodape
        F_TITLE  = int(14 * PT)        # 14pt -- titulos de secao (negrito)
        F_H1     = int(16 * PT)        # 16pt -- titulos principais

        # Espacamento entrelinhas ABNT: 1,5x a altura da fonte body
        LINE_H   = int(F_BODY * 1.5)

        # Alias de compatibilidade com codigo existente
        MARGIN = M_LEFT

        # Paleta branco (ABNT exige papel branco)
        C_BG   = (255, 255, 255)
        C_BG2  = (245, 247, 250)
        C_CYAN = (0,   90, 110)
        C_TEXT = (30,  30,  50)
        C_MUTE = (120, 120, 150)
        C_LINE = (210, 215, 225)
        C_OK   = (0,  140, 100)
        C_WARN = (180, 110,  0)
        C_ERR  = (200,  40,  50)
        C_WHITE= (255, 255, 255)

        def new_page():
            img = PILImage.new("RGB", (A4_W, A4_H), C_BG)
            return img, ImageDraw.Draw(img)

        def load_font(size, bold=False):
            # Tenta Liberation Sans (equivalente Arial), depois DejaVu
            suffix = "-Bold" if bold else "-Regular"
            candidates = [
                f"/usr/share/fonts/truetype/liberation/LiberationSans{suffix}.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans{}.ttf".format("-Bold" if bold else ""),
            ]
            for path in candidates:
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue
            return ImageFont.load_default()

        def draw_header(draw, page_num, total):
            # ABNT NBR 14724 sec 5.3: numeracao no canto superior direito,
            # a 2 cm da borda superior, em algarismos arabicos, sem tracejado
            txt = str(page_num)
            f   = load_font(F_SMALL)
            bb  = draw.textbbox((0, 0), txt, font=f)
            x   = A4_W - M_RIGHT - (bb[2] - bb[0])
            y   = int(15 * MM)
            draw.text((x, y), txt, font=f, fill=C_MUTE)

        def draw_footer(draw, page_num, total):
            # Rodape institucional (complemento, nao previsto na ABNT)
            txt = f"NOSSIS ONE INVENTORY  .  Pag. {page_num} de {total}"
            f   = load_font(F_SMALL)
            bb  = draw.textbbox((0, 0), txt, font=f)
            tw  = bb[2] - bb[0]
            x   = M_LEFT + (TEXT_W - tw) // 2
            y   = A4_H - M_BOT + int(4 * MM)
            draw.line([(M_LEFT, y - int(3*MM)), (A4_W - M_RIGHT, y - int(3*MM))],
                      fill=C_LINE, width=1)
            draw.text((x, y), txt, font=f, fill=C_MUTE)

        def draw_page_frame(draw, page_num, total):
            draw_header(draw, page_num, total)
            draw_footer(draw, page_num, total)

        def fit_image(img_path, max_w, max_h):
            """Abre PNG e redimensiona para caber em max_w x max_h mantendo proporção."""
            im = PILImage.open(img_path).convert("RGB")
            iw, ih = im.size
            scale  = min(max_w / iw, max_h / ih, 1.0)
            nw, nh = int(iw * scale), int(ih * scale)
            return im.resize((nw, nh), PILImage.LANCZOS)

        pages_pil = []  # lista de PILImage prontas para salvar

        # ── CAPA ──────────────────────────────────────────────────
        img, draw = new_page()
        usable_h  = A4_H - M_TOP - M_BOT - 40
        logo_h    = 120; divider_h = 28; title_h = 80
        meta_h    = 4 * 64; stats_h = 116; bar_h_blk = 38; gaps = 60
        total_content_h = logo_h + divider_h + title_h + meta_h + stats_h + bar_h_blk + gaps
        cy = M_TOP + max(0, (usable_h - total_content_h) // 2)

        # Logo
        f_logo = load_font(90, bold=True)
        draw.text((A4_W//2, cy+50), "NOSSIS", font=f_logo, fill=C_CYAN, anchor="mm")
        bb_logo = draw.textbbox((0,0), "NOSSIS", font=f_logo)
        logo_right = A4_W//2 + (bb_logo[2]-bb_logo[0])//2 + 10
        draw.text((logo_right, cy+10), "ONE", font=load_font(26, bold=True), fill=C_MUTE)
        cy += 90
        draw.text((A4_W//2, cy+14), "I N V E N T O R Y", font=load_font(16), fill=C_MUTE, anchor="mm")
        cy += 34

        # Divisor
        div_w = 80
        draw.rectangle([A4_W//2-div_w//2, cy, A4_W//2+div_w//2, cy+3], fill=C_CYAN)
        cy += 22

        # Titulo
        draw.text((A4_W//2, cy+22), "Relatorio de Evidencias", font=load_font(36, bold=True), fill=C_TEXT, anchor="mm")
        cy += 44
        draw.text((A4_W//2, cy+10), "AutoScreen . v7.1", font=load_font(17), fill=C_MUTE, anchor="mm")
        cy += 34

        # Metadados
        meta_items = [
            ("AMBIENTE",   env["name"]),
            ("VERSAO",     version_tag),
            ("GERADO EM",  now),
            ("DURACAO",    f"{elapsed/60:.1f} min ({elapsed:.0f}s)"),
            ("PASTA",      str(output_dir.resolve())),
            ("AUTOR",      "Diego Santos . diego-f-santos@openlabs.com.br"),
        ]
        cw2 = (A4_W - 2*MARGIN) // 2
        cell_h = 64
        fl = load_font(12); fv = load_font(16, bold=True)

        for idx, (lbl, val) in enumerate(meta_items):
            if idx < 4:
                col = idx % 2; row = idx // 2; cw = cw2
            else:
                col = 0; row = 2 + (idx-4); cw = A4_W - 2*MARGIN
            x0 = MARGIN + col*cw2
            y0 = cy + row*cell_h
            bg = C_BG2 if idx % 2 == 0 else (250, 252, 255)
            draw.rectangle([x0+1, y0+1, x0+cw-3, y0+cell_h-3], fill=bg, outline=C_LINE)
            draw.rectangle([x0+1, y0+1, x0+5, y0+cell_h-3], fill=C_CYAN)
            draw.text((x0+14, y0+10), lbl, font=fl, fill=C_MUTE)
            val_str = val if len(val) < 60 else val[:57]+"..."
            draw.text((x0+14, y0+28), val_str, font=fv, fill=C_TEXT)
        cy += 4*cell_h + 16

        # Stats
        stat_items = [(str(ok),"OK",C_OK),(str(warn),"Avisos",C_WARN),(str(err),"Erros",C_ERR),(str(total),"Total",C_CYAN)]
        sw = (A4_W - 2*MARGIN) // 4; sh = 100
        fn = load_font(52, bold=True); fsl = load_font(15)
        for idx, (n, lbl, col) in enumerate(stat_items):
            x0 = MARGIN + idx*sw
            draw.rectangle([x0+2, cy, x0+sw-4, cy+sh], fill=C_BG2, outline=C_LINE)
            draw.rectangle([x0+2, cy, x0+sw-4, cy+5], fill=col)
            bb = draw.textbbox((0,0), n, font=fn)
            nx = x0 + (sw-(bb[2]-bb[0]))//2
            draw.text((nx, cy+12), n, font=fn, fill=col)
            draw.text((x0+sw//2, cy+sh-18), lbl, font=fsl, fill=C_MUTE, anchor="mm")
        cy += sh + 14

        # Barra de progresso
        bar_w = A4_W - 2*MARGIN; bar_h = 12
        draw.rounded_rectangle([MARGIN, cy, MARGIN+bar_w, cy+bar_h], radius=6, fill=C_BG2, outline=C_LINE)
        fill_w = max(int(bar_w * ok_pct / 100), 12)
        draw.rounded_rectangle([MARGIN, cy, MARGIN+fill_w, cy+bar_h], radius=6, fill=C_OK)
        pct_txt = f"{ok_pct}% de sucesso"
        bb = draw.textbbox((0,0), pct_txt, font=load_font(14))
        draw.text((A4_W//2-(bb[2]-bb[0])//2, cy+bar_h+10), pct_txt, font=load_font(14), fill=C_MUTE)

        draw_footer(draw, 1, "?")
        pages_pil.append(img)

        # ── RESUMO ────────────────────────────────────────────────
        img, draw = new_page()
        fy = M_TOP

        # Header da secao
        hdr_h = 52
        draw.rectangle([MARGIN, fy, A4_W-MARGIN, fy+hdr_h], fill=C_CYAN)
        draw.text((MARGIN+16, fy+15), "Resumo das Capturas", font=load_font(22, bold=True), fill=(255,255,255))
        count_txt = f"{total} paginas"
        bb = draw.textbbox((0,0), count_txt, font=load_font(15))
        draw.text((A4_W-MARGIN-16-(bb[2]-bb[0]), fy+18), count_txt, font=load_font(15), fill=(200,240,245))
        fy += hdr_h + 6

        # Cabecalho da tabela
        col_widths = [52, 460, 140, 100]
        headers    = ["#", "PAGINA", "STATUS", "TEMPO"]
        fth = load_font(13, bold=True); ftd = load_font(14)
        row_h = 33

        draw.rectangle([MARGIN, fy, A4_W-MARGIN, fy+row_h], fill=(225, 232, 245))
        x = MARGIN
        for w, h in zip(col_widths, headers):
            draw.text((x+8, fy+10), h, font=fth, fill=C_CYAN)
            x += w
        draw.line([(MARGIN, fy+row_h), (A4_W-MARGIN, fy+row_h)], fill=C_LINE, width=2)
        fy += row_h

        def draw_table_header(draw, fy, col_widths, headers, fth):
            draw.rectangle([MARGIN, fy, A4_W-MARGIN, fy+row_h], fill=(225, 232, 245))
            x = MARGIN
            for w, h in zip(col_widths, headers):
                draw.text((x+8, fy+10), h, font=fth, fill=C_CYAN)
                x += w
            draw.line([(MARGIN, fy+row_h), (A4_W-MARGIN, fy+row_h)], fill=C_LINE, width=2)
            return fy + row_h

        page_count = 2
        for i, r in enumerate(results, 1):
            if fy + row_h > A4_H - MARGIN - 50:
                draw_page_frame(draw, page_count, "?")
                pages_pil.append(img)
                page_count += 1
                img, draw = new_page()
                fy = draw_table_header(draw, MARGIN, col_widths, headers, fth)

            sc  = {"ok": C_OK, "aviso": C_WARN, "erro": C_ERR}.get(r["status"], C_MUTE)
            si  = {"ok": "OK", "aviso": "Aviso", "erro": "Erro", "nok": "NOK"}.get(r["status"], r["status"])
            row_bg = C_BG if i % 2 == 1 else C_BG2
            draw.rectangle([MARGIN, fy, A4_W-MARGIN, fy+row_h], fill=row_bg)
            draw.rectangle([MARGIN, fy, MARGIN+4, fy+row_h], fill=sc)
            x = MARGIN
            vals = [f"{i:02d}", r["label"], si, r.get("time","--")]
            for j, (w, val) in enumerate(zip(col_widths, vals)):
                col_c = sc if j == 2 else C_TEXT
                bold = j == 2
                draw.text((x+8, fy+10), str(val)[:48], font=load_font(14, bold=bold), fill=col_c)
                x += w
            draw.line([(MARGIN, fy+row_h), (A4_W-MARGIN, fy+row_h)], fill=C_LINE, width=1)
            fy += row_h

        draw_page_frame(draw, page_count, "?")
        pages_pil.append(img)
        page_count += 1

        # ── EVIDÊNCIAS — 2 por página ─────────────────────────────
        IMG_MAX_H = int((A4_H - 2*MARGIN - 160) // 2)  # altura máx por imagem
        IMG_MAX_W = A4_W - 2*MARGIN

        for i in range(0, len(results), 2):
            pair = results[i:i+2]
            img, draw = new_page()
            y = M_TOP

            for r in pair:
                sc  = {"ok": C_OK, "aviso": C_WARN, "erro": C_ERR}.get(r["status"], C_MUTE)
                si  = {"ok": "✓ OK", "aviso": "⚠ Aviso", "erro": "✗ Erro"}.get(r["status"], r["status"])
                idx = results.index(r) + 1

                # cabeçalho do card — mesma cor do header do resumo (C_CYAN)
                card_h = 40
                draw.rectangle([M_LEFT, y, A4_W-M_RIGHT, y+card_h], fill=C_CYAN)
                # numero (#01) em branco semi-transparente
                draw.text((M_LEFT+12, y+12), f"#{idx:02d}", font=load_font(14), fill=(180, 220, 230))
                # label em branco
                draw.text((M_LEFT+58, y+12), r["label"], font=load_font(15, bold=True), fill=(255, 255, 255))
                # pill de status
                pill_txt = si
                bb  = draw.textbbox((0,0), pill_txt, font=load_font(12))
                pw  = bb[2]-bb[0]+16
                px  = A4_W - M_RIGHT - pw - 12
                # pill branco com texto colorido — destaque sobre o header ciano
                draw.rectangle([px, y+8, px+pw, y+32], fill=(255,255,255), outline=(255,255,255))
                draw.text((px+8, y+12), pill_txt, font=load_font(12, bold=True), fill=sc)
                # tempo à esquerda do pill
                draw.text((px-75, y+12), r.get("time","—"), font=load_font(12), fill=(180, 220, 230))
                y += card_h + 2

                # imagem
                img_path = Path(r.get("file",""))
                if img_path.exists():
                    try:
                        thumb = fit_image(img_path, IMG_MAX_W, IMG_MAX_H)
                        img.paste(thumb, (M_LEFT, y))
                        y += thumb.size[1] + 12
                    except Exception:
                        draw.rectangle([MARGIN, y, A4_W-MARGIN, y+80], fill=C_BG2, outline=C_LINE)
                        draw.text((A4_W//2, y+30), "Imagem não disponível", font=load_font(14), fill=C_MUTE, anchor="mm")
                        y += 92
                else:
                    draw.rectangle([MARGIN, y, A4_W-MARGIN, y+80], fill=C_BG2, outline=C_LINE)
                    draw.text((A4_W//2, y+30), "Sem imagem", font=load_font(14), fill=C_MUTE, anchor="mm")
                    y += 92

                y += 8  # espaço entre os dois cards

            draw_page_frame(draw, page_count, "?")
            pages_pil.append(img)
            page_count += 1

        # Corrige numeração do total
        total_pages = len(pages_pil)
        # Não é possível reescrever rodapés já desenhados em cada PIL —
        # usamos a contagem correta já no loop acima; vamos regenerar apenas
        # os rodapés com total correto re-desenhando por cima
        # (mais simples: já temos total_pages, basta sobrescrever)
        fp_font = load_font(14)
        for pi, pimg in enumerate(pages_pil):
            pd = ImageDraw.Draw(pimg)
            txt = f"NOSSIS ONE INVENTORY  ·  Página {pi+1} de {total_pages}"
            bb  = pd.textbbox((0,0), txt, font=fp_font)
            tw  = bb[2] - bb[0]
            x   = (A4_W - tw) // 2
            y   = A4_H - MARGIN + 10
            # cobre o rodapé anterior com fundo
            pd.rectangle([0, y-12, A4_W, A4_H], fill=C_BG)
            pd.line([(MARGIN, y-8), (A4_W-MARGIN, y-8)], fill=C_LINE, width=1)
            pd.text((x, y), txt, font=fp_font, fill=C_MUTE)

        # Salva PDF
        pages_pil[0].save(
            str(pdf_out),
            save_all=True,
            append_images=pages_pil[1:],
            resolution=DPI,
        )

        if pdf_out.exists() and pdf_out.stat().st_size > 10_000:
            pdf_path = pdf_out
            log.info(f"PDF via Pillow: {pdf_path} ({pdf_out.stat().st_size//1024}KB)")
        else:
            log.warning("PDF gerado mas muito pequeno")

    except ImportError:
        log.warning("PDF não gerado — instale Pillow: pip3 install Pillow")
    except Exception as e:
        log.warning(f"PDF não gerado: {e}")

    return report_path, pdf_path


# ══════════════════════════════════════════════════════════════════
# LOGIN IAM
# ══════════════════════════════════════════════════════════════════

def do_login_iam(page: Page, env: dict, output_dir: Path) -> Page | None:
    iam_url    = env["iam_url"]
    portal_url = env["portal_url"]
    username   = env["username"]
    password   = env["password"]

    if RICH: console.print(f"\n[bold cyan]🔐 Login IAM[/bold cyan]")
    else: print("\n🔐 Login IAM")

    print_info(f"Acessando {iam_url}")
    page.goto(iam_url, wait_until=WAIT_UNTIL, timeout=TIMEOUT)
    debug_shot(page, "01_iam_inicial", output_dir)

    try:
        el = page.wait_for_selector("#anotherAccount", timeout=5_000)
        if el:
            print_info("'use another account'")
            el.click()
            page.wait_for_load_state(WAIT_UNTIL, timeout=TIMEOUT)
    except Exception:
        pass

    print_info(f"Usuário: {username}")
    page.wait_for_selector("#inputUsername", timeout=TIMEOUT)
    page.fill("#inputUsername", username)

    print_info("Next")
    page.click("#next")
    try:
        page.wait_for_selector("#inputPassword", timeout=TIMEOUT)
    except Exception:
        page.wait_for_load_state(WAIT_UNTIL, timeout=TIMEOUT)

    print_info("Senha")
    page.wait_for_selector("#inputPassword", timeout=TIMEOUT)
    page.fill("#inputPassword", password)

    print_info("Login")
    page.click("#login")
    try:
        page.wait_for_url(lambda url: "idp/login" not in url, timeout=TIMEOUT)
    except Exception:
        page.wait_for_load_state(WAIT_UNTIL, timeout=TIMEOUT)
    debug_shot(page, "02_after_login", output_dir)

    if "idp/login" in page.url:
        print_err("Login falhou — credenciais incorretas?")
        return None
    print_ok("Login OK")

    # ── Clique no card do módulo no IAM ─────────────────────────
    module_name  = env.get("module", "").strip()
    inicio_link  = env.get("inicio_link", "/portal").strip()
    portal_host  = urlparse(portal_url).netloc

    page.wait_for_load_state(WAIT_UNTIL, timeout=TIMEOUT)
    page.wait_for_timeout(2000)

    new_page = page  # default: mesma página

    if module_name:
        print_info(f"Aguardando card '{module_name}'...")
        try:
            # Tenta encontrar o card pelo nome do módulo (texto do h4 ou título)
            # ou pelo href apontando para o portal_url
            card = None
            for sel in [
                f"a.thumbnail:has(h4:text-is('{module_name}'))",  # match exato: <a class="thumbnail"><h4>NETWIN</h4>
                f"a.thumbnail:has-text('{module_name}')",          # match parcial dentro do thumbnail
                f"a:has(h4:text-is('{module_name}'))",             # sem classe thumbnail
                f"a[href*='{portal_host}']",                       # fallback por URL do portal
            ]:
                try:
                    card = page.wait_for_selector(sel, timeout=5_000)
                    if card:
                        break
                except Exception:
                    continue

            if card:
                print_info(f"Clicando '{module_name}'...")
                try:
                    with page.context.expect_page(timeout=TIMEOUT) as new_page_info:
                        card.click()
                    new_page = new_page_info.value
                    new_page.wait_for_load_state(WAIT_UNTIL, timeout=TIMEOUT)
                except Exception:
                    # Sem nova aba — ficou na mesma página
                    card.click()
                    page.wait_for_load_state(WAIT_UNTIL, timeout=TIMEOUT)
                    new_page = page
                debug_shot(new_page, "03_after_module", output_dir)
            else:
                print_warn(f"Card '{module_name}' não encontrado — navegando direto para portal")
                new_page.goto(portal_url, wait_until=WAIT_UNTIL, timeout=TIMEOUT)
        except Exception as e:
            print_warn(f"Erro ao clicar no card '{module_name}': {e}")
            new_page = page

    # ── Clica no link de início do módulo ────────────────────────
    if inicio_link:
        print_info(f"Procurando link '{inicio_link}'...")
        try:
            inicio = new_page.wait_for_selector(
                f"a[href='{inicio_link}'], a[target='_parent'][href='{inicio_link}']",
                timeout=10_000
            )
            if inicio:
                print_info(f"Clicando '{inicio_link}'...")
                inicio.click()
                new_page.wait_for_load_state(WAIT_UNTIL, timeout=TIMEOUT)
        except Exception:
            # Se não encontrou o link, tenta navegar direto
            try:
                base = urlparse(portal_url)
                full_inicio = f"{base.scheme}://{base.netloc}{inicio_link}"
                if new_page.url.rstrip("/") != full_inicio.rstrip("/"):
                    new_page.goto(full_inicio, wait_until=WAIT_UNTIL, timeout=TIMEOUT)
            except Exception:
                pass

    return new_page


# ══════════════════════════════════════════════════════════════════
# COLETA DE MENU
# ══════════════════════════════════════════════════════════════════

def collect_menu_links(page: Page, portal_url: str) -> list[dict]:
    """
    Coleta todos os links do menu via JavaScript puro — sem hover, sem espera.
    Passa base_domain e portal_url como argumento JS para evitar f-string
    com expressões regulares (causa SyntaxError no Playwright).
    """
    page.goto(portal_url, wait_until=WAIT_UNTIL, timeout=TIMEOUT)
    wait_for_page_ready(page, "home")

    base_domain = urlparse(portal_url).netloc

    JS = """([baseHost, baseUrl]) => {
        const seen    = new Set();
        const results = [];

        const containers = document.querySelectorAll(
            'nav, [class*="menu"], [class*="nav"], [class*="sidebar"], ' +
            '[id*="menu"], [id*="nav"], [id*="sidebar"]'
        );
        const searchRoots = containers.length > 0
            ? Array.from(containers)
            : [document.body];

        for (const root of searchRoots) {
            const anchors = root.querySelectorAll('a[href]');
            for (const a of anchors) {
                const href = a.getAttribute('href') || '';
                if (!href || href === '#' || href.startsWith('javascript')
                        || href.toLowerCase().includes('logout')) continue;

                let fullUrl;
                try { fullUrl = new URL(href, baseUrl).href; }
                catch(e) { continue; }

                try { if (new URL(fullUrl).host !== baseHost) continue; }
                catch(e) { continue; }

                if (seen.has(fullUrl)) continue;
                seen.add(fullUrl);

                const label = (a.innerText || a.textContent || href).trim();
                // Limpa espaços via charCodeAt (sem regex, sem escapes problemáticos)
                let cleanLabel = '';
                let prevSpace = false;
                for (let i = 0; i < label.length; i++) {
                    const code = label.charCodeAt(i);
                    const isSpace = (code === 32 || code === 9 || code === 10 || code === 13);
                    if (isSpace) { if (!prevSpace && cleanLabel.length > 0) cleanLabel += ' '; prevSpace = true; }
                    else { cleanLabel += label[i]; prevSpace = false; }
                }
                cleanLabel = cleanLabel.trim();
                if (!cleanLabel) continue;

                results.push({ label: cleanLabel, url: fullUrl });
            }
        }
        return results;
    }"""

    try:
        raw_links = page.evaluate(JS, [base_domain, portal_url])
    except Exception as e:
        log.warning(f"collect_menu_links JS falhou: {e} — usando fallback Playwright")
        raw_links = []
        # Fallback: usa query_selector_all do Playwright
        for anchor in page.query_selector_all(SELECTOR_MENU):
            href  = anchor.get_attribute("href") or ""
            label = (anchor.inner_text() or href).strip()
            if not href or href in ("#", "") or href.startswith("javascript"):
                continue
            full_url = urljoin(portal_url, href)
            if label:
                raw_links.append({"label": label, "url": full_url})

    # Deduplica
    links, seen = [], set()
    for item in (raw_links or []):
        url   = item.get("url", "")
        label = item.get("label", "").strip()
        if url and label and url not in seen:
            seen.add(url)
            links.append({"label": label, "url": url})

    log.info(f"Menu coletado: {len(links)} links")
    return links

# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

def run_single(args, env_key: str, env: dict):
    """Executa captura para um único ambiente."""
    portal_url = env["portal_url"]
    log_file   = setup_logger(env_key)
    log.info(f"Portal  : {env['portal_url']}")
    log.info(f"IAM     : {env['iam_url']}")
    log.info(f"Usuário : {env['username']}")


def main():
    args = parse_args()

    # Modo comparação — não precisa de ambiente
    if args.compare:
        compare_screenshots(args.compare[0], args.compare[1])
        return

    # --all-envs: roda todos os módulos de todos os sistemas
    if args.all_envs:
        envs_to_run = {k: v for k, v in ENVIRONMENTS.items() if "-" in k}
        if RICH:
            console.print(f"\n[bold cyan]🌍 Executando todos os módulos ({len(envs_to_run)})...[/bold cyan]\n")
        for env_key, env in envs_to_run.items():
            if RICH:
                console.print(f"\n[bold yellow]{'='*50}[/bold yellow]")
                console.print(f"[bold]► {env['name']}[/bold]\n")
            else:
                print(f"\n{'='*50}\n► {env['name']}\n")
            args.env = env_key
            try:
                _run_env(args, env_key, env)
            except SystemExit:
                print_warn(f"{env_key} falhou — continuando...")
                continue
        return

    env_key, env = select_environment(args)

    # Opção "Todos os módulos" selecionada no menu interativo
    if getattr(args, "_run_all_modules", False):
        sys_key  = args.__dict__.get("_system_key", "")
        system   = SYSTEMS.get(sys_key, {})
        mod_envs = {f"{sys_key}-{k}": ENVIRONMENTS[f"{sys_key}-{k}"]
                    for k in system.get("modules", {})
                    if f"{sys_key}-{k}" in ENVIRONMENTS}
        if RICH:
            console.print(f"\n[bold cyan]🌍 Todos os módulos de {system.get('name',sys_key)} ({len(mod_envs)})...[/bold cyan]\n")
        for ek, ev in mod_envs.items():
            if RICH:
                console.print(f"\n[bold yellow]{'='*50}[/bold yellow]")
                console.print(f"[bold]► {ev['name']}[/bold]\n")
            else:
                print(f"\n{'='*50}\n► {ev['name']}\n")
            args.env = ek
            try:
                _run_env(args, ek, ev)
            except SystemExit:
                print_warn(f"{ek} falhou — continuando...")
                continue
        return

    _run_env(args, env_key, env)


def _run_env(args, env_key: str, env: dict):
    portal_url = env["portal_url"]

    log_file = setup_logger(env_key)
    log.info(f"Portal  : {env['portal_url']}")
    log.info(f"IAM     : {env['iam_url']}")
    log.info(f"Usuário : {env['username']}")
    if args.dry_run: log.info("Modo: DRY-RUN")
    if args.page:    log.info(f"Filtro de página: {args.page}")

    show_banner(env, Path(f"nossis_prints_{env_key}"))

    # Valida conectividade antes de iniciar (detecta VPN desconectada)
    if not args.dry_run:
        validate_connectivity(env)

    start_time = time.time()

    with sync_playwright() as p:
        browser = _launch_optimized_browser(p)

        # Tenta reusar sessão salva
        saved_session = None if args.no_session else load_session(env_key)
        if saved_session:
            session_file = SESSION_DIR / f"session_{env_key}.json"
            age_min = int((time.time() - session_file.stat().st_mtime) // 60)
            remaining = int(SESSION_TTL // 60) - age_min
            print_ok(f"Sessão salva encontrada ({age_min} min — expira em {remaining} min) — pulando login")
            context = _new_optimized_context(browser, saved_session)
        else:
            context = _new_optimized_context(browser)

        page = context.new_page()

        # Console listener para detectar erros HTTP 4xx/5xx
        current_label = [""]
        http_errors_map = {}
        def on_response(response):
            if response.status >= 400:
                lbl = current_label[0]
                msg = f"HTTP {response.status}: {response.url[:80]}"
                http_errors_map.setdefault(lbl, []).append(msg)
                log.warning(f"[{lbl}] {msg}")
        def on_console(msg):
            if msg.type == "error":
                log.debug(f"[{current_label[0]}] console.error: {msg.text[:100]}")
        page.on("response", on_response)
        page.on("console",  on_console)

        # Login (pula se sessão válida)
        try:
            temp_dir = Path(f"nossis_prints_{env_key}_temp")
            temp_dir.mkdir(exist_ok=True)
            if saved_session:
                # Verifica se sessão ainda é válida navegando para o portal
                try:
                    # Captura todos os status HTTP durante o goto
                    responses_401 = []

                    def _on_response(response):
                        if response.status in (401, 403):
                            responses_401.append(response.url)

                    page.on("response", _on_response)
                    page.goto(env['portal_url'], wait_until="domcontentloaded", timeout=30_000)
                    page.wait_for_timeout(1500)  # aguarda respostas assíncronas
                    page.remove_listener("response", _on_response)

                    # Sessão inválida se: redirecionou para login OU algum 401/403
                    portal_url_host = env['portal_url'].split("/portal")[0]
                    got_401 = any(portal_url_host in u for u in responses_401)

                    if 'idp/login' in page.url or 'login' in page.url.lower() or got_401:
                        reason = f"HTTP 401 em {len(responses_401)} request(s)" if got_401 else "redirecionado para login"
                        print_warn(f"Sessão expirada ({reason}) — fazendo login novamente...")
                        log.warning(f"Sessão inválida: {reason}")
                        clear_session(env_key)
                        portal_page = do_login_iam(page, env, temp_dir)
                        if portal_page:
                            save_session(context, env_key)
                    else:
                        portal_page = page
                        print_ok(f"Portal acessível via sessão: {page.url}")
                except Exception:
                    clear_session(env_key)
                    portal_page = do_login_iam(page, env, temp_dir)
                    if portal_page:
                        save_session(context, env_key)
            else:
                portal_page = do_login_iam(page, env, temp_dir)
                # Salva sessão após login bem-sucedido
                if portal_page:
                    save_session(context, env_key)

            if portal_page is None:
                print_err("Login falhou")
                browser.close()
                sys.exit(1)
        except KeyboardInterrupt:
            browser.close()
            sys.exit(0)
        except Exception as e:
            print_err(f"Exceção no login: {e}")
            browser.close()
            sys.exit(1)

        # Modal Sobre — extrai versão
        if RICH: console.print(f"\n[bold cyan]📸 Capturando modal 'Sobre'...[/bold cyan]")
        else: print("\n📸 Capturando modal 'Sobre'...")

        version_tag  = "unknown"
        MAX_SOBRE_ATTEMPTS = 3  # tentativas para abrir o modal e extrair versão

        for sobre_attempt in range(1, MAX_SOBRE_ATTEMPTS + 1):
            try:
                if sobre_attempt > 1:
                    print_info(f"Tentativa {sobre_attempt}/{MAX_SOBRE_ATTEMPTS} para capturar modal 'Sobre'...")
                    # Fecha modal anterior se ainda estiver aberto
                    try:
                        portal_page.keyboard.press("Escape")
                        portal_page.wait_for_timeout(500)
                    except Exception:
                        pass
                    # Recarrega a página para garantir estado limpo
                    portal_page.reload(wait_until="domcontentloaded", timeout=TIMEOUT)
                    portal_page.wait_for_timeout(2000)

                # Garante que o portal está carregado
                portal_page.wait_for_load_state("domcontentloaded", timeout=TIMEOUT)
                portal_page.wait_for_timeout(2000)

                # Tenta clicar no link "Sobre" de várias formas
                clicked = False
                for selector in [
                    "a:has-text('Sobre')",
                    "span:has-text('Sobre')",
                    "text=Sobre",
                    "[href*='sobre']",
                ]:
                    try:
                        portal_page.click(selector, timeout=3_000)
                        clicked = True
                        break
                    except Exception:
                        continue

                if not clicked:
                    portal_page.evaluate("""
                        () => {
                            const el = Array.from(document.querySelectorAll('a, span, li, button'))
                                .find(e => e.textContent.trim() === 'Sobre');
                            if (el) el.click();
                        }
                    """)

                portal_page.wait_for_timeout(1500)

                # Aguarda o modal — tenta vários seletores
                modal_visible = False
                for modal_sel in ["#nossis-modal", ".modal.in", ".modal[style*='display: block']", ".modal.show"]:
                    try:
                        portal_page.wait_for_selector(modal_sel, state="visible", timeout=5_000)
                        modal_visible = True
                        break
                    except Exception:
                        continue

                if not modal_visible:
                    log.warning(f"Modal 'Sobre' não apareceu na tentativa {sobre_attempt}")
                    if sobre_attempt < MAX_SOBRE_ATTEMPTS:
                        continue  # tenta novamente

                # Extrai a versão — varre TODO o texto do modal procurando padrão X.Y.Z
                version_raw = ""

                # 1. Seletores específicos conhecidos
                for ver_sel in [".fx-suite-desc p", ".fx-suite-desc", ".modal-body p",
                                ".modal-body", ".modal-content", "[class*='version']",
                                "[class*='suite']", "[class*='about']"]:
                    try:
                        version_raw = portal_page.evaluate(f"""
                            () => {{
                                const el = document.querySelector('{ver_sel}');
                                return el ? el.innerText.trim() : '';
                            }}
                        """)
                        if version_raw and re.search(r'[0-9]+\.[0-9]+', version_raw):
                            log.info(f"Versão via seletor '{ver_sel}': {version_raw[:80]}")
                            break
                    except Exception:
                        continue

                # 2. Varre todos os modais visíveis
                if not version_raw or not re.search(r'[0-9]+\.[0-9]+', version_raw):
                    version_raw = portal_page.evaluate("""
                        () => {
                            const modals = document.querySelectorAll(
                                '.modal, [role="dialog"], [id*="modal"], [class*="modal"]'
                            );
                            for (const m of modals) {
                                const style = window.getComputedStyle(m);
                                if (style.display !== 'none' && style.visibility !== 'hidden') {
                                    return m.innerText || m.textContent || '';
                                }
                            }
                            return '';
                        }
                    """)

                # 3. Último fallback — busca na página inteira
                if not version_raw or not re.search(r'[0-9]+\.[0-9]+\.[0-9]+', version_raw):
                    all_text = portal_page.evaluate("() => document.body ? document.body.innerText : ''")
                    m = re.search(
                        r'(?:vers[aã]o|version|v\.tal|tag)[\s:]+([0-9]+\.[0-9]+\.[0-9]+[\w\-\.]*)',
                        all_text, re.IGNORECASE
                    )
                    if m:
                        version_raw = m.group(0)

                if version_raw and re.search(r'[0-9]+\.[0-9]+\.[0-9]+', version_raw):
                    match = re.search(r'[0-9]+\.[0-9]+\.[0-9]+[\w\-\.]*', version_raw)
                    if match:
                        version_tag = match.group(0)
                    log.info(f"Versão detectada na tentativa {sobre_attempt}: {version_tag}")
                    print_ok(f"Versão: {version_tag}")
                    break  # versão encontrada — sai do loop de tentativas

                # Versão não encontrada nessa tentativa
                log.warning(f"Versão não encontrada na tentativa {sobre_attempt}/{MAX_SOBRE_ATTEMPTS}")
                if sobre_attempt == MAX_SOBRE_ATTEMPTS:
                    # Salva HTML para debug na última tentativa
                    try:
                        debug_html = portal_page.evaluate("""
                            () => {
                                const m = document.querySelector('.modal, [role=\"dialog\"]');
                                return m ? m.outerHTML : document.body.innerHTML.substring(0, 3000);
                            }
                        """)
                        Path("debug_modal.html").write_text(debug_html or "", encoding="utf-8")
                        log.warning("HTML do modal salvo em debug_modal.html")
                    except Exception:
                        pass
                    print_warn(f"Versão não encontrada após {MAX_SOBRE_ATTEMPTS} tentativas — usando 'unknown'")

            except Exception as e:
                log.warning(f"Tentativa {sobre_attempt}/{MAX_SOBRE_ATTEMPTS} falhou: {e}")
                if sobre_attempt == MAX_SOBRE_ATTEMPTS:
                    print_warn(f"Versão não detectada: {e}")

        # Define pasta com versão
        base_dir = Path(f"nossis_prints_{env_key}_{version_tag}")
        if base_dir.exists():
            ts         = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path(f"{base_dir}_{ts}")
            print_warn(f"Pasta já existe — criando: {output_dir.name}")
        else:
            output_dir = base_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        log.info(f"Saída: {output_dir.resolve()}")

        # Move debug shots da pasta temp
        for f in temp_dir.glob("*.png"):
            f.rename(output_dir / f.name)
        try: temp_dir.rmdir()
        except Exception: pass

        # Screenshot do Sobre
        try:
            sobre_path = output_dir / "00_sobre.png"
            portal_page.screenshot(path=str(sobre_path), full_page=True)
            add_timestamp_watermark(sobre_path, "Sobre")
            print_ok("00_sobre.png")
            try:
                portal_page.click("button[data-dismiss='modal']")
                portal_page.wait_for_selector("#nossis-modal", state="hidden", timeout=10_000)
                portal_page.wait_for_timeout(500)
            except Exception:
                portal_page.keyboard.press("Escape")
                portal_page.wait_for_timeout(800)
        except Exception as e:
            print_warn(f"Sobre não capturado: {e}")

        # Coleta links
        if RICH: console.print(f"\n[bold cyan]🔍 Coletando links do menu...[/bold cyan]")
        else: print("\n🔍 Coletando links do menu...")
        links = collect_menu_links(portal_page, portal_url)

        # Aplica filtro --page
        page_filter = [p.strip().lower() for p in args.page.split(",")] if args.page else None

        # Tabela de links
        if RICH:
            table = Table(box=box.ROUNDED, border_style="cyan", show_header=True,
                          header_style="bold cyan", padding=(0, 2))
            table.add_column("#",      justify="right",  width=4,  style="dim")
            table.add_column("Label",  justify="left",   width=32)
            table.add_column("Status", justify="center", width=14)
            for i, item in enumerate(links, 1):
                skip     = should_skip(item["label"], item["url"], portal_url)
                filtered = page_filter and not any(f in item["label"].lower() for f in page_filter)
                if skip:         status = "[dim]⏭ ignorar[/dim]"
                elif filtered:   status = "[dim]⏭ filtrado[/dim]"
                else:            status = "[green]✓ capturar[/green]"
                style = "dim" if (skip or filtered) else "white"
                table.add_row(str(i), f"[{style}]{item['label']}[/{style}]", status)
            console.print(table)
        else:
            for i, item in enumerate(links, 1):
                skip     = should_skip(item["label"], item["url"], portal_url)
                filtered = page_filter and not any(f in item["label"].lower() for f in page_filter)
                status   = "⏭ ignorar" if skip else ("⏭ filtrado" if filtered else "✓ capturar")
                print(f"  {i:>2}. {item['label']:<32} {status}")

        to_capture = [
            item for item in links
            if not should_skip(item["label"], item["url"], portal_url)
            and (not page_filter or any(f in item["label"].lower() for f in page_filter))
        ]

        # --since: remove páginas que não mudaram
        if args.since:
            since_dir = Path(args.since)
            if not since_dir.exists():
                print_warn(f"--since: pasta não encontrada: {since_dir}")
            else:
                ref_hashes = load_hashes(since_dir)
                before = len(to_capture)
                # Marcamos para capturar e depois comparamos
                print_info(f"--since: referência em {since_dir} ({len(ref_hashes)} screenshots)")
                log.info(f"--since ativo: {since_dir}")

        if RICH:
            console.print(f"\n[bold]📋 {len(to_capture)} páginas para capturar[/bold] [dim](de {len(links)} encontradas)[/dim]")
            if args.dry_run:
                console.print(f"\n[bold yellow]⚡ DRY-RUN — nenhuma captura será feita.[/bold yellow]\n")
        else:
            print(f"\n📋 {len(to_capture)} para capturar (de {len(links)})")
            if args.dry_run: print("⚡ DRY-RUN\n")

        if args.dry_run:
            browser.close()
            return

        if not to_capture:
            print_warn("Nenhuma página para capturar.")
            browser.close()
            return

        # ── Captura: paralela ou sequencial ──────────────────────
        capture_results = []
        errors          = []
        n_threads       = calc_threads(len(to_capture))
        session_file    = SESSION_DIR / f"session_{env_key}.json"

        if n_threads > 1:
            # ── MODO PARALELO ─────────────────────────────────────
            # fecha o portal_page do thread principal — workers abrem os seus
            portal_page.close()
            context.close()
            browser.close()

            capture_results = parallel_capture(
                to_capture, output_dir, env,
                session_file, args.retries, http_errors_map
            )
            errors = [(r["label"], "", r["msg"])
                      for r in capture_results if r["status"] == "erro"]

            # Exibe resumo do que foi capturado
            if RICH:
                for r in capture_results:
                    icon  = "✓" if r["status"] == "ok" else ("⚠" if r["status"] == "aviso" else "✗")
                    color = "green" if r["status"] == "ok" else ("yellow" if r["status"] == "aviso" else "red")
                    console.print(f"  [{color}]{icon}[/{color}] {r['label']:<35} {r['time']}")
            else:
                for r in capture_results:
                    icon = "✓" if r["status"] == "ok" else ("⚠" if r["status"] == "aviso" else "✗")
                    print(f"  {icon} {r['label']:<35} {r['time']}")

            # Marca que browser já foi fechado
            browser_closed = True

        else:
            # ── MODO SEQUENCIAL ───────────────────────────────────
            browser_closed = False
            if RICH:
                with Progress(SpinnerColumn(), TextColumn("[bold cyan]{task.description}[/bold cyan]"),
                              BarColumn(bar_width=30), TaskProgressColumn(),
                              TextColumn("[dim]{task.fields[label]}[/dim]"), console=console) as progress:
                    task = progress.add_task("Capturando", total=len(to_capture), label="")
                    for i, item in enumerate(to_capture, 1):
                        label    = item["label"]
                        url      = item["url"]
                        filename = f"{i:02d}_{sanitize(label)}.png"
                        filepath = output_dir / filename
                        progress.update(task, label=label)
                        current_label[0] = label
                        t0 = time.time()
                        log.info(f"[{i}/{len(to_capture)}] {label} → {url}")
                        ok, msg = capture_with_retry(portal_page, url, filepath, label, args.retries)
                        elapsed_p = time.time() - t0
                        if ok:
                            add_timestamp_watermark(filepath, label)
                            log.info(f"[{i}/{len(to_capture)}] ✓ {filename} ({elapsed_p:.1f}s) {msg}")
                            http_err = http_errors_map.get(label, [])
                            extra_msg = (" | " + "; ".join(http_err[:2])) if http_err else ""
                            status = "aviso" if (msg.startswith("AVISO") or http_err) else "ok"
                            final_msg = (msg if msg.startswith("AVISO") else "") + extra_msg
                            capture_results.append({"label": label, "file": str(filepath),
                                                    "status": status, "time": f"{elapsed_p:.1f}s",
                                                    "msg": final_msg.strip(" |").strip()})
                        else:
                            log.error(f"[{i}/{len(to_capture)}] ✗ {label}: {msg}")
                            errors.append((label, url, msg))
                            capture_results.append({"label": label, "file": str(filepath),
                                                    "status": "erro", "time": f"{elapsed_p:.1f}s", "msg": msg})
                        progress.advance(task)
            else:
                for i, item in enumerate(to_capture, 1):
                    label    = item["label"]
                    url      = item["url"]
                    filename = f"{i:02d}_{sanitize(label)}.png"
                    filepath = output_dir / filename
                    print(f"[{i:>2}/{len(to_capture)}] {label:<35}", end=" ", flush=True)
                    current_label[0] = label
                    t0 = time.time()
                    ok, msg = capture_with_retry(portal_page, url, filepath, label, args.retries)
                    elapsed_p = time.time() - t0
                    if ok:
                        add_timestamp_watermark(filepath, label)
                        http_err = http_errors_map.get(label, [])
                        extra_msg = (" | " + "; ".join(http_err[:2])) if http_err else ""
                        status = "aviso" if (msg.startswith("AVISO") or http_err) else "ok"
                        final_msg = (msg if msg.startswith("AVISO") else "") + extra_msg
                        print(f"✓ {filename} ({elapsed_p:.1f}s)")
                        capture_results.append({"label": label, "file": str(filepath),
                                                "status": status, "time": f"{elapsed_p:.1f}s",
                                                "msg": final_msg.strip(" |").strip()})
                    else:
                        print(f"✗ ERRO ({args.retries} tentativas)")
                        errors.append((label, url, msg))
                        capture_results.append({"label": label, "file": str(filepath),
                                                "status": "erro", "time": f"{elapsed_p:.1f}s", "msg": msg})

        # Adiciona o Sobre ao relatório
        sobre_path = output_dir / "00_sobre.png"
        capture_results.insert(0, {"label": "Sobre", "file": str(sobre_path),
                                   "status": "ok" if sobre_path.exists() else "erro",
                                   "time": "—", "msg": ""})

        # Fecha browser se ainda não foi fechado (modo sequencial)
        if not browser_closed:
            portal_page.close()
            context.close()
            browser.close()

    # Gera relatório HTML
    elapsed  = time.time() - start_time
    rep_path, pdf_path = generate_report(output_dir, env, version_tag, capture_results, elapsed, log_file)
    print_ok(f"Relatório HTML: {rep_path}")
    if pdf_path:
        print_ok(f"Relatório PDF : {pdf_path}")
    else:
        print_info("PDF não gerado — instale weasyprint: pip3 install weasyprint")

    # Gera README.txt
    readme_path = generate_readme(output_dir, env, version_tag, capture_results, elapsed, rep_path, pdf_path)
    print_ok(f"README       : {readme_path}")

    # Resumo final
    total = len(capture_results)
    ok    = sum(1 for r in capture_results if r["status"] == "ok")
    warn  = sum(1 for r in capture_results if r["status"] == "aviso")
    err   = sum(1 for r in capture_results if r["status"] == "erro")

    log.info("=" * 70)
    log.info(f"Sucesso: {ok}/{total} | Avisos: {warn} | Erros: {err}")
    log.info(f"Duração: {elapsed/60:.1f} min | Pasta: {output_dir.resolve()}")
    log.info("=" * 70)

    if RICH:
        summary = (
            f"[bold cyan]Ambiente  :[/bold cyan] {env['name']}  [dim]v{version_tag}[/dim]\n"
            f"[bold green]✓ OK      :[/bold green] {ok}/{total}\n"
            f"[bold yellow]⚠ Avisos  :[/bold yellow] {warn}\n"
            f"[bold red]✗ Erros   :[/bold red] {err}\n"
            f"[bold cyan]⏱ Duração :[/bold cyan] {elapsed/60:.1f} min ({elapsed:.0f}s)\n"
            f"[bold cyan]📁 Pasta   :[/bold cyan] {output_dir.resolve()}\n"
            f"[bold cyan]📊 HTML      :[/bold cyan] {rep_path}\n"
            f"[bold cyan]📄 PDF       :[/bold cyan] {pdf_path or 'pip3 install weasyprint'}\n"
            f"[bold cyan]📋 Log     :[/bold cyan] {log_file.resolve()}\n"
            f"[bold cyan]📝 README  :[/bold cyan] {readme_path}"
        )
        console.print(Panel(summary, title="[bold white]✅ Concluído[/bold white]",
                            border_style="green", padding=(1, 2)))
    else:
        print(f"\n{'═'*60}")
        print(f"  ✓ OK      : {ok}/{total}")
        print(f"  ⚠ Avisos  : {warn}")
        print(f"  ✗ Erros   : {err}")
        print(f"  ⏱ Duração : {elapsed/60:.1f} min")
        print(f"  📁 Pasta  : {output_dir.resolve()}")
        print(f"  📊 HTML    : {rep_path}")
        print(f"  📄 PDF     : {pdf_path or 'pip3 install weasyprint'}")
        print(f"{'═'*60}\n")


if __name__ == "__main__":
    main()