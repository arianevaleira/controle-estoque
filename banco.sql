create database db_estoque;
use db_estoque;

create table tb_usuarios(
usu_id int primary key auto_increment not null,
usu_nome varchar(255),
usu_senha varchar(255),
usu_email varchar(255)
);

create table tb_produtos(
pro_id int primary key auto_increment not null,
pro_nome varchar(255),
pro_descricao varchar(255),
pro_categoria varchar(45),
pro_custo decimal(10,2),
pro_preco decimal(10,2),
pro_quantidade varchar(255)
);

create table tb_movimentacoes(
mov_id int primary key auto_increment not null,
mov_pro_id int,
mov_usu_id int,
mov_motivo varchar(500),
mov_data datetime,
mov_quantidade int, # Quantidade que sera adicionada ou tirada do estoque 
foreign key (mov_pro_id) references tb_produtos(pro_id),
foreign key (mov_usu_id) references tb_usuarios(usu_id)
);

