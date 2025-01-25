import os

class Config:
    # Configurações para o banco de dados MySQL
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'  # Alterar para o seu usuário MySQL
    MYSQL_PASSWORD = ''  # So usar se pedir
    MYSQL_DB = 'db_estoque'

    # Configuração do Flask
    SECRET_KEY = 'SUPER_DIFICIL'  # Para sessão, CSRF, etc.

