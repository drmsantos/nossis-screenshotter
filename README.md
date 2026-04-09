# AutoScreen v7.1

> Ferramenta de automação para captura de evidências de portais NOSSIS ONE INVENTORY via Playwright.
> Faz login no IAM, navega por todas as opções de menu e gera relatório completo em HTML e PDF.

**Autor:** Diego Regis M. F. dos Santos  
**Email:** diego-f-santos@openlabs.com.br  
**Time:** OpenLabs — DevOps | Infra

---

## Funcionalidades

| Feature | Descrição |
|---|---|
| 🔐 Login IAM multi-step | Autenticação automática no IAM com múltiplos ambientes e módulos |
| 💾 Sessão persistente | Reutiliza cookies por 30 min — renova login automaticamente ao expirar |
| 🔌 Validação de VPN | Verifica conectividade (TCP) antes de iniciar — detecta VPN desconectada |
| 🗺️ Mapeamento de menu | Coleta todos os links via JavaScript direto no DOM — sem hover, instantâneo |
| 📸 Screenshots full-page | Captura a página inteira com watermark de data/hora |
| ⚡ Multi-thread automático | Escala threads pelo volume: `< 10 pág → 1` / `10–29 → 2` / `≥ 30 → 3` threads |
| 📊 Barras de progresso | Barra por thread em tempo real com cores distintas (ciano, magenta, amarelo) |
| 🔄 Retry com backoff | Retenta automaticamente com espera progressiva (1s, 2s, 3s…) |
| ✅ Validação dupla | Camada DOM (spinner, URL, conteúdo) + Camada imagem (variância, % branco) |
| ✗ Status NOK | Página que não carrega após todos os retries é marcada como NOK em vermelho |
| 📄 PDF ABNT NBR 14724 | Gerado via Pillow — margens, fonte Liberation Sans, entrelinhas, numeração |
| 📊 Relatório HTML | Capa, tabela resumo e evidências com 2 capturas por página |
| 🔍 Comparação visual | Compara screenshots entre duas execuções e detecta diferenças |
| 📝 README.txt | Gerado automaticamente na pasta de saída de cada execução |
| 📋 Logs detalhados | Log completo em `logs/nossis_<env>_<timestamp>.log` |

---

## Pré-requisitos

```bash
# Dependências Python
pip3 install playwright Pillow rich

# Browser headless
python3 -m playwright install chromium

# Dependências de sistema (Linux)
python3 -m playwright install-deps chromium

# Fonte ABNT para o PDF
sudo apt install fonts-liberation       # Ubuntu/Debian
sudo yum install liberation-fonts       # RHEL/CentOS
sudo dnf install liberation-fonts       # Fedora/RHEL 8+
```

| Pacote | Obrigatório | Função |
|---|---|---|
| `playwright` | ✅ | Automação do browser Chromium |
| `Pillow` | ✅ | Watermark, validação de imagem e geração do PDF |
| `rich` | ⚡ Recomendado | Menu interativo, barras de progresso e output colorido |
| `numpy` | Opcional | Comparação visual entre execuções (`--compare`) |

---

## Instalação

### Global (todos os usuários)

```bash
# 1. Clone ou copie os arquivos para uma pasta temporária
mkdir /tmp/autoscreen && cd /tmp/autoscreen
# Coloque aqui: nossis_screenshotter.py e install.sh

# 2. Instale com sudo
chmod +x install.sh
sudo ./install.sh

# 3. Cada usuário precisa rodar isso UMA VEZ (Playwright por usuário)
python3 -m playwright install chromium

# 4. Pronto — use de qualquer lugar
autoscreen
```

O `install.sh` faz automaticamente:
- Instala dependências Python (`playwright`, `Pillow`, `rich`)
- Instala Chromium via Playwright
- Instala fontes Liberation Sans
- Copia o script para `/opt/autoscreen/`
- Cria o wrapper `/usr/local/bin/autoscreen`
- Cria as pastas `logs/` e `.nossis_sessions/` com permissão para todos os usuários

### Local (sem sudo)

```bash
./install.sh
# Quando perguntado, responda "s" para instalar em ~/autoscreen
# Adicione ~/.local/bin ao PATH se necessário:
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.zshrc
source ~/.zshrc
```

### Estrutura instalada

```
/opt/autoscreen/
├── nossis_screenshotter.py     ← script principal
├── install.sh                  ← instalador (referência)
├── logs/                       ← logs de execução (777 — todos escrevem)
└── .nossis_sessions/           ← sessões salvas (777 — todos escrevem)

/usr/local/bin/autoscreen       ← wrapper global
```

---

## Configuração de Ambientes

Edite o dicionário `SYSTEMS` no início do script:

```python
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
                "module":      "NETWIN",    # texto do card no IAM (<h4>NETWIN</h4>)
                "inicio_link": "/portal",   # link clicado após entrar no módulo
            },
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
            # "sigo": { ... },
            # "alarmmgr": { ... },
        },
    },
}
```

