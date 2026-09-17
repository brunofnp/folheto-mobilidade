"""
Tema MOBILIDADE — Ficha de Diagnóstico Preliminar de Segurança Viária.

Público-alvo do folheto: cidades acima de 80 mil habitantes. Conteúdo
derivado do documento de briefing do projeto (mortes, internações, custo
hospitalar, ranking de causas de morte, evolução da frota).

Estado desta primeira versão (ver CLAUDE.md "Pendências"):
  - Frota, mortalidade e série histórica de mortes: implementadas — os dados
    de mortes já foram tratados em R pela equipe (ver notas do projeto).
  - Internações: página implementada, mas o schema aceita valores `None`
    porque a coleta de dados de internação ainda está em andamento.
  - Custo por hospital e mapa de internações por bairro: NÃO implementados
    ainda — dependem de dado que ainda não existe (ver SCHEMA.md).

Contrato de dados completo: data/mobilidade/SCHEMA.md.
"""
import sys

from core.base_folheto import FolhetoFNP
from core.components import (
    draw_stripe, draw_page_number, draw_header, draw_footer,
    draw_eyebrow, draw_titulo, draw_body, draw_caption,
    draw_kpi_box, draw_destaque_box, draw_table, draw_ranking_item,
    draw_section_divider, draw_qr_page, draw_capa_padrao, draw_line_chart,
)
from core.tokens import (
    MARGIN, STRIPE_W, CONTENT_W, ASSETS_DIR,
    BLUE, BLUE_DARK, RED_BURNT, GREEN,
    FS_TITLE_SECAO,
)


def _fmt_taxa(v) -> str:
    """Taxa por 100 mil habitantes. `None` vira 'n/d' — nunca um traço solto
    (ver DESIGN_SYSTEM.md: travessão é proibido e confunde com sinal de menos)."""
    if v is None:
        return "n/d"
    return f"{v:,.1f}".replace(",", "@").replace(".", ",").replace("@", ".")


def _fmt_pct(v) -> str:
    if v is None:
        return "n/d"
    sinal = "+" if v >= 0 else ""
    return f"{sinal}{v:,.1f}%".replace(".", ",")


class FolhetoMobilidade(FolhetoFNP):
    titulo_publicacao = "SEGURANÇA VIÁRIA · DIAGNÓSTICO PRELIMINAR FNP"

    # PLACEHOLDER — não confirmado que esta URL existe/resolve. Nunca enviar
    # para impressão sem sobrescrever via campo "url" no JSON (ver SCHEMA.md)
    # com um endereço real e testado. Ver CLAUDE.md, seção Pendências.
    URL_PADRAO = "https://fnp.org.br/mobilidade"

    def construir_paginas(self):
        paginas = [
            self._pag_capa,
            self._pag_problema,
            self._pag_divisor_mortes,
            self._pag_mortalidade_2024,
            self._pag_serie_mortes,
            self._pag_divisor_internacoes,
            self._pag_internacoes,
            self._pag_serie_internacoes,
            self._pag_causas_morte,
            self._pag_metodologia,
            self._pag_encerramento,
        ]
        return paginas

    # ─── Helpers de conteúdo/ausência de dado ────────────────────────────────

    def _output_name(self):
        return self.d.get("nome", "folheto"), self.d.get("uf", "")

    def _avisar_se_ausente(self, chave: str, secao: str):
        if not self.d.get(chave):
            print(f"[aviso] '{chave}' ausente nos dados; a seção '{secao}' sairá "
                  f"incompleta ou vazia.", file=sys.stderr)

    def _topo_pagina(self, c, n, lado, label_secao, eyebrow, titulo, titulo_size=FS_TITLE_SECAO):
        """Fundo + stripe + numeração + header + eyebrow/título + footer.
        Retorna (x_conteudo, y_abaixo_titulo) prontos para o corpo da página."""
        from core.tokens import PAPER
        c.setFillColor(PAPER)
        c.rect(0, 0, self.W, self.H, fill=1, stroke=0)

        draw_stripe(c, self.W, self.H, lado)
        draw_page_number(c, self.W, n, lado)
        draw_header(c, self.H, self.titulo_publicacao)
        draw_footer(c, self.W, label_secao)

        x = STRIPE_W + MARGIN if lado == "esq" else MARGIN
        y = self.H - 56
        draw_eyebrow(c, eyebrow, x, y)
        # Gap entre a baseline do eyebrow e a do título precisa acompanhar o
        # tamanho do título: um título de 30pt tem ascendentes que
        # ultrapassam um gap fixo pequeno e encostam no eyebrow (bug real,
        # visível sobretudo em letras com acento como "Ó").
        titulo_y = y - titulo_size * 1.05
        draw_titulo(c, titulo, x, titulo_y, size=titulo_size)
        y_corpo = titulo_y - titulo_size * 0.95 * titulo.count("\n") - 26
        return x, y_corpo

    # ─── Página 1: Capa ───────────────────────────────────────────────────────

    def _pag_capa(self, c, n):
        nome = self.d.get("nome", "Município")
        uf = self.d.get("uf", "")
        draw_capa_padrao(
            c, self.W, self.H,
            titulo_capa="SEGURANÇA\nVIÁRIA",
            subtitulo=f"Ficha de diagnóstico preliminar · {nome}/{uf}" if uf else
                      f"Ficha de diagnóstico preliminar · {nome}",
            foto_path=self.d.get("_capa_foto"),   # opcional, ver SCHEMA.md
            logo_path=str(ASSETS_DIR / "logos" / "fnp-logo.png"),
            lado="dir",
        )

    # ─── Página 2: Apresentação / "O problema" ───────────────────────────────

    def _pag_problema(self, c, n):
        self._avisar_se_ausente("problema", "Apresentação do tema")
        x, y = self._topo_pagina(
            c, n, "dir", "O PROBLEMA", "SEGURANÇA VIÁRIA",
            "Por que isso\nimporta para a cidade",
        )
        problema = self.d.get("problema") or {}
        citacao = problema.get(
            "citacao",
            "Cada sinistro de trânsito custa vidas, leitos hospitalares e "
            "recursos que a cidade poderia empregar em outras prioridades "
            "de saúde pública.",
        )
        draw_destaque_box(c, "DESTAQUE", citacao, x, y - 70, CONTENT_W, h=90, font_size=15)
        y -= 180

        pop = (self.d.get("populacao") or {}).get("valor")
        frota = self.d.get("frota") or {}
        frota_atual = (frota.get("atual") or {}).get("total")
        cresc_frota = (frota.get("evolucao_pct") or {}).get("2003_2025", {}).get("total")
        mortes_serie = self.d.get("mortes_serie_historica") or {}
        anos_m = mortes_serie.get("anos") or []
        totais_m = mortes_serie.get("total") or []
        mortes_ultimo_ano = totais_m[-1] if totais_m else None

        cards = [
            ("População", f"{pop:,}".replace(",", ".") if pop else "n/d", "hab."),
            ("Frota atual", f"{frota_atual:,}".replace(",", ".") if frota_atual else "n/d", "veículos"),
            ("Cresc. da frota · 2003–2025", _fmt_pct(cresc_frota), ""),
            ("Mortes no trânsito", f"{mortes_ultimo_ano:,.0f}".replace(",", ".") if mortes_ultimo_ano is not None else "n/d",
             str(anos_m[-1]) if anos_m else ""),
        ]
        # Grid 2×2 (não 1×4): com só ~4 caracteres de sobra por card numa
        # fileira de 4, tanto o rótulo quanto valor+unidade estouram a
        # largura (ver CLAUDE.md/lição do draw_kpi_box). 2×2 dobra a largura
        # útil de cada card.
        card_w = (CONTENT_W - 12) / 2
        card_h = 64
        gap_v = 12
        for i, (label, valor, unidade) in enumerate(cards):
            col, row = i % 2, i // 2
            cx = x + col * (card_w + 12)
            cy = y - 58 - row * (card_h + gap_v)
            draw_kpi_box(c, label, valor, unidade, cx, cy, w=card_w, h=card_h)

    # ─── Página 3: Divisória "Mortes no trânsito" ────────────────────────────

    def _pag_divisor_mortes(self, c, n):
        draw_section_divider(
            c, self.W, self.H,
            capitulo="CAPÍTULO 01",
            titulo="MORTES NO\nTRÂNSITO",
            subtitulo="Comparação de taxas de mortalidade e série histórica por modo",
            n_pagina=n, lado="esq",
        )

    # ─── Página 4: Tabela comparativa de mortalidade 2024 ────────────────────

    def _pag_mortalidade_2024(self, c, n):
        self._avisar_se_ausente("mortalidade_2024", "Taxa de mortalidade 2024")
        x, y = self._topo_pagina(
            c, n, "dir", "MORTES NO TRÂNSITO", "TAXA DE MORTALIDADE",
            "Óbitos por 100 mil hab. · 2024",
        )
        draw_body(
            c,
            "Comparação da taxa de mortalidade do município com o recorte "
            "metropolitano, cidades de mesmo porte, o estado, o Brasil e as "
            "capitais. Fonte: SIM/DATASUS. Elaboração: FNP.",
            x, y, CONTENT_W, size=9,
        )
        y -= 30

        dados = self.d.get("mortalidade_2024") or {}
        linhas_labels = [
            ("total", "Total"),
            ("motociclistas", "Motociclistas"),
            ("pedestres", "Pedestres"),
            ("ciclistas", "Ciclistas"),
        ]
        # Rótulos curtos de propósito: "MESMO PORTE" não cabe numa coluna
        # estreita sem invadir a coluna vizinha (draw_table alinha à
        # direita, sem clip — texto largo demais transborda pra esquerda).
        headers = ["MODO", "MUNICÍPIO", "RM", "PORTE", "ESTADO", "BRASIL", "CAPITAIS"]
        col_w = [CONTENT_W * w for w in (0.17, 0.15, 0.13, 0.14, 0.14, 0.14, 0.13)]
        rows = []
        for chave, label in linhas_labels:
            linha = dados.get(chave) or {}
            rows.append([
                label,
                _fmt_taxa(linha.get("municipio")),
                _fmt_taxa(linha.get("rm")),
                _fmt_taxa(linha.get("porte")),
                _fmt_taxa(linha.get("estado")),
                _fmt_taxa(linha.get("brasil")),
                _fmt_taxa(linha.get("capitais")),
            ])
        draw_table(c, headers, rows, col_w, x, y, highlight_col=1)
        y -= len(rows) * 18 + 26
        draw_caption(c, "Leitura: quanto menor a taxa, melhor a posição do município.", x, y)

    # ─── Página 5: Série histórica de mortes 2010-2024 ───────────────────────

    def _pag_serie_mortes(self, c, n):
        self._avisar_se_ausente("mortes_serie_historica", "Série histórica de mortes")
        x, y = self._topo_pagina(
            c, n, "esq", "MORTES NO TRÂNSITO", "EVOLUÇÃO DAS MORTES",
            "Série histórica por modo · 2010–2024",
        )
        serie = self.d.get("mortes_serie_historica") or {}
        anos = serie.get("anos") or []
        if anos:
            series = [
                {"nome": "Total", "valores": serie.get("total"), "cor": BLUE_DARK},
                {"nome": "Motociclistas", "valores": serie.get("motociclistas"), "cor": RED_BURNT},
                {"nome": "Pedestres", "valores": serie.get("pedestres"), "cor": BLUE},
                {"nome": "Ciclistas", "valores": serie.get("ciclistas"), "cor": GREEN},
            ]
            series = [s for s in series if s["valores"]]
            y = draw_line_chart(
                c, series=series, categorias=anos,
                x=x, y=y, w=CONTENT_W, h=280,
            )
            y -= 14
            draw_caption(c, "Fonte: SIM/DATASUS, tratamento próprio. Elaboração: FNP.", x, y)
        else:
            draw_body(c, "Série histórica ainda não disponível para este município.",
                      x, y - 20, CONTENT_W)

    # ─── Página 6: Divisória "Internações e custos" ──────────────────────────

    def _pag_divisor_internacoes(self, c, n):
        draw_section_divider(
            c, self.W, self.H,
            capitulo="CAPÍTULO 02",
            titulo="INTERNAÇÕES\nE CUSTOS",
            subtitulo="Feridos em sinistros de trânsito e o peso no sistema de saúde",
            n_pagina=n, lado="dir",
        )

    # ─── Página 7: Tabela comparativa de internações ─────────────────────────

    def _pag_internacoes(self, c, n):
        self._avisar_se_ausente("internacoes_2025", "Internações por sinistro")
        x, y = self._topo_pagina(
            c, n, "esq", "INTERNAÇÕES E CUSTOS", "INTERNAÇÕES POR SINISTRO",
            "SIH/SIA · dados sujeitos a revisão",
        )
        draw_body(
            c,
            "Internações por sinistro de trânsito, por modo. Coleta em "
            "andamento: valores em branco (\"n/d\") serão preenchidos "
            "conforme os dados forem consolidados.",
            x, y, CONTENT_W, size=9,
        )
        y -= 30

        dados = self.d.get("internacoes_2025") or {}
        linhas_labels = [
            ("total", "Total"),
            ("motociclistas", "Motociclistas"),
            ("pedestres", "Pedestres"),
            ("ciclistas", "Ciclistas"),
        ]
        headers = ["MODO", "MUNICÍPIO", "PORTE", "ESTADO", "BRASIL"]
        col_w = [CONTENT_W * w for w in (0.28, 0.18, 0.20, 0.17, 0.17)]
        rows = []
        for chave, label in linhas_labels:
            linha = dados.get(chave) or {}
            rows.append([
                label,
                _fmt_taxa(linha.get("municipio")),
                _fmt_taxa(linha.get("porte")),
                _fmt_taxa(linha.get("estado")),
                _fmt_taxa(linha.get("brasil")),
            ])
        draw_table(c, headers, rows, col_w, x, y, highlight_col=1)
        y -= len(rows) * 18 + 26
        draw_caption(c, "Fonte: SIH/SIA · DATASUS. Elaboração: FNP.", x, y)

    # ─── Página 8: Série histórica de internações (hachura gestão atual) ─────

    def _pag_serie_internacoes(self, c, n):
        x, y = self._topo_pagina(
            c, n, "dir", "INTERNAÇÕES E CUSTOS", "EVOLUÇÃO DAS INTERNAÇÕES",
            "Faixa destacada: gestão do prefeito atual",
        )
        serie = self.d.get("internacoes_serie_historica") or {}
        anos = serie.get("anos") or []
        if anos and serie.get("total"):
            gestao = serie.get("gestao_atual") or {}
            faixa = None
            if gestao.get("inicio") in anos:
                i0 = anos.index(gestao["inicio"])
                i1 = anos.index(gestao["fim"]) if gestao.get("fim") in anos else len(anos) - 1
                faixa = (i0, i1)
            y = draw_line_chart(
                c, series=[{"nome": "Internações", "valores": serie.get("total"), "cor": BLUE_DARK}],
                categorias=anos, x=x, y=y, w=CONTENT_W, h=280,
                faixa_destaque=faixa, faixa_label="Gestão atual" if faixa else None,
                legenda=False,
            )
            y -= 14
            draw_caption(c, "Fonte: SIH/DATASUS. Elaboração: FNP.", x, y)
        else:
            draw_body(
                c,
                "Série histórica de internações ainda não disponível: "
                "coleta de dados em andamento (ver CLAUDE.md, seção "
                "Pendências).",
                x, y - 20, CONTENT_W,
            )

    # ─── Página 9: Ranking de causas de morte ────────────────────────────────

    def _pag_causas_morte(self, c, n):
        self._avisar_se_ausente("ranking_causas_morte", "Ranking de causas de morte")
        x, y = self._topo_pagina(
            c, n, "esq", "INTERNAÇÕES E CUSTOS", "CAUSAS DE MORTE",
            "Trânsito no ranking\nde causas de morte",
        )
        ranking = self.d.get("ranking_causas_morte") or {}
        posicoes = ranking.get("posicao_acidentes_transito") or {}
        if posicoes:
            draw_body(
                c,
                "Posição dos \"acidentes de trânsito\" no ranking de causas de "
                f"morte do município, por ano (fonte: {ranking.get('fonte', 'SMS')}).",
                x, y, CONTENT_W, size=9,
            )
            y -= 34
            anos_ordenados = sorted(posicoes.keys())
            total_causas = ranking.get("total_causas", 20)
            for ano in anos_ordenados:
                draw_ranking_item(c, int(posicoes[ano]), f"Acidentes de trânsito · {ano}",
                                  total_causas, x, y, w=CONTENT_W)
                y -= 36
        else:
            draw_body(c, "Ranking de causas de morte ainda não disponível para "
                        "este município.", x, y - 20, CONTENT_W)

        leitos = self.d.get("leitos_uti_hipotetico") or {}
        nota = leitos.get("nota")
        if nota:
            # draw_destaque_box trunca silenciosamente após 2 linhas — feito
            # para citação curta, não para um parágrafo. Um título curto no
            # box + o texto completo em draw_body logo abaixo evita perder
            # conteúdo sem aviso nenhum (ver CLAUDE.md: precisão importa
            # mais aqui do que em qualquer folheto anterior).
            y -= 20
            draw_destaque_box(
                c, "SE NÃO HOUVESSE SINISTROS DE TRÂNSITO",
                "Quantos leitos de UTI a cidade ganharia?",
                x, y - 60, CONTENT_W, h=70, font_size=17,
            )
            draw_body(c, nota, x + 10, y - 78, CONTENT_W - 20, size=9)

    # ─── Página 10: Metodologia ───────────────────────────────────────────────

    def _pag_metodologia(self, c, n):
        x, y = self._topo_pagina(
            c, n, "dir", "METODOLOGIA", "DE ONDE VÊM OS DADOS",
            "Fontes e tratamento",
        )
        passos = (self.d.get("metodologia") or {}).get("passos") or [
            "Mortes no trânsito: Sistema de Informação sobre Mortalidade "
            "(SIM/DATASUS), classificadas por modo (pedestre, ciclista, "
            "motociclista) a partir da causa básica do óbito.",
            "Internações por sinistro: Sistema de Informações Hospitalares "
            "e Sistema de Informações Ambulatoriais (SIH/SIA, DATASUS).",
            "Frota de veículos: Registro Nacional de Veículos Automotores "
            "(RENAVAM/DENATRAN), evolução histórica por tipo de veículo.",
            "Comparações (recorte metropolitano, mesmo porte, estado, "
            "Brasil, capitais): mesma fonte e ano de referência do "
            "indicador do município, para manter a comparação justa.",
            "Custo hospitalar e mapa por bairro: dado em coleta. Ver "
            "CLAUDE.md, seção Pendências, para o estado atual.",
        ]
        for i, passo in enumerate(passos, start=1):
            draw_eyebrow(c, f"PASSO {i}", x, y, color=BLUE)
            y = draw_body(c, passo, x, y - 14, CONTENT_W, size=9.5) - 14

    # ─── Página 11: Encerramento + QR ─────────────────────────────────────────

    def _pag_encerramento(self, c, n):
        draw_qr_page(c, self.W, self.H, self.d.get("url", self.URL_PADRAO), n, lado="esq")
