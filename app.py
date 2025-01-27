from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor

# Inicializa o aplicativo Flask
app = Flask(__name__)

# Configurações para o banco de dados MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Alterar para o seu usuário MySQL
app.config['MYSQL_PASSWORD'] = ''  # So usar se pedir
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
    cursor = mysql.connection.cursor()  # Usando o cursor diretamente
    cursor.execute("SELECT * FROM tb_produtos")
    produtos = cursor.fetchall()  # Agora 'produtos' será uma lista de tuplas
    cursor.close()
    return render_template('lista_produtos.html', produtos=produtos)


# Rota para adicionar um produto
@app.route('/produtos/adicionar', methods=['GET', 'POST'])
def adicionar_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        categoria = request.form['categoria']
        preco_custo = float(request.form['preco_custo'])
        preco_venda = float(request.form['preco_venda'])
        quantidade_estoque = int(request.form['quantidade_estoque'])

        # Conexão com o banco de dados
        cur = mysql.connection.cursor()

        # Comando SQL para inserir o produto na tabela tb_produtos
        cur.execute("""
            INSERT INTO tb_produtos (pro_nome, pro_descricao, pro_categoria, pro_custo, pro_preco, pro_quantidade)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nome, descricao, categoria, preco_custo, preco_venda, quantidade_estoque))

        # Commit para confirmar a inserção
        mysql.connection.commit()

        # Fechar o cursor
        cur.close()

        # Redirecionar para a página de lista de produtos após a inserção
        return redirect(url_for('lista_produtos'))  # Redireciona para a lista de produtos

    # Caso o método seja GET, renderiza o formulário de adicionar produto
    return render_template('adicionar_produto.html')


# Rota para cadastrar cliente
@app.route('/clientes/adicionar', methods=['GET', 'POST'])
def adicionar_cliente():
    if request.method == 'POST':
        cnpj = request.form['cnpj']
        nome = request.form['nome']

        # Conexão com o banco de dados
        cur = mysql.connection.cursor()

        # Comando SQL para inserir o cliente
        cur.execute("""
            INSERT INTO tb_clientes (cli_cnpj, cli_nome)
            VALUES (%s, %s)
        """, (cnpj, nome))

        # Commit para confirmar a inserção
        mysql.connection.commit()

        # Fechar o cursor
        cur.close()

        # Redirecionar para a página de lista de clientes
        return redirect(url_for('lista_clientes'))  # Redireciona para a lista de clientes

    # Caso o método seja GET, renderiza o formulário de adicionar cliente
    return render_template('adicionar_cliente.html')


# Rota para movimentação de produto
@app.route('/movimentacao/<int:id_produto>', methods=['GET', 'POST'])
def movimentacao(id_produto):
    # Recupera o produto específico
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM tb_produtos WHERE pro_id = %s", (id_produto,))
    produto = cursor.fetchone()  # Recupera o produto
    cursor.execute("SELECT * FROM tb_clientes")  # Recupera todos os clientes para a movimentação
    clientes = cursor.fetchall()
    cursor.close()

    # Se o método for POST, processa a movimentação
    if request.method == 'POST':
        quantidade = int(request.form['quantidade'])  # Quantidade movimentada
        tipo = request.form['tipo']  # Armazenamos o tipo como 'motivo' na movimentação
        cliente_id = request.form['cliente_id'] if 'cliente_id' in request.form else None  # Para venda ou devolução

        cursor = mysql.connection.cursor()

        # Verifica o tipo de movimentação
        if tipo == 'entrada' or tipo == 'devolucao':
            # Aumenta o estoque
            cursor.execute("""
                UPDATE tb_produtos
                SET pro_quantidade = pro_quantidade + %s
                WHERE pro_id = %s
            """, (quantidade, id_produto))
            
            # Para entradas, definimos mov_cli_id como NULL
            cliente_id = None
        elif tipo == 'venda':
            # Verifica se o estoque é suficiente para a venda
            cursor.execute("SELECT pro_quantidade FROM tb_produtos WHERE pro_id = %s", (id_produto,))
            estoque_atual = cursor.fetchone()[0]
            
            if estoque_atual >= quantidade:
                # Se o estoque for suficiente, diminui o estoque
                cursor.execute("""
                    UPDATE tb_produtos
                    SET pro_quantidade = pro_quantidade - %s
                    WHERE pro_id = %s
                """, (quantidade, id_produto))
            else:
                # Mensagem amigável caso o estoque seja insuficiente
                flash("Desculpe, o estoque é insuficiente para completar a venda. Temos apenas " +
                      str(estoque_atual) + " unidades disponíveis.", 'error')
                cursor.close()
                return redirect(url_for('movimentacao', id_produto=id_produto))

        # Registrar a movimentação na tabela de movimentações
        cursor.execute("""
            INSERT INTO tb_movimentacoes (mov_pro_id, mov_cli_id, mov_motivo, mov_data, mov_quantidade)
            VALUES (%s, %s, %s, NOW(), %s)
        """, (id_produto, cliente_id, tipo, quantidade))

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('lista_produtos'))  # Redireciona para a lista de produtos

    # Renderiza o formulário de movimentação
    return render_template('movimentacao_produto.html', produto=produto, clientes=clientes)

@app.route('/relatorio', methods=['GET', 'POST'])
def relatorio():
    cursor = mysql.connection.cursor()

    # Buscar produtos com estoque baixo
    cursor.execute("""
        SELECT pro_nome, pro_quantidade
        FROM tb_produtos
        WHERE pro_quantidade < 10
    """)
    produtos_baixos = cursor.fetchall()

    if produtos_baixos:
        flash("Atenção: Alguns produtos estão com estoque baixo!", "warning")  # Adicionando o flash

    # Buscar todas as categorias únicas no banco de dados
    cursor.execute("""
        SELECT DISTINCT pro_categoria
        FROM tb_produtos
    """)
    categorias = cursor.fetchall()

    # Buscar todos os produtos para o filtro
    cursor.execute("""
        SELECT pro_nome
        FROM tb_produtos
    """)
    produtos = cursor.fetchall()

    # Lógica para gerar o relatório com base nas datas e filtros
    if request.method == 'POST':
        data_inicial = request.form['data_inicial']
        data_final = request.form['data_final']
        filtro_categoria = request.form['filtro_categoria']
        filtro_produto = request.form['filtro_produto']

        # Ajuste no filtro para incluir a última data
        query = """
            SELECT tb_movimentacoes.mov_id, tb_produtos.pro_nome, tb_clientes.cli_nome, 
                   tb_movimentacoes.mov_motivo, tb_movimentacoes.mov_data, tb_movimentacoes.mov_quantidade
            FROM tb_movimentacoes
            JOIN tb_produtos ON tb_produtos.pro_id = tb_movimentacoes.mov_pro_id
            LEFT JOIN tb_clientes ON tb_clientes.cli_id = tb_movimentacoes.mov_cli_id
            WHERE mov_data BETWEEN %s AND %s
        """

        params = [data_inicial, data_final]

        if filtro_categoria:
            query += " AND pro_categoria = %s"
            params.append(filtro_categoria)

        if filtro_produto:
            query += " AND pro_nome = %s"
            params.append(filtro_produto)

        cursor.execute(query, tuple(params))
        movimentacoes = cursor.fetchall()

        # Resumo das entradas e saídas
        resumo = {}
        for movimentacao in movimentacoes:
            tipo = movimentacao[3]
            if tipo not in resumo:
                resumo[tipo] = 0
            resumo[tipo] += movimentacao[5]

        cursor.close()

        # Exibir mensagem se não houver movimentação
        if not movimentacoes:
            mensagem = "Nenhuma movimentação encontrada para este período."
        else:
            mensagem = None

        return render_template('relatorio.html', 
                               produtos_baixos=produtos_baixos, 
                               movimentacoes=movimentacoes, 
                               resumo=resumo, 
                               mensagem=mensagem,
                               categorias=categorias,  # Passa as categorias dinâmicas
                               produtos=produtos)  # Passa todos os produtos para o filtro

    cursor.close()
    return render_template('relatorio.html', 
                           produtos_baixos=produtos_baixos, 
                           categorias=categorias,  # Passa as categorias dinâmicas
                           produtos=produtos)  # Passa todos os produtos para o filtro

# Rota para listar clientes
@app.route('/clientes', methods=['GET'])
def lista_clientes():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM tb_clientes")
    clientes = cursor.fetchall()
    cursor.close()
    return render_template('lista_clientes.html', clientes=clientes)

@app.route('/produtos/editar/<int:id>', methods=['GET', 'POST']) 
def editar_produto(id):
    cursor = mysql.connection.cursor(DictCursor)  # Use DictCursor em vez de dictionary=True
    
    # Se o método for POST, atualiza os dados do produto
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
    
    # Se o método for GET, exibe os dados do produto para edição
    cursor.execute("SELECT * FROM tb_produtos WHERE pro_id = %s", (id,))
    produto = cursor.fetchone()
    cursor.close()
    
    return render_template('editar_produto.html', produto=produto)

@app.route('/produtos/excluir/<int:id>', methods=['POST'])
def excluir_produto(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM tb_produtos WHERE pro_id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('lista_produtos'))

if __name__ == "__main__":
    app.run(debug=True)
