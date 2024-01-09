import os
import numpy as np
import pandas as pd
from bs4.element import Tag
from dataclasses import dataclass
from datetime import datetime
from src.infrastructure.services.funds_explorer import FundsExplorerService
from src.domain.entities.fii import FII
from typing import List

@dataclass
class FIIService:

    def _retorna_valor_texto(self, valor_texto: str) -> float:
        if valor_texto is None:
            return None
        
        valor_texto = valor_texto.split(' ')
        valor = valor_texto[0]
        if valor.strip() == '-':
            return None
        
        fator_multiplicacao = 1
        valor = valor.replace('.', '').replace(',', '.')
        valor = float(valor)
        if len(valor_texto) == 2:
            fator = valor_texto[1]
            if fator == 'M':
                fator_multiplicacao = 1000000
            elif fator == 'B':
                fator_multiplicacao = 1000000000
            elif fator == 'T':
                fator_multiplicacao = 1000000000000

        return valor * fator_multiplicacao

    def _processar_fii(self, fii: Tag) -> FII:
        tipo = fii.find('span', {"class":"tickerBox__type"})
        if tipo is not None:
            tipo = tipo.text

        descricao = fii.find('span', {"class":"tickerBox__desc"})
        if descricao is not None:
            descricao = descricao.text

        simbolo = fii.find('div', {'class':"tickerBox__title"})
        if simbolo is not None:
            simbolo = simbolo.text

        dividend_patrimonio = fii.find_all('div', {"class":"tickerBox__info__box"})
        dividend_yield = None
        patrimonio_liquido = None
        if len(dividend_patrimonio) > 0:
            if dividend_patrimonio[0] is not None:
                dividend_yield = dividend_patrimonio[0].text
            
            if dividend_patrimonio[1] is not None:
                patrimonio_liquido = dividend_patrimonio[1].text

            if dividend_yield is not None:
                dividend_yield = self._retorna_valor_texto(dividend_yield)

            if patrimonio_liquido is not None:
                patrimonio_liquido = self._retorna_valor_texto(patrimonio_liquido)


        return FII(
            simbolo=simbolo,
            descricao=descricao,
            tipo=tipo.split(':')[0].strip(), 
            sub_tipo=tipo.split(':')[1].strip(),
            dividend_yield=dividend_yield,
            patrimonio_liquido=patrimonio_liquido
        )

    def get_fiis(self) -> List[FII]:
        fiis_html_tag = FundsExplorerService().get_fiis()
        fiis = []
        for fii_tag in fiis_html_tag:
            fiis.append(self._processar_fii(fii_tag))

        return fiis
    
    def possui_patrimonio_e_dividend_yield(self, fii: FII) -> bool:
        return fii.dividend_yield is not None and fii.patrimonio_liquido is not None
    
    def get_fiis_com_dividend_patrimonio(self, fiis: List[FII]) -> List[FII]:
        #removendo os que não possui: dvdy, pl
        filtered_results = list(filter(self.possui_patrimonio_e_dividend_yield, fiis))
        return filtered_results
    
    def get_fii(self, fii: FII):
        fii_html_tag = FundsExplorerService().get_fii(fii.simbolo)
        fii.processar_beautiful_soup(fii_html_tag)

    def start(self, save: bool = True):
        results = self.get_fiis()
        filtered_results = self.get_fiis_com_dividend_patrimonio(results)
        for idx, fii in enumerate(filtered_results):
            self.get_fii(fii)

        df = pd.DataFrame.from_dict(filtered_results)
        if save:
            df.to_csv(os.path.join(os.path.curdir, f'fiis_{datetime.now().strftime("%Y%m%d")}.csv'))
        return df