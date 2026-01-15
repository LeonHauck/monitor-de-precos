import threading
import time
from flask import Flask, render_template, request, redirect, url_for
from database import get_products, get_history, add_product, delete_product, init_db
from scraper import verificar_preco

app = Flask(__name__)

# --- AUTOMAÇÃO EM SEGUNDO PLANO ---
def worker_monitoramento():
    """Função que roda em loop checando os preços de todos os produtos."""
    print("Iniciando monitoramento automático...")
    while True:
        try:
            products = get_products()
            for product in products:
                print(f"Monitor: Verificando {product['name']}...")
                # Aqui precisamos que o verificar_preco receba a URL como parâmetro
                # Vou ajustar o scraper.py logo em seguida
                from scraper import verificar_preco_url
                verificar_preco_url(product['url'], product['target_price'])
                time.sleep(5) # Pequena pausa entre produtos para evitar bloqueio
        except Exception as e:
            print(f"Erro no monitor: {e}")
        
        # Espera 1 hora (3600 segundos) entre as checagens
        time.sleep(3600)


@app.route('/')
def index():
    """Página principal com a lista de produtos."""
    products = get_products()
    return render_template('index.html', products=products)

@app.route('/add', methods=['POST'])
def add():
    """Rota para adicionar novo produto."""
    name = request.form.get('name')
    url = request.form.get('url')
    target_price = request.form.get('target_price')
    
    if name and url and target_price:
        add_product(name, url, float(target_price))
    
    return redirect(url_for('index'))

@app.route('/delete/<int:product_id>')
def delete(product_id):
    """Rota para deletar produto."""
    delete_product(product_id)
    return redirect(url_for('index'))

@app.route('/edit/<int:product_id>', methods=['POST'])
def edit(product_id):
    """Rota para editar o preço alvo."""
    new_price = request.form.get('new_price')
    if new_price:
        from database import update_product_price
        update_product_price(product_id, float(new_price))
    return redirect(url_for('index'))


@app.route('/history/<int:product_id>')
def history(product_id):
    """Página de histórico de um produto."""
    history_data = get_history(product_id)
    return render_template('history.html', history=history_data)

if __name__ == '__main__':
    init_db()
    
    # Inicia a thread de monitoramento (daemon para fechar junto com o app)
    # Usamos o check de WERKZEUG_RUN_MAIN para não iniciar a thread duas vezes com o reloader do Flask
    import os
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        threading.Thread(target=worker_monitoramento, daemon=True).start()
        print("Thread de monitoramento iniciada.")
    
    app.run(debug=True)


