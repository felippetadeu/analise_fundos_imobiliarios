from dataclasses import dataclass
from bs4 import BeautifulSoup
from bs4.element import ResultSet

@dataclass
class FII:
    simbolo: str = None
    tipo: str = None
    sub_tipo: str = None
    descricao: str = None
    dividend_yield: float = None
    patrimonio_liquido: float = None

    liquidez_diaria_media: float = None
    ultimo_rendimento: float = None
    valor_patrimonial: float = None
    rentabilidade_mes: float = None
    p_vp: float = None
    cotas_emitidas: int = None
    numero_cotistas: int = None
    min_semanas: float = None
    max_semanas: float = None
    valorizacao: float = None

    def _processar_indicator_box(self, rs: BeautifulSoup):
        try:
            indicator_box = rs.findAll('p')
            titulo:str = indicator_box[0].text
            valor:str = indicator_box[1].text.replace('\n', '').replace('\t', '').replace(' ', '').replace('R$', '').strip()

            if titulo == 'Liquidez Média Diária':
                self.liquidez_diaria_media = valor
            elif titulo == 'Último Rendimento':
                self.ultimo_rendimento = float(valor.replace('.', '').replace(',', '.'))
            elif titulo == 'Valor Patrimonial':
                self.valor_patrimonial = float(valor.replace('.', '').replace(',', '.'))
            elif titulo == 'Rentab. no mês':
                self.rentabilidade_mes = float(valor.replace('.', '').replace('%', '').replace(',', '.'))
            elif titulo == 'P/VP' and valor != 'N/A':
                self.ultimo_rendimento = float(valor.replace('.', '').replace(',', '.'))
        except Exception as e:
            print(e)
        

    def _processar_indicators_box(self, fii: BeautifulSoup):
        list_indicator_box = fii.findAll('div', {"class":"wrapper indicators"})[0].findAll('div', {"class":"indicators__box"})
        for ib in list_indicator_box:
            self._processar_indicator_box(ib)

    def _processar_bi_g(self, rs: BeautifulSoup):
        basic_info = rs.findAll('p')
        titulo:str = basic_info[0].text
        valor:str = basic_info[1].text

        if titulo == 'Número de cotistas':
            self.numero_cotistas = int(valor.replace('.', ''))
        elif titulo == 'Cotas emitidas':
            self.cotas_emitidas = int(valor.replace('.', ''))

    def _processar_basic_information_grid(self, fii: BeautifulSoup):
        list_bi_g = fii.findAll('div', {"class":"basicInformation__grid__box"})
        for bi_g in list_bi_g:
            self._processar_bi_g(bi_g)

    def _processar_quotation(self, rs: BeautifulSoup):
        quotation = rs.findAll('p')
        titulo:str = quotation[1].text
        valor:str = quotation[0].text.replace('%', '').replace(' ', '')
        attrs = rs.attrs
        
        if 'Valorização' in titulo:
            self.valorizacao = float(valor.replace(',', '.'))
            if attrs is not None: 
                if 'class' in attrs:
                    if 'baixa' in attrs['class']:
                        self.valorizacao * -1
        elif 'Máx' in titulo:
            self.max_semanas = float(valor.replace('R$', '').replace('.', '').replace(',', '.'))
        elif 'Mín' in titulo:
            self.min_semanas = float(valor.replace('R$', '').replace('.', '').replace(',', '.'))


    def _processar_quotations_grid(self, fii: BeautifulSoup):
        list_q_g = fii.findAll('div', {"class":"quotation__grid__box"})
        for quotation in list_q_g:
            self._processar_quotation(quotation)

    def processar_beautiful_soup(self, beautiful_soup: BeautifulSoup):
        self._processar_indicators_box(beautiful_soup)
        self._processar_basic_information_grid(beautiful_soup)
        self._processar_quotations_grid(beautiful_soup)