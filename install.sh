#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════╗
# ║  AutoScreen v7.1 — Instalação Automática                        ║
# ║  Autor : Diego Regis M. F. dos Santos                           ║
# ║  Email : diego-f-santos@openlabs.com.br                         ║
# ║  Time  : OpenLabs - DevOps | Infra                              ║
# ║  Versão: 1.0                                                    ║
# ╚══════════════════════════════════════════════════════════════════╝
#
# Uso:
#   chmod +x install.sh && sudo ./install.sh
#
# O que este script faz:
#   1. Verifica Python 3.8+
#   2. Instala dependências Python (pip)
#   3. Instala Chromium via Playwright
#   4. Instala fontes Liberation Sans (padrão ABNT)
#   5. Instala em /opt/autoscreen/ (acessível por todos os usuários)
#   6. Cria wrapper /usr/local/bin/autoscreen
#   7. Valida instalação completa

set -e

# ── Cores ──────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

ok()   { echo -e "  ${GREEN}✓${RESET} $1"; }
warn() { echo -e "  ${YELLOW}⚠${RESET}  $1"; }
err()  { echo -e "  ${RED}✗${RESET} $1"; exit 1; }
info() { echo -e "  ${CYAN}→${RESET} $1"; }
step() { echo -e "\n${BOLD}$1${RESET}"; }

# ── Banner ─────────────────────────────────────────────────────────
echo -e "${CYAN}"
echo "     ___         __       _____                          "
echo "    /   | __  __/ /_____ / ___/_____________  ___  ____  "
echo "   / /| |/ / / / __/ __ \__ \/ ___/ ___/ _ \/ _ \/ __ \ "
echo "  / ___ / /_/ / /_/ /_/ /__/ / /__/ /  /  __/  __/ / / /"
echo " /_/  |_\__,_/\__/\____/____/\___/_/   \___/\___/_/ /_/ "
echo -e "${RESET}"
echo -e "  ${BOLD}AutoScreen v7.1 — Instalação${RESET}"
echo -e "  Diego Santos · diego-f-santos@openlabs.com.br"
echo "  ──────────────────────────────────────────────"

# ── Verifica root (necessário para /opt e /usr/local/bin) ──────────
if [ "$EUID" -ne 0 ]; then
    warn "Este script precisa de privilégios root para instalar em /opt/"
    warn "Execute: sudo ./install.sh"
    echo ""
    read -rp "  Continuar sem root? (instalação local em ~/autoscreen) [s/N] " RESP
    if [[ "$RESP" =~ ^[Ss]$ ]]; then
        INSTALL_DIR="$HOME/autoscreen"
        WRAPPER_DIR="$HOME/.local/bin"
        GLOBAL_INSTALL=false
        warn "Instalação local em $INSTALL_DIR"
    else
        exit 1
    fi
else
    INSTALL_DIR="/opt/autoscreen"
    WRAPPER_DIR="/usr/local/bin"
    GLOBAL_INSTALL=true
    info "Instalação global em $INSTALL_DIR"
fi

# ── Detecta script principal ───────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_SCRIPT=""
for name in nossis_screenshotter.py autoscreen.py screenshotter.py; do
    if [ -f "$SCRIPT_DIR/$name" ]; then
        MAIN_SCRIPT="$SCRIPT_DIR/$name"
        MAIN_SCRIPT_NAME="$name"
        break
    fi
done

# ── 1. Python ──────────────────────────────────────────────────────
step "1. Verificando Python..."

if command -v python3 &>/dev/null; then
    PY=python3
    PIP=pip3
elif command -v python &>/dev/null; then
    PY=python
    PIP=pip
else
    err "Python não encontrado. Instale Python 3.8+ e tente novamente."
fi

PY_VERSION=$($PY -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$($PY -c "import sys; print(sys.version_info.major)")
PY_MINOR=$($PY -c "import sys; print(sys.version_info.minor)")

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 8 ]; }; then
    err "Python $PY_VERSION encontrado. Necessário Python 3.8+."
fi

ok "Python $PY_VERSION ($PY)"

# ── 2. pip ─────────────────────────────────────────────────────────
step "2. Verificando pip..."

if ! $PY -m pip --version &>/dev/null; then
    info "pip não encontrado — instalando..."
    $PY -m ensurepip --upgrade 2>/dev/null || {
        warn "ensurepip falhou — tentando get-pip.py..."
        curl -sS https://bootstrap.pypa.io/get-pip.py | $PY
    }
fi

ok "pip disponível"

# ── 3. Dependências Python ─────────────────────────────────────────
step "3. Instalando dependências Python..."

PACKAGES=(
    "playwright"    # automação de browser
    "Pillow"        # análise de imagem e geração de PDF
    "rich"          # terminal com cores, menus e barras de progresso
)

for pkg in "${PACKAGES[@]}"; do
    info "Instalando $pkg..."
    $PIP install "$pkg" --quiet --break-system-packages 2>/dev/null \
        || $PIP install "$pkg" --quiet 2>/dev/null \
        || warn "$pkg pode já estar instalado ou falhou — continuando..."
    ok "$pkg"
done

# ── 4. Playwright + Chromium ───────────────────────────────────────
step "4. Instalando Chromium (Playwright)..."

info "Isso pode demorar alguns minutos na primeira vez..."

# Playwright instala o Chromium no diretório do usuário que rodar
# Para instalação global, instala como root E instrui cada usuário
$PY -m playwright install chromium
ok "Chromium instalado (usuário: $(whoami))"

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    info "Instalando dependências do sistema para Chromium..."
    $PY -m playwright install-deps chromium 2>/dev/null \
        || warn "playwright install-deps falhou — pode precisar de sudo"
fi

# ── 5. Fontes Liberation Sans (padrão ABNT) ────────────────────────
step "5. Instalando fontes Liberation Sans..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v apt-get &>/dev/null; then
        apt-get install -y fonts-liberation 2>/dev/null \
            || warn "Não foi possível instalar fontes via apt — PDF usará fonte padrão"
        ok "Liberation Sans instalada"
    elif command -v yum &>/dev/null; then
        yum install -y liberation-fonts 2>/dev/null \
            || warn "Não foi possível instalar fontes via yum"
        ok "Liberation Sans instalada"
    elif command -v dnf &>/dev/null; then
        dnf install -y liberation-fonts 2>/dev/null \
            || warn "Não foi possível instalar fontes via dnf"
        ok "Liberation Sans instalada"
    else
        warn "Gerenciador de pacotes não reconhecido — instale fonts-liberation manualmente"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v brew &>/dev/null; then
        brew install --cask font-liberation 2>/dev/null || true
        ok "Liberation Sans instalada via Homebrew"
    else
        warn "Homebrew não encontrado — instale a fonte manualmente"
    fi
else
    warn "Sistema não reconhecido — instale Liberation Sans manualmente para PDF ABNT"
fi

# ── 6. Instalação em /opt/autoscreen ──────────────────────────────
step "6. Instalando AutoScreen em $INSTALL_DIR..."

# Cria diretório de instalação
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "$INSTALL_DIR/.nossis_sessions"

# Copia o script principal
if [ -n "$MAIN_SCRIPT" ]; then
    cp "$MAIN_SCRIPT" "$INSTALL_DIR/$MAIN_SCRIPT_NAME"
    chmod 755 "$INSTALL_DIR/$MAIN_SCRIPT_NAME"
    ok "Script copiado → $INSTALL_DIR/$MAIN_SCRIPT_NAME"
else
    warn "Script principal não encontrado nesta pasta — copie manualmente para $INSTALL_DIR/"
fi

# Copia este install.sh para referência futura
cp "${BASH_SOURCE[0]}" "$INSTALL_DIR/install.sh"
chmod 755 "$INSTALL_DIR/install.sh"

# Permissões: todos os usuários podem ler e escrever nas pastas de saída
chmod -R 755 "$INSTALL_DIR"
chmod -R 777 "$INSTALL_DIR/logs"
chmod -R 777 "$INSTALL_DIR/.nossis_sessions"

ok "Estrutura criada em $INSTALL_DIR"

# ── 7. Wrapper /usr/local/bin/autoscreen ──────────────────────────
step "7. Criando comando 'autoscreen'..."

mkdir -p "$WRAPPER_DIR"

# Detecta nome do script principal instalado
if [ -n "$MAIN_SCRIPT_NAME" ]; then
    TARGET_SCRIPT="$INSTALL_DIR/$MAIN_SCRIPT_NAME"
else
    TARGET_SCRIPT="$INSTALL_DIR/nossis_screenshotter.py"
fi

cat > "$WRAPPER_DIR/autoscreen" << EOF
#!/usr/bin/env bash
# AutoScreen v7.1 — wrapper global
# Gerado automaticamente por install.sh
exec $PY $TARGET_SCRIPT "\$@"
EOF

chmod 755 "$WRAPPER_DIR/autoscreen"
ok "Comando criado → $WRAPPER_DIR/autoscreen"

# Adiciona ao PATH se for instalação local e não estiver no PATH
if [ "$GLOBAL_INSTALL" = false ]; then
    if [[ ":$PATH:" != *":$WRAPPER_DIR:"* ]]; then
        warn "$WRAPPER_DIR não está no PATH"
        info "Adicione ao ~/.bashrc ou ~/.zshrc:"
        echo ""
        echo -e "    ${CYAN}export PATH=\"\$PATH:$WRAPPER_DIR\"${RESET}"
        echo ""
    fi
fi

# ── 8. Validação final ─────────────────────────────────────────────
step "8. Validando instalação..."

ERRORS=0

$PY -c "import sys; assert sys.version_info >= (3,8)" 2>/dev/null \
    && ok "Python 3.8+" || { warn "Python < 3.8"; ERRORS=$((ERRORS+1)); }

$PY -c "from playwright.sync_api import sync_playwright; print('ok')" 2>/dev/null \
    | grep -q ok && ok "playwright" || { warn "playwright não importável"; ERRORS=$((ERRORS+1)); }

$PY -c "from PIL import Image; print('ok')" 2>/dev/null \
    | grep -q ok && ok "Pillow (PIL)" || { warn "Pillow não disponível — PDF sem imagens"; ERRORS=$((ERRORS+1)); }

$PY -c "from rich.console import Console; print('ok')" 2>/dev/null \
    | grep -q ok && ok "rich" || { warn "rich não disponível — modo texto simples"; }

$PY -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    b.close()
    print('ok')
" 2>/dev/null | grep -q ok && ok "Chromium funcional" \
    || { warn "Chromium não abre — verifique dependências do sistema"; ERRORS=$((ERRORS+1)); }

$PY -c "
from PIL import ImageFont
try:
    ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', 12)
    print('ok')
except:
    print('fallback')
" 2>/dev/null | grep -q ok && ok "Liberation Sans (ABNT)" \
    || warn "Liberation Sans não encontrada — PDF usará DejaVu Sans"

[ -f "$TARGET_SCRIPT" ] && ok "Script principal: $TARGET_SCRIPT" \
    || warn "Script principal não encontrado em $TARGET_SCRIPT"

[ -x "$WRAPPER_DIR/autoscreen" ] && ok "Comando 'autoscreen' disponível" \
    || warn "Wrapper não criado em $WRAPPER_DIR/autoscreen"

# ── Resultado ──────────────────────────────────────────────────────
echo ""
echo "  ──────────────────────────────────────────────"

if [ "$ERRORS" -eq 0 ]; then
    echo -e "  ${GREEN}${BOLD}✓ Instalação concluída com sucesso!${RESET}"
    echo ""
    echo -e "  ${BOLD}Como usar (qualquer usuário do sistema):${RESET}"
    echo -e "    ${CYAN}autoscreen${RESET}              # menu interativo"
    echo -e "    ${CYAN}autoscreen hml${RESET}           # executa direto HML"
    echo -e "    ${CYAN}autoscreen hml netwin${RESET}    # sistema + módulo direto"
    echo -e "    ${CYAN}autoscreen --all-envs${RESET}    # todos os ambientes"
    echo -e "    ${CYAN}autoscreen --help${RESET}        # todas as opções"
    echo ""
    echo -e "  ${BOLD}Instalação:${RESET}"
    echo -e "    Script  : ${CYAN}$TARGET_SCRIPT${RESET}"
    echo -e "    Comando : ${CYAN}$WRAPPER_DIR/autoscreen${RESET}"
    echo -e "    Logs    : ${CYAN}$INSTALL_DIR/logs/${RESET}"
    echo -e "    Sessões : ${CYAN}$INSTALL_DIR/.nossis_sessions/${RESET}"
    echo ""
    if [ "$GLOBAL_INSTALL" = true ]; then
        echo -e "  ${BOLD}Nota:${RESET} Outros usuários precisam rodar Playwright Chromium uma vez:"
        echo -e "    ${CYAN}python3 -m playwright install chromium${RESET}"
    fi
else
    echo -e "  ${YELLOW}${BOLD}⚠ Instalação concluída com $ERRORS erro(s).${RESET}"
    echo -e "  Verifique os itens marcados com ⚠ acima antes de usar."
fi

echo ""
