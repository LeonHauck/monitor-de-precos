import requests
from bs4 import BeautifulSoup
import time
from database import save_price, init_db

# --- CONFIGURAÇÕES ---
# Para o seu estudo: mude esta URL para um produto que você queira monitorar na Amazon Brasil
URL_PRODUTO = 'https://www.amazon.com.br/Apple-iPhone-13-128-GB-Estelar/dp/B09G9FPGTN' 
PRECO_ALVO = 4000.00 
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Device-Memory": "8",
}


def extrair_preco_amazon(soup):
    """
    Função dedicada a minerar o preço dentro do HTML da Amazon.
    A Amazon usa classes diferentes dependendo do tipo de oferta.
    """
    # Estratégia 1: O novo padrão da Amazon (a-price-whole)
    preco_inteiro = soup.find("span", class_="a-price-whole")
    preco_centavos = soup.find("span", class_="a-price-fraction")
    
    if preco_inteiro:
        # Remove pontos de milhar e junta com os centavos
        texto = preco_inteiro.get_text(strip=True).replace('.', '').replace(',', '')
        if preco_centavos:
            texto += "." + preco_centavos.get_text(strip=True)
        return float(texto)

    # Estratégia 2: ID clássico (as vezes ainda aparece)
    preco_id = soup.find(id="priceblock_ourprice") or soup.find(id="priceblock_dealprice")
    if preco_id:
        texto = preco_id.get_text(strip=True).replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(texto)

    return None

def verificar_preco_url(url, preco_alvo):
    """Nova função que aceita URL e Alvo dinamicamente."""
    print(f"Verificando: {url}")
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        preco = extrair_preco_amazon(soup)
        
        if preco:
            print(f"Sucesso! Preço: R$ {preco:.2f}")
            save_price(url, preco)
            
            if preco < preco_alvo:
                print(f"--- ALERTA: {url} está abaixo do alvo! ---")
        else:
            print(f"Preço não encontrado para {url}")

    except Exception as e:
        print(f"Erro ao verificar {url}: {e}")

def verificar_preco():
    """Mantida para compatibilidade com o script antigo."""
    verificar_preco_url(URL_PRODUTO, PRECO_ALVO)

if __name__ == "__main__":
    init_db()
    verificar_preco()