### Adicionando um novo módulo

```python
# No sistema "hml", descomentar ou adicionar:
"alarmmgr": {
    "name":        "ALARMMGR",
    "portal_url":  "https://alarmmgr-nossis-dev.apps.ocparc-nprd.vtal.intra/",
    "module":      "ALARMMGR",   # texto exato do <h4> no card do IAM
    "inicio_link": "/",
},
```

### Adicionando um novo sistema/ambiente

```python
SYSTEMS["prd"] = {
    "name":     "PRD — Produção",
    "iam_url":  "https://iam-prd.vtal.intra/idp/login",
    "username": "netwin",
    "password": "senha_prd",
    "modules": {
        "netwin": {
            "name":        "NETWIN",
            "portal_url":  "https://netwin-prd.vtal.intra/portal",
            "module":      "NETWIN",
            "inicio_link": "/portal",
        },
    },
}
```

---

## Uso

### Menu interativo (recomendado)

```bash
autoscreen
# ou
python3 nossis_screenshotter.py
```

O menu apresenta primeiro os sistemas disponíveis, depois os módulos:

```
┌────┬──────┬──────────────────────────┐
│ #  │ Chave│ Sistema                  │
├────┼──────┼──────────────────────────┤
│ 1  │ INT  │ INT — Dev (V.Tal)        │
│ 2  │ HML  │ HML — Dev (OCP Arc)      │
└────┴──────┴──────────────────────────┘

┌────┬──────────┬──────────┬─────────────────────┐
│ #  │ Módulo   │ Nome     │ Portal               │
├────┼──────────┼──────────┼─────────────────────┤
│ 1  │ NETWIN   │ NETWIN   │ netwin-nossis-dev... │
├────┼──────────┼──────────┼─────────────────────┤
│ 0  │ TODOS    │ Capturar todos os módulos        │
└────┴──────────┴──────────┴─────────────────────┘
```

### Linha de comando

```bash
autoscreen hml                  # primeiro módulo do sistema HML
autoscreen hml netwin           # sistema + módulo direto
autoscreen int                  # sistema INT
autoscreen hml-netwin           # formato alternativo sistema-módulo
autoscreen --all-envs           # todos os sistemas e módulos
```

### Opções disponíveis

| Opção | Descrição | Exemplo |
|---|---|---|
| _(sem argumentos)_ | Menu interativo | `autoscreen` |
| `<sistema>` | Executa o primeiro módulo do sistema | `autoscreen hml` |
| `<sistema> <módulo>` | Sistema + módulo direto | `autoscreen hml netwin` |
| `--dry-run` | Lista páginas sem capturar | `autoscreen hml --dry-run` |
| `--page <nome>` | Captura página(s) específica(s) | `autoscreen hml --page OSP` |
| `--page` múltiplo | Separar com vírgula | `autoscreen hml --page "OSP,ISP,S&R"` |
| `--retries <N>` | Tentativas em caso de falha (padrão: 2) | `autoscreen hml --retries 3` |
| `--all-envs` | Todos os sistemas e módulos | `autoscreen --all-envs` |
| `--since <pasta>` | Só páginas que mudaram | `autoscreen hml --since nossis_prints_hml_1.0.7` |
| `--no-session` | Ignora sessão salva e faz login do zero | `autoscreen hml --no-session` |
| `--compare <d1> <d2>` | Compara duas execuções | `autoscreen --compare dir1 dir2` |

---

## Estrutura de Saída

```
nossis_prints_hml_1.0.7-r2_20260408_151829/
├── 00_sobre.png                    ← modal Sobre com versão do sistema
├── 01_Início.png
├── 02_LOCAIS.png
├── 03_Locais_físicos.png
├── ...                             ← screenshot de cada página do menu
├── relatorio_20260408_151829.html  ← relatório HTML com evidências
├── relatorio_20260408_151829.pdf   ← relatório PDF (ABNT NBR 14724)
└── README.txt                      ← resumo da execução

logs/
└── nossis_hml_20260408_151350.log

.nossis_sessions/                   ← ⚠ não commitar — contém cookies
└── session_hml-netwin.json

comparacoes/                        ← gerado pelo --compare
└── comparacao_20260408.html
```

---

## Relatório PDF

O PDF é gerado via **Pillow** (sem weasyprint) seguindo o padrão **ABNT NBR 14724**:

| Elemento | Valor |
|---|---|
| Margem superior | 3 cm |
| Margem inferior | 2 cm |
| Margem esquerda | 3 cm |
| Margem direita | 2 cm |
| Fonte | Liberation Sans 12pt |
| Entrelinhas | 1,5x |
| Numeração | Canto superior direito (sec. 5.3) |
| Tamanho | A4 |

