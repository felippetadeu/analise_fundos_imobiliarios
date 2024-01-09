import requests
from dataclasses import dataclass
from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import List

@dataclass
class FundsExplorerService:
    url: str = 'https://www.fundsexplorer.com.br'

    def get_fiis(self) -> List[Tag]:
        site = self.url
        html = requests.get(f'{site}/funds').content

        dados = BeautifulSoup(html, 'html.parser')

        fiis_html = dados.find_all("div", {"data-element":"content-list-ticker"})

        return fiis_html
    
    def get_fii(self, simbolo) -> BeautifulSoup:
        site = self.url
        html = requests.get(f'{site}/funds/{simbolo}').content

        dados = BeautifulSoup(html, 'html.parser')
        
        return dados