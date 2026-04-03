"""
╔══════════════════════════════════════════════════════════════════╗
║           NOSSIS ONE INVENTORY — Screenshot Automático           ║
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
║  Versão    : 6.0                                                 ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║  CHANGELOG                                                       ║
╠══════════════════════════════════════════════════════════════════╣
║  v6.0  · Sessão/cookies salva e reutilizada entre execuções      ║
║        · Detecção de submenus expandidos (hover)                 ║
║        · Log embutido no HTML do relatório                       ║
║        · README.txt gerado na pasta de saída                     ║
║        · Modo --all-envs (todos os ambientes em sequência)       ║
║        · Modo --since (só páginas que mudaram)                   ║
║        · Captura de menus expandidos via hover                   ║
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
    """Carrega sessão salva se existir e for recente (< 8h)."""
    try:
        session_file = SESSION_DIR / f"session_{env_key}.json"
        if not session_file.exists():
            return None
        age = time.time() - session_file.stat().st_mtime
        if age > 8 * 3600:  # expirada após 8h
            log.info("Sessão expirada — novo login necessário")
            return None
        import json
        data = json.loads(session_file.read_text(encoding="utf-8"))
        log.info(f"Sessão carregada: {session_file} (idade: {age/3600:.1f}h)")
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
        "  NOSSIS ONE INVENTORY — Evidências de Screenshot",
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
        "  Gerado por NOSSIS Screenshot Automático v6.0",
        "=" * 65,
    ]

    readme_path = output_dir / "README.txt"
    readme_path.write_text("\n".join(lines), encoding="utf-8")
    log.info(f"README gerado: {readme_path}")
    return readme_path


# ══════════════════════════════════════════════════════════════════
# AMBIENTES
# ══════════════════════════════════════════════════════════════════
ENVIRONMENTS = {
    "int": {
        "name":       "INT — Dev (V.Tal)",
        "iam_url":    "https://iam-dev-vtal.10.51.195.98.nip.io/idp/login",
        "portal_url": "https://netwin-dev-vtal.10.51.195.98.nip.io/portal",
        "username":   "netwin",
        "password":   "netwin",
    },
    "hml": {
        "name":       "HML — Dev (OCP Arc)",
        "iam_url":    "https://iam-nossis-dev.apps.ocparc-nprd.vtal.intra/idp/login",
        "portal_url": "https://netwin-nossis-dev.apps.ocparc-nprd.vtal.intra/portal",
        "username":   "netwin",
        "password":   "Netwin123456!!",
    },
    # "prd": {
    #     "name":       "PRD — Produção",
    #     "iam_url":    "https://iam-prd.exemplo.com/idp/login",
    #     "portal_url": "https://netwin-prd.exemplo.com/portal",
    #     "username":   "usuario",
    #     "password":   "senha",
    # },
}

# ══════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO GERAL
# ══════════════════════════════════════════════════════════════════
SELECTOR_MENU = "nav a, .menu a, #menu a, .sidebar a, [class*='menu'] a, [class*='nav'] a"
TIMEOUT       = 120_000
WAIT_UNTIL    = "load"
MAX_RETRIES   = 2      # tentativas extras em caso de falha

SKIP_LABELS   = ["outros módulos", "outros modulos"]
SKIP_URLS     = ["/portal#", "/portal/home", "/portal/outros"]

EXTRA_WAIT    = {
    "OSP":         8_000,
    "Viabilidade": 10_000,
}

# Arquivo de sessão salva
SESSION_DIR = Path(".nossis_sessions")

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

    log.info("=" * 70)
    log.info("NOSSIS Screenshot Automático v5.0")
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
            title="[bold white]NOSSIS ONE INVENTORY — Screenshot Automático v5.0[/bold white]",
            border_style="cyan", padding=(1, 2)))
    else:
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║       NOSSIS ONE INVENTORY — Screenshot Automático v5.0         ║")
        print(f"║  Ambiente : {env['name']:<53}║")
        print(f"║  Início   : {now:<53}║")
        print(f"║  Saída    : {str(output_dir):<53}║")
        print("╚══════════════════════════════════════════════════════════════════╝")
    print()


def parse_args():
    """Parse argumentos CLI."""
    parser = argparse.ArgumentParser(
        description="NOSSIS Screenshot Automático v5.0",
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


def select_environment(args) -> tuple[str, dict]:
    env_keys = list(ENVIRONMENTS.keys())

    if args.env:
        key = args.env.lower()
        if key in ENVIRONMENTS:
            return key, ENVIRONMENTS[key]
        if RICH:
            console.print(f"[red]❌ Ambiente '{key}' não encontrado.[/red]")
            console.print(f"   Disponíveis: [cyan]{', '.join(env_keys)}[/cyan]")
        else:
            print(f"❌ Ambiente '{key}' não encontrado. Disponíveis: {', '.join(env_keys)}")
        sys.exit(1)

    if RICH:
        console.print()
        banner_text = (
            "[bold cyan] ███╗   ██╗ ██████╗ ███████╗███████╗██╗███████╗[/bold cyan]\n"
            "[bold cyan] ████╗  ██║██╔═══██╗██╔════╝██╔════╝██║██╔════╝[/bold cyan]\n"
            "[bold cyan] ██╔██╗ ██║██║   ██║███████╗███████╗██║███████╗[/bold cyan]\n"
            "[bold cyan] ██║╚██╗██║██║   ██║╚════██║╚════██║██║╚════██║[/bold cyan]\n"
            "[bold cyan] ██║ ╚████║╚██████╔╝███████║███████║██║███████║[/bold cyan]\n"
            "[bold cyan] ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝╚═╝╚══════╝[/bold cyan]\n"
            "\n"
            "[bold white]ONE INVENTORY[/bold white]  [dim]— Screenshot Automático v5.0[/dim]\n"
            "[dim]Diego Santos · diego-f-santos@openlabs.com.br[/dim]"
        )
        W = 120
        console.print(Panel(Align.center(banner_text), border_style="cyan", padding=(1, 4), width=W))
        console.print()

        table = Table(box=box.ROUNDED, border_style="cyan", show_header=True,
                      header_style="bold cyan", padding=(0, 2), show_lines=True, width=W)
        table.add_column("#",        style="bold white",  justify="center", width=5,  no_wrap=True, min_width=5)
        table.add_column("Chave",    style="bold yellow", justify="center", width=10, no_wrap=True)
        table.add_column("Ambiente", style="white",       justify="left",   width=26, no_wrap=True)
        table.add_column("Portal",   style="cyan",        justify="left",   width=74, no_wrap=True)

        for i, (key, env) in enumerate(ENVIRONMENTS.items(), 1):
            table.add_row(str(i), key.upper(), env["name"], env["portal_url"])
        table.add_section()
        table.add_row("[dim]0[/dim]", "[dim]---[/dim]", "[dim]Sair[/dim]", "")
        console.print(table)
        console.print()

        while True:
            try:
                choice = Prompt.ask(f"[bold cyan]Selecione[/bold cyan] [dim](0-{len(env_keys)})[/dim]", default="0")
                idx = int(choice)
                if idx == 0:
                    console.print("\n[dim]Encerrando...[/dim]")
                    sys.exit(0)
                if 1 <= idx <= len(env_keys):
                    key = env_keys[idx - 1]
                    console.print(f"\n[green]✓[/green] Ambiente: [bold]{ENVIRONMENTS[key]['name']}[/bold]\n")
                    return key, ENVIRONMENTS[key]
                console.print(f"[red]Opção inválida.[/red] Digite 0 a {len(env_keys)}.")
            except (ValueError, EOFError):
                console.print(f"[red]Opção inválida.[/red]")
            except KeyboardInterrupt:
                console.print("\n\n[dim]Interrompido.[/dim]")
                sys.exit(0)
    else:
        print("\n┌─────────────────────────────────────────┐")
        print("│   NOSSIS — Selecione o ambiente          │")
        print("├─────────────────────────────────────────┤")
        for i, (key, env) in enumerate(ENVIRONMENTS.items(), 1):
            print(f"│  {i}. [{key.upper():>3}]  {env['name']:<30}│")
        print("│  0.  Sair                                │")
        print("└─────────────────────────────────────────┘")
        while True:
            try:
                choice = input(f"\nOpção [0-{len(env_keys)}]: ").strip()
                idx = int(choice)
                if idx == 0:
                    sys.exit(0)
                if 1 <= idx <= len(env_keys):
                    return env_keys[idx - 1], ENVIRONMENTS[env_keys[idx - 1]]
            except (ValueError, EOFError):
                pass
            except KeyboardInterrupt:
                sys.exit(0)
            print("Opção inválida.")


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


def wait_for_page_ready(page: Page, label: str = ""):
    try:
        page.wait_for_selector("text=A carregar página", state="hidden", timeout=60_000)
    except Exception:
        pass
    extra = next((ms for key, ms in EXTRA_WAIT.items() if key.lower() in label.lower()), 0)
    if extra:
        print_info(f"+{extra//1000}s extra para '{label}'...")
    page.wait_for_timeout(1500 + extra)


def debug_shot(page: Page, nome: str, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        page.screenshot(path=str(output_dir / f"debug_{nome}.png"), full_page=True)
    except Exception:
        pass


def validate_screenshot(page: Page, filepath: Path) -> tuple[bool, str]:
    """
    Valida se o screenshot capturado é uma página válida.
    Retorna (ok, motivo).
    """
    # Verifica URL atual — se voltou pra login ou erro
    current_url = page.url.lower()
    for indicator in ERROR_INDICATORS:
        if indicator in current_url:
            return False, f"URL suspeita: {page.url}"

    # Verifica título da página
    try:
        title = page.title().lower()
        for indicator in ["error", "404", "403", "acesso negado", "not found"]:
            if indicator in title:
                return False, f"Título suspeito: {page.title()}"
    except Exception:
        pass

    # Verifica tamanho do arquivo (< 10KB pode ser página branca)
    if filepath.exists() and filepath.stat().st_size < 10_000:
        return False, f"Imagem muito pequena ({filepath.stat().st_size} bytes) — possível página branca"

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
                page.wait_for_timeout(2000)

            page.goto(url, wait_until=WAIT_UNTIL, timeout=TIMEOUT)
            wait_for_page_ready(page, label)
            page.screenshot(path=str(filepath), full_page=True)

            # Validação pós-screenshot
            ok, motivo = validate_screenshot(page, filepath)
            if not ok:
                print_warn(f"Validação falhou para '{label}': {motivo}")
                log.warning(f"Validação: [{label}] {motivo}")
                # Não marca como erro — salva mesmo assim com aviso
                return True, f"AVISO: {motivo}"

            return True, "ok"

        except Exception as e:
            last_error = str(e)
            log.error(f"Tentativa {attempt+1}/{1+retries} falhou para '{label}': {e}")

            # Screenshot parcial do que carregou
            try:
                partial_path = filepath.parent / f"PARCIAL_{filepath.name}"
                page.screenshot(path=str(partial_path), full_page=True)
                log.info(f"Screenshot parcial salvo: {partial_path.name}")
                print_warn(f"Screenshot parcial salvo: {partial_path.name}")
            except Exception:
                pass

    return False, last_error


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
<h1>🔍 Comparação de Screenshots — NOSSIS ONE INVENTORY</h1>
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

    STATUS_COLOR = {"ok": "#00c896", "aviso": "#ffb300", "erro": "#ff4757"}
    STATUS_ICON  = {"ok": "✓", "aviso": "⚠", "erro": "✗"}
    STATUS_LABEL = {"ok": "OK", "aviso": "Aviso", "erro": "Erro"}

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
    <p class="cover-subtitle">Screenshot Automático · v5.0</p>

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
<div class="page-break"></div>
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
<div class="page-break"></div>
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
            img_html = f'<a href="{img_src}" target="_blank"><img src="{img_src}" class="ev-img" loading="lazy"></a>'
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
<div class="page-break"></div>
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

    /* ── PAGE BREAK ── */
    .page-break { page-break-after:always; break-after:page }

    /* ── PÁGINA DE EVIDÊNCIAS (2 por página) ── */
    .ev-page {
      max-width:1200px; margin:0 auto; padding:24px 36px;
      display:flex; flex-direction:column; gap:24px;
      position:relative;
    }
    .ev-page::after {
      content: attr(data-page);
      position:fixed; bottom:18px; right:28px;
      font-family:var(--mono); font-size:11px; color:var(--muted);
      background:var(--bg2); border:1px solid var(--border);
      border-radius:20px; padding:3px 12px;
      pointer-events:none;
    }

    /* ── NUMERAÇÃO DE PÁGINAS (CSS counter) ── */
    body { counter-reset: page-counter }
    .page-break { counter-increment: page-counter }

    /* ── PRINT ── */
    @media print {
      body { background:#fff; color:#000 }
      .cover { background:#fff; min-height:auto }
      .cover-logo-wrap, .cover-title, .section-title { color:#005a6e }
      .cover::before { display:none }
      .ev-item { break-inside:avoid; page-break-inside:avoid; border:1px solid #ddd }
      .ev-header { background:#f5f5f5 }
      .summary-table th { background:#f0f0f0; color:#005a6e }

      /* Numeração real no PDF via @page */
      @page {
        margin: 20mm 15mm 25mm 15mm;
        @bottom-center {
          content: "NOSSIS ONE INVENTORY  ·  " attr(data-env) "  ·  Página " counter(page) " de " counter(pages);
          font-size: 9pt;
          color: #999;
          font-family: monospace;
        }
        @bottom-right {
          content: "v " attr(data-version);
          font-size: 9pt;
          color: #aaa;
          font-family: monospace;
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

    # ── PDF ───────────────────────────────────────────────────────
    pdf_path = None
    try:
        import subprocess
        pdf_out = output_dir / f"relatorio_{now_file}.pdf"
        try:
            import weasyprint
            weasyprint.HTML(filename=str(report_path)).write_pdf(str(pdf_out))
            pdf_path = pdf_out
            log.info(f"PDF via weasyprint: {pdf_path}")
        except ImportError:
            chromium = Path.home() / ".cache/ms-playwright/chromium-1208/chrome-linux64/chrome"
            if chromium.exists():
                subprocess.run([
                    str(chromium), "--headless", "--no-sandbox", "--disable-gpu",
                    f"--print-to-pdf={pdf_out}", "--print-to-pdf-no-header",
                    f"file://{report_path.resolve()}"
                ], capture_output=True, timeout=60)
                if pdf_out.exists():
                    pdf_path = pdf_out
                    log.info(f"PDF via chromium: {pdf_path}")
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

    print_info("Aguardando card NETWIN...")
    page.wait_for_load_state(WAIT_UNTIL, timeout=TIMEOUT)
    page.wait_for_timeout(2000)

    try:
        netwin_card = page.wait_for_selector(
            f"a.thumbnail[href*='{urlparse(portal_url).netloc}'], a[href*='{urlparse(portal_url).netloc}']",
            timeout=TIMEOUT
        )
        print_info("Clicando NETWIN...")
        with page.context.expect_page(timeout=TIMEOUT) as new_page_info:
            netwin_card.click()
        new_page = new_page_info.value
        new_page.wait_for_load_state(WAIT_UNTIL, timeout=TIMEOUT)
        debug_shot(new_page, "03_after_netwin", output_dir)
    except Exception as e:
        print_warn(f"Card NETWIN não encontrado: {e}")
        new_page = page

    print_info("Procurando link 'início'...")
    try:
        inicio = new_page.wait_for_selector("a[href='/portal']", timeout=10_000)
        if inicio:
            print_info("Clicando 'início'...")
            inicio.click()
            new_page.wait_for_load_state(WAIT_UNTIL, timeout=TIMEOUT)
    except Exception:
        pass

    return new_page


# ══════════════════════════════════════════════════════════════════
# COLETA DE MENU
# ══════════════════════════════════════════════════════════════════

def collect_menu_links(page: Page, portal_url: str) -> list[dict]:
    page.goto(portal_url, wait_until=WAIT_UNTIL, timeout=TIMEOUT)
    wait_for_page_ready(page, "home")

    links, seen = [], set()
    base_domain = urlparse(portal_url).netloc

    def harvest_anchors():
        """Coleta todos os links visíveis no momento."""
        for anchor in page.query_selector_all(SELECTOR_MENU):
            href  = anchor.get_attribute("href") or ""
            label = (anchor.inner_text() or href).strip()
            if not href or href in ("#", "") or href.startswith("javascript") or "logout" in href.lower():
                continue
            full_url = urljoin(portal_url, href)
            if urlparse(full_url).netloc != base_domain:
                continue
            if full_url not in seen and label:
                seen.add(full_url)
                links.append({"label": label, "url": full_url})

    # Coleta links do estado inicial
    harvest_anchors()

    # Expande submenus via hover para capturar links ocultos
    try:
        menu_triggers = page.query_selector_all(
            "nav [class*='dropdown'], nav [class*='submenu'], "
            "nav li:has(ul), [class*='nav'] li:has(ul), "
            "[data-toggle='dropdown'], [data-bs-toggle='dropdown']"
        )
        print_info(f"Expandindo {len(menu_triggers)} submenu(s)...")
        for trigger in menu_triggers[:10]:  # limita a 10 para não travar
            try:
                trigger.hover(timeout=2_000)
                page.wait_for_timeout(300)
                harvest_anchors()
            except Exception:
                continue
        # Retorna ao estado normal
        try:
            page.mouse.move(0, 0)
            page.wait_for_timeout(200)
        except Exception:
            pass
        log.info(f"Menu coletado: {len(links)} links (incluindo submenus)")
    except Exception as e:
        log.warning(f"Erro ao expandir submenus: {e}")

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

    # --all-envs: roda em todos os ambientes em sequência
    if args.all_envs:
        if RICH:
            console.print(f"\n[bold cyan]🌍 Executando em todos os ambientes ({len(ENVIRONMENTS)})...[/bold cyan]\n")
        for env_key, env in ENVIRONMENTS.items():
            if RICH: console.print(f"\n[bold yellow]{'='*50}[/bold yellow]")
            if RICH: console.print(f"[bold]Ambiente: {env['name']}[/bold]\n")
            else: print(f"\n{'='*50}\nAmbiente: {env['name']}\n")
            # Roda como se fosse argumento CLI
            args.env = env_key
            try:
                _run_env(args, env_key, env)
            except SystemExit:
                print_warn(f"Ambiente {env_key} falhou — continuando...")
                continue
        return

    env_key, env = select_environment(args)
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
        browser = p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])

        # Tenta reusar sessão salva
        saved_session = None if args.no_session else load_session(env_key)
        if saved_session:
            print_ok("Sessão salva encontrada — pulando login")
            context = browser.new_context(
                viewport={"width": 1600, "height": 900},
                ignore_https_errors=True,
                storage_state=saved_session
            )
        else:
            context = browser.new_context(viewport={"width": 1600, "height": 900}, ignore_https_errors=True)

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
                    page.goto(env['portal_url'], wait_until=WAIT_UNTIL, timeout=30_000)
                    if 'idp/login' in page.url or 'login' in page.url.lower():
                        print_warn("Sessão expirada — fazendo login novamente...")
                        clear_session(env_key)
                        portal_page = do_login_iam(page, env, temp_dir)
                    else:
                        portal_page = page
                        print_ok(f"Portal acessível via sessão: {page.url}")
                except Exception:
                    portal_page = do_login_iam(page, env, temp_dir)
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

        version_tag = "unknown"
        try:
            portal_page.wait_for_load_state("load", timeout=TIMEOUT)
            wait_for_page_ready(portal_page, "home")
            portal_page.evaluate("""
                () => {
                    const el = Array.from(document.querySelectorAll('a, span'))
                        .find(e => e.textContent.trim() === 'Sobre');
                    if (el) el.click();
                }
            """)
            portal_page.wait_for_selector("#nossis-modal", state="visible", timeout=10_000)
            portal_page.wait_for_timeout(800)

            version_raw = portal_page.evaluate("""
                () => {
                    const el = document.querySelector('.fx-suite-desc p');
                    return el ? el.textContent.trim() : '';
                }
            """)
            if version_raw:
                match = re.search(r'[0-9]+\.[0-9]+\.[0-9]+[\w\-\.]*', version_raw)
                if match:
                    version_tag = match.group(0)
                log.info(f"Versão: {version_raw} → tag: {version_tag}")
                print_ok(f"Versão: {version_tag}")

        except Exception as e:
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

        # Screenshots com retry
        capture_results = []
        errors = []

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
