# 📸 NOSSIS ONE INVENTORY — Screenshot Automático

> Ferramenta de automação para captura de evidências do Portal NOSSIS ONE INVENTORY via Playwright.  
> Faz login no IAM, navega por todas as opções de menu e gera relatório HTML/PDF completo.

---

## 🚀 Funcionalidades

| Feature | Descrição |
|---|---|
| 🔐 Login IAM multi-step | Autenticação automática no IAM com suporte a múltiplos ambientes |
| 💾 Sessão persistente | Reutiliza cookies por até 8h, evitando login repetido |
| 🔌 Validação de VPN | Verifica conectividade antes de iniciar — detecta VPN desconectada |
| 🗺️ Mapeamento de menu | Coleta todos os links do portal incluindo submenus expandidos via hover |
| 📸 Screenshots full-page | Captura a página inteira com watermark de data/hora |
| 🔄 Retry automático | Tenta novamente em caso de falha (configurável) |
| ✅ Validação pós-capture | Detecta páginas brancas, redirects e erros HTTP 4xx/5xx |
| 📊 Relatório HTML/PDF | Relatório completo com capa, tabela resumo e grid de evidências |
| 🔍 Comparação visual | Compara screenshots entre duas execuções e detecta diferenças |
| 📝 README.txt | Gerado automaticamente na pasta de saída |
| 📋 Logs detalhados | Log completo em `logs/nossis_<env>_<timestamp>.log` |

---

## 📋 Pré-requisitos

```bash
pip3 install playwright rich Pillow numpy weasyprint
python3 -m playwright install chromium
```

| Pacote | Obrigatório | Função |
|---|---|---|
| `playwright` | ✅ | Automação do browser |
| `rich` | ⚡ Recomendado | Menu e output colorido |
| `Pillow` | ⚡ Recomendado | Watermark nos screenshots |
| `numpy` | ⚡ Recomendado | Comparação visual |
| `weasyprint` | ⚡ Recomendado | Geração de PDF |

---

## ⚙️ Configuração de Ambientes

Edite o dicionário `ENVIRONMENTS` no início do script:

```python
ENVIRONMENTS = {
    "int": {
        "name":       "INT — Dev (V.Tal)",
        "iam_url":    "https://iam-dev-vtal.../idp/login",
        "portal_url": "https://netwin-dev-vtal.../portal",
        "username":   "netwin",
        "password":   "netwin",
    },
    "hml": {
        "name":       "HML — Dev (OCP Arc)",
        "iam_url":    "https://iam-nossis-dev.../idp/login",
        "portal_url": "https://netwin-nossis-dev.../portal",
        "username":   "netwin",
        "password":   "Netwin123456!!",
    },
    # Adicione novos ambientes aqui...
}
```

---

## 🖥️ Uso

### Menu interativo
```bash
python3 nossis_screenshotter.py
```

### Ambiente direto
```bash
python3 nossis_screenshotter.py int
python3 nossis_screenshotter.py hml
```

### Opções disponíveis

| Opção | Descrição | Exemplo |
|---|---|---|
| `--dry-run` | Lista páginas sem capturar | `python3 nossis_screenshotter.py int --dry-run` |
| `--page` | Captura página(s) específica(s) | `python3 nossis_screenshotter.py int --page OSP` |
| `--page` múltiplo | Vírgula para separar | `python3 nossis_screenshotter.py int --page "OSP,ISP"` |
| `--retries` | Tentativas em caso de falha | `python3 nossis_screenshotter.py int --retries 3` |
| `--all-envs` | Executa todos os ambientes | `python3 nossis_screenshotter.py --all-envs` |
| `--since` | Só páginas que mudaram | `python3 nossis_screenshotter.py int --since nossis_prints_int_1.0.7` |
| `--no-session` | Ignora sessão salva | `python3 nossis_screenshotter.py int --no-session` |
| `--compare` | Compara duas execuções | `python3 nossis_screenshotter.py --compare dir1 dir2` |

---

## 📁 Estrutura de Saída

```
nossis_prints_int_1.0.7-r1-r2/
├── 00_sobre.png              ← Modal Sobre com versão do sistema
├── 01_Locais.png             ← Screenshots de cada página do menu
├── 02_OSP.png
├── ...
├── PARCIAL_*.png             ← Screenshots parciais em caso de erro
├── debug_*.png               ← Debug do fluxo de login
├── relatorio_YYYYMMDD.html   ← Relatório completo com evidências
├── relatorio_YYYYMMDD.pdf    ← Relatório em PDF
└── README.txt                ← Resumo da execução

logs/
└── nossis_int_YYYYMMDD_HHMMSS.log

.nossis_sessions/             ← Sessões salvas (não commitar!)
└── session_int.json

comparacoes/                  ← Relatórios de comparação visual
└── comparacao_YYYYMMDD.html
```

---

## 📊 Relatório de Evidências

O relatório HTML gerado contém:

- **Capa** — ambiente, versão, data, duração, estatísticas OK/Aviso/Erro
- **Tabela resumo** — todas as páginas com status e tempo de captura
- **Evidências** — 2 capturas por página com lightbox ao clicar
- **Numeração de páginas** — no rodapé de cada página
- **Badges coloridos** — ✓ OK | ⚠ Aviso | ✗ Erro

---

## 🔍 Comparação Visual

```bash
# Compara screenshots entre duas versões
python3 nossis_screenshotter.py --compare \
    nossis_prints_int_1.0.6 \
    nossis_prints_int_1.0.7

# Gera relatório em comparacoes/comparacao_YYYYMMDD.html
```

---

## 🛠️ Configurações Avançadas

No início do script:

```python
TIMEOUT    = 120_000   # Timeout geral em ms
WAIT_UNTIL = "load"    # Estratégia de espera

# Páginas a ignorar
SKIP_LABELS = ["outros módulos"]
SKIP_URLS   = ["/portal#"]

# Tempo extra para páginas lentas
EXTRA_WAIT = {
    "OSP":         8_000,   # +8s após spinner
    "Viabilidade": 10_000,  # +10s após spinner
}
```

---

## 📦 Dependências de Sistema

```bash
# Ubuntu/Debian (WSL)
sudo apt install fonts-dejavu  # Para watermark com fonte monospace
```

---

## 📝 Changelog

| Versão | Novidades |
|---|---|
| **v6.0** | Sessão persistente, submenus via hover, erros HTTP, README.txt, `--all-envs`, `--since` |
| **v5.0** | Retry automático, screenshot parcial, validação pós-capture, relatório HTML/PDF, `--dry-run`, `--page`, `--compare` |
| **v4.0** | Menu Rich interativo, multi-ambiente, logs, versão no nome da pasta, barra de progresso |
| **v3.0** | CLI multi-ambiente, pasta separada por ambiente |
| **v2.0** | Login IAM multi-step, card NETWIN, modal Sobre, spinner, watermark |

---

## 👤 Autor

**Diego Santos**  
📧 diego-f-santos@openlabs.com.br  

---

## ⚠️ Observações de Segurança

- O arquivo `.nossis_sessions/` contém cookies de autenticação — **nunca commitar**
- As senhas estão no código — use variáveis de ambiente em produção:
```python
import os
"password": os.environ.get("NOSSIS_PASS_INT", "netwin")
```
