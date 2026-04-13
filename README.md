# API REST Flask - Gerenciamento de Clientes

API REST desenvolvida com Flask seguindo os princípios de **Arquitetura Limpa** para gerenciamento de clientes, com testes automatizados e pipeline CI/CD.

## 🏗️ Arquitetura

O projeto segue os princípios da **Clean Architecture** com separação clara de responsabilidades:

```
src/
├── domain/           # Regras de negócio e entidades
│   ├── client.py     # Entidade Client
│   └── exceptions.py # Exceções de domínio
├── application/      # Casos de uso
│   ├── use_cases.py  # Casos de uso (CRUD)
│   ├── dtos.py       # Data Transfer Objects
│   └── interfaces/   # Abstrações/Interfaces
├── infrastructure/   # Implementações técnicas
│   ├── database.py   # Configuração do banco
│   ├── models.py     # Modelos SQLAlchemy
│   └── repositories.py # Implementação dos repositórios
└── presentation/     # Controllers e rotas
    ├── controllers.py # Controllers HTTP
    └── routes.py     # Definição das rotas
```

## 🚀 Funcionalidades

- **Criar cliente**: POST `/api/clients`
- **Buscar cliente**: GET `/api/clients/{id}`
- **Listar clientes**: GET `/api/clients` (com paginação)
- **Atualizar cliente**: PUT `/api/clients/{id}`
- **Excluir cliente**: DELETE `/api/clients/{id}`
- **Health check**: GET `/health`

## 💾 Estrutura do Banco de Dados

```sql
CREATE TABLE clients (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  email VARCHAR(120) NOT NULL UNIQUE,
  phone VARCHAR(30),
  created_at TIMESTAMP DEFAULT NOW()
);
```

## 🛠️ Tecnologias Utilizadas

- **Flask** - Framework web
- **SQLAlchemy** - ORM
- **MySQL** - Banco de dados
- **pytest** - Testes automatizados
- **Docker** - Containerização
- **GitHub Actions** - CI/CD

## 📋 Pré-requisitos

- Python 3.9+
- Docker e Docker Compose
- MySQL (ou usar container Docker)

## 🔧 Instalação e Configuração

### 1. Clone o repositório

```bash
git clone <repository-url>
cd teste-python-ci
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### 3. Inicie o banco de dados

```bash
docker-compose up -d
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Execute a aplicação

```bash
python -m src.main
```

A API estará disponível em `http://localhost:5000`

## 🧪 Executar Testes

### Executar todos os testes

```bash
pytest
```

### Executar com cobertura

```bash
pytest --cov=src --cov-report=term-missing --cov-report=html
```

### Executar testes específicos

```bash
# Testes de domínio
pytest tests/test_domain.py

# Testes de casos de uso
pytest tests/test_use_cases.py

# Testes de integração da API
pytest tests/test_api_integration.py
```

## 📊 Cobertura de Testes

O projeto é configurado para exigir **mínimo de 80% de cobertura** nos testes. O pipeline CI/CD falha se a cobertura for inferior a 80%.

Para visualizar o relatório de cobertura:

```bash
pytest --cov=src --cov-report=html
# Abra htmlcov/index.html no navegador
```

## 🔄 Pipeline CI/CD

O projeto inclui um pipeline GitHub Actions que:

1. **Executa linting** com flake8
2. **Roda todos os testes** com cobertura mínima de 80%
3. **Gera relatório de cobertura** e envia para Codecov
4. **Cria artefato** para deploy (apenas na branch main)

O pipeline é executado a cada push/PR para as branches `main` e `develop`.

## 📚 Exemplos de Uso da API

### Criar cliente

```bash
curl -X POST http://localhost:5000/api/clients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "email": "joao.silva@email.com",
    "phone": "11999999999"
  }'
```

### Buscar cliente

```bash
curl http://localhost:5000/api/clients/1
```

### Listar clientes com paginação

```bash
curl "http://localhost:5000/api/clients?page=1&per_page=10"
```

### Atualizar cliente

```bash
curl -X PUT http://localhost:5000/api/clients/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João da Silva",
    "phone": "11888888888"
  }'
```

### Excluir cliente

```bash
curl -X DELETE http://localhost:5000/api/clients/1
```

## 🎯 Princípios Aplicados

### Clean Architecture

- **Separação de responsabilidades** por camadas
- **Inversão de dependências** com interfaces abstratas
- **Regras de negócio isoladas** na camada de domínio
- **Testabilidade** através de mocks e dependency injection

### Padrões de Design

- **Repository Pattern** para abstração do acesso a dados
- **Use Case Pattern** para casos de uso específicos
- **DTO Pattern** para transferência de dados
- **Dependency Injection** para baixo acoplamento

### Boas Práticas

- **Validação de dados** na camada de domínio
- **Tratamento de exceções** personalizado
- **Testes abrangentes** com alta cobertura
- **Documentação completa** da API
- **Pipeline CI/CD** automatizado

## 🏃‍♂️ Testes de Performance

Para testar a performance da API, você pode usar ferramentas como `ab` (Apache Bench):

```bash
# Teste de carga para listar clientes
ab -n 1000 -c 10 http://localhost:5000/api/clients
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🐛 Problemas Conhecidos e Soluções

### Erro de Conexão com MySQL

Se você encontrar erros de conexão com MySQL:

1. Verifique se o container MySQL está rodando: `docker ps`
2. Aguarde o MySQL inicializar completamente: `docker-compose logs mysql`
3. Teste a conexão: `mysql -h localhost -u root -ppassword`

### Falha nos Testes de Integração

Se os testes de integração falharem:

1. Verifique se o banco de teste existe: `clientes_db_test`
2. Confirme as variáveis de ambiente no arquivo `.env`
3. Execute os testes com verbose: `pytest -v tests/test_api_integration.py`

## 📈 Métricas do Projeto

- **Cobertura de testes**: 80%+ (obrigatório)
- **Linhas de código**: ~1000 linhas
- **Arquivos de teste**: 6 arquivos
- **Casos de teste**: 50+ testes
- **Endpoints**: 6 endpoints REST