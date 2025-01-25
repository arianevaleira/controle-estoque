from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from datetime import datetime

# Inicializa o aplicativo Flask
app = Flask(__name__)

# Configurações para o banco de dados MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Alterar para o seu usuário MySQL
app.config['MYSQL_PASSWORD'] = ''  # Se usar senha, colocar aqui
app.config['MYSQL_DB'] = 'db_estoque'

# Configuração do Flask
app.config['SECRET_KEY'] = 'SUPER_DIFICIL'

# Inicializa a conexão com o MySQL
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/produtos', methods=['GET'])
def lista_produtos():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM tb_produtos")
    produtos = cursor.fetchall()
    cursor.close()
    return render_template('lista_produtos.html', produtos=produtos)

@app.route('/produtos/adicionar', methods=['GET', 'POST'])
def adicionar_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco_custo = float(request.form['preco_custo'])
        preco_venda = float(request.form['preco_venda'])
        quantidade_estoque = int(request.form['quantidade_estoque'])

        cur = mysql.connection.cursor()
        cur.execute(""" 
            INSERT INTO tb_produtos (pro_nome, pro_descricao, pro_custo, pro_preco, pro_quantidade)
            VALUES (%s, %s, %s, %s, %s)
        """, (nome, descricao, preco_custo, preco_venda, quantidade_estoque))

        mysql.connection.commit()
        cur.close()
        return redirect(url_for('lista_produtos'))
    
    return render_template('adicionar_produto.html')

@app.route('/movimentacao/<int:id_produto>', methods=['GET', 'POST'])
def movimentacao(id_produto):
    if request.method == 'POST':
        tipo = request.form['tipo']
        quantidade = int(request.form['quantidade'])
        motivo = request.form['motivo']

        cursor = mysql.connection.cursor()

        if tipo == 'entrada':  # Se for entrada, adiciona a quantidade
            cursor.execute("""
                UPDATE tb_produtos
                SET pro_quantidade = pro_quantidade + %s
                WHERE pro_id = %s
            """, (quantidade, id_produto))
        else:  # Se for saída, subtrai a quantidade
            cursor.execute("""
                UPDATE tb_produtos
                SET pro_quantidade = pro_quantidade - %s
                WHERE pro_id = %s
            """, (quantidade, id_produto))

        cursor.execute("""
            INSERT INTO tb_movimentacoes (mov_pro_id, mov_quantidade, mov_motivo, mov_data)
            VALUES (%s, %s, %s, NOW())
        """, (id_produto, quantidade, motivo))

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('lista_produtos'))
    
    return render_template('movimentacao_produto.html', id_produto=id_produto)

# Relatórios

@app.route('/relatorio')
def relatorio():
    return render_template('relatorio.html')

@app.route('/relatorio/produtos_estoque_baixo')
def produtos_estoque_baixo():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM tb_produtos WHERE pro_quantidade < 10")
    produtos_baixo_estoque = cursor.fetchall()
    cursor.close()
    return render_template('relatorio_produtos_estoque_baixo.html', produtos=produtos_baixo_estoque)

@app.route('/relatorio/historico_movimentacoes/<int:id_produto>')
def historico_movimentacoes(id_produto):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT * FROM tb_movimentacoes
        WHERE mov_pro_id = %s
        ORDER BY mov_data DESC
    """, (id_produto,))
    movimentacoes = cursor.fetchall()
    cursor.close()
    return render_template('relatorio_historico_movimentacoes.html', movimentacoes=movimentacoes, id_produto=id_produto)

@app.route('/relatorio/entradas_saidas_periodo', methods=['GET', 'POST'])
def entradas_saidas_periodo():
    if request.method == 'POST':
        data_inicial = request.form['data_inicial']
        data_final = request.form['data_final']
        cursor = mysql.connection.cursor()
        
        cursor.execute("""
            SELECT SUM(mov_quantidade) as total_quantidade, mov_motivo 
            FROM tb_movimentacoes
            WHERE mov_data BETWEEN %s AND %s
            GROUP BY mov_motivo
        """, (data_inicial, data_final))
        
        relatorio = cursor.fetchall()
        cursor.close()
        
        return render_template('relatorio_entradas_saidas_periodo.html', relatorio=relatorio, data_inicial=data_inicial, data_final=data_final)
    
    return render_template('entradas_saidas_periodo_form.html')

@app.route('/produtos/editar/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco_custo = float(request.form['preco_custo'])
        preco_venda = float(request.form['preco_venda'])
        quantidade_estoque = int(request.form['quantidade_estoque'])

        cursor.execute("""
            UPDATE tb_produtos
            SET pro_nome = %s, pro_descricao = %s, pro_custo = %s, pro_preco = %s, pro_quantidade = %s
            WHERE pro_id = %s
        """, (nome, descricao, preco_custo, preco_venda, quantidade_estoque, id))
        
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('lista_produtos'))

    cursor.execute("SELECT * FROM tb_produtos WHERE pro_id = %s", (id,))
    produto = cursor.fetchone()
    cursor.close()
    
    return render_template('editar_produto.html', produto=produto)

if __name__ == "__main__":
    app.run(debug=True)
