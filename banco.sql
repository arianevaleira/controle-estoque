DROP DATABASE IF EXISTS db_estoque;

CREATE DATABASE db_estoque;
USE db_estoque;

CREATE TABLE tb_clientes (
    cli_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    cli_cnpj VARCHAR(18),
    cli_nome VARCHAR(45)
);

CREATE TABLE tb_produtos (
    pro_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    pro_nome VARCHAR(255),
    pro_descricao VARCHAR(255),
    pro_categoria VARCHAR(45),
    pro_custo DECIMAL(10, 2),
    pro_preco DECIMAL(10, 2),
    pro_quantidade INT
);

CREATE TABLE tb_movimentacoes (
    mov_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    mov_pro_id INT,
    mov_cli_id INT,
    mov_motivo VARCHAR(500),
    mov_data DATETIME,
    mov_quantidade INT,  -- Quantidade que será adicionada ou removida do estoque
    FOREIGN KEY (mov_pro_id) REFERENCES tb_produtos(pro_id) ON DELETE CASCADE,
    FOREIGN KEY (mov_cli_id) REFERENCES tb_clientes(cli_id)
);