Estrutura do PDF:
- **Página 1 — Capa:** ambiente, versão, data, duração, estatísticas OK/Aviso/Erro
- **Página 2 — Resumo:** tabela com todas as páginas, status e tempo de captura
- **Páginas seguintes — Evidências:** 2 capturas por página com header colorido e status

---

## Configurações Avançadas

No início do script, antes da seção `SYSTEMS`:

```python
TIMEOUT     = 60_000             # Timeout geral em ms (60s)
WAIT_UNTIL  = "domcontentloaded" # Estratégia de espera do Playwright
MAX_RETRIES = 2                  # Tentativas em caso de falha
SESSION_TTL = 30 * 60            # Sessão válida por 30 minutos

# Páginas a ignorar (por label)
SKIP_LABELS = ["outros módulos", "segurança", "Funções assurance"]

# URLs a ignorar
SKIP_URLS   = ["/portal#", "/portal/home"]

# Tempo extra de espera por página (em ms)
EXTRA_WAIT = {
    "OSP":                      10_000,   # +10s
    "Viabilidade":              12_000,   # +12s
    "GISMaps":                   8_000,   # +8s
    "Templates de equipamentos": 8_000,   # +8s
    "Armazém":                   8_000,   # +8s
    "Reserva":                   8_000,   # +8s
    "ISP":                       5_000,   # +5s
    # ... demais páginas com +5s
}

# Recursos bloqueados para economizar banda
BLOCKED_RESOURCES = ["media"]    # vídeos bloqueados; fontes liberadas (necessárias para ícones)
```

---

## Validação de Screenshots

O AutoScreen valida cada captura em duas camadas antes de marcar como OK:

**Camada 1 — DOM (via Playwright):**
- URL redirecionada para login/erro
- Título da página com 404, 403 ou "error"
- Spinner visível por texto (`"A carregar página"`, `"Loading"`, etc.)
- Spinner visível por classe CSS (`.spinner`, `.loader`)
- `aria-busy=true` ativo na página
- Conteúdo mínimo no body (menos de 50 chars)

**Camada 2 — Imagem (via Pillow):**
- Arquivo menor que 15KB → provavelmente página branca
- Variância geral menor que 3 → imagem quase sólida
- Mais de 97% de pixels brancos → não renderizou

Se qualquer verificação falhar → retry automático com backoff progressivo.  
Se esgotar os retries → marca como **NOK** (vermelho) no relatório.

---

## Sessão e Login

- A sessão é salva em `.nossis_sessions/session_<env>.json`
- Válida por **30 minutos** — renova automaticamente ao expirar
- Em execução paralela (multi-thread), se a sessão expirar durante a captura, a thread detecta o redirect para o IAM e navega de volta ao portal automaticamente
- Para forçar novo login: `autoscreen hml --no-session`

---

## Comparação Visual

```bash
# Compara screenshots entre duas versões
autoscreen --compare \
    nossis_prints_hml_1.0.6 \
    nossis_prints_hml_1.0.7

# Gera relatório em comparacoes/comparacao_YYYYMMDD.html
# Requer: pip3 install numpy
```

---

## Segurança

- `.nossis_sessions/` contém cookies de autenticação — **nunca commitar**
- As senhas estão no script — para ambientes sensíveis, use variáveis de ambiente:

```python
import os
"password": os.environ.get("AUTOSCREEN_PASS_HML", "Netwin123456!!")
```

Adicione `.nossis_sessions/` ao `.gitignore`:

```
.nossis_sessions/
nossis_prints_*/
logs/
```

---

## Changelog

| Versão | Novidades |
|---|---|
| **v7.1** | Multi-thread automático por volume; barras de progresso por thread; sessão TTL 30min com renovação automática; PDF via Pillow com ABNT NBR 14724; validação dupla DOM+imagem; status NOK; retry com backoff; bloqueio de recursos; 12 flags de performance no browser; `WAIT_UNTIL=domcontentloaded`; detecção de versão com 3 níveis de fallback; menu dois passos sistema→módulo; mapeamento de menu via JS (sem hover) |
| **v6.0** | Sessão/cookies persistente; detecção de submenus por hover; log embutido no HTML; README.txt na pasta de saída; `--all-envs`; `--since` |
| **v5.0** | Retry automático `--retries`; screenshot parcial em erro; validação pós-screenshot; relatório HTML com grid e badges; `--dry-run`; `--page`; comparação visual `--compare` |
| **v4.0** | Menu Rich interativo; multi-ambiente; pasta com versão do modal Sobre; logging completo; barra de progresso |
| **v3.0** | Multi-ambiente via CLI ou menu; pasta separada por ambiente |
| **v2.0** | Login IAM multi-step; card NETWIN; modal Sobre como primeiro print; spinner; watermark; tempo extra por página |

---

## Arquivos do Projeto

| Arquivo | Descrição |
|---|---|
| `nossis_screenshotter.py` | Script principal |
| `install.sh` | Instalador automático |
| `README.md` | Esta documentação |