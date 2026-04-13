# Explicação do workflow `CI Pipeline`

Este README explica, passo a passo, o arquivo de GitHub Actions abaixo, que automatiza **testes**, **lint**, **cobertura** e **build** do projeto.

---

## Arquivo analisado

```yaml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: password
          MYSQL_DATABASE: clientes_db
        ports:
          - 3306:3306
        options: --health-cmd="mysqladmin ping" --health-interval=10s --health-timeout=5s --health-retries=3

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python 3.9
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Wait for MySQL
      run: |
        while ! mysqladmin ping -h"127.0.0.1" --silent; do
          sleep 1
        done

    - name: Set up test database
      run: |
        mysql -h 127.0.0.1 -u root -ppassword -e "CREATE DATABASE IF NOT EXISTS clientes_db_test;"

    - name: Run linting with flake8
      run: |
        pip install flake8
        # Stop the build if there are Python syntax errors or undefined names
        flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics
        # Exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
        flake8 src --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

    - name: Run tests with coverage
      env:
        DATABASE_HOST: 127.0.0.1
        DATABASE_PORT: 3306
        DATABASE_NAME: clientes_db
        DATABASE_USER: root
        DATABASE_PASSWORD: password
        TEST_DATABASE_NAME: clientes_db_test
      run: |
        pytest --cov=src --cov-report=xml --cov-report=term-missing --cov-fail-under=80

    - name: Upload coverage to Codecov
      if: success()
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python 3.9
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Build application
      run: |
        echo "Building application..."
        # Add your build steps here if needed

    - name: Create deployment artifact
      run: |
        tar czf app.tar.gz src/ requirements.txt .env docker-compose.yml init.sql

    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: app-artifact
        path: app.tar.gz
```

---

# Visão geral

Esse workflow define uma **pipeline de integração contínua (CI)** para um projeto Python.

Ele faz duas coisas principais:

1. Executa **testes, lint e cobertura**.
2. Executa um **build** apenas quando estiver na branch `main`.

---

# 1. Nome do workflow

```yaml
name: CI Pipeline
```

Aqui você define o nome do workflow que vai aparecer na aba **Actions** do GitHub.

---

# 2. Quando esse workflow é executado

```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
```

## O que isso significa

O workflow roda em duas situações:

### a) Quando acontece um `push`
```yaml
push:
  branches: [ main, develop ]
```

Ele será executado quando alguém enviar código diretamente para as branches:

- `main`
- `develop`

### b) Quando acontece um `pull_request`
```yaml
pull_request:
  branches: [ main ]
```

Ele também será executado quando alguém abrir ou atualizar um Pull Request cujo destino seja a branch `main`.

## Na prática

- Se você fizer push para `develop`, a pipeline roda.
- Se você fizer push para `main`, a pipeline roda.
- Se você abrir um PR de `feature-x` para `main`, a pipeline também roda.

---

# 3. Jobs do workflow

O workflow tem **dois jobs**:

- `test`
- `build`

Cada job é uma etapa maior da pipeline.

---

# 4. Job `test`

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
```

Esse job roda em uma máquina virtual Linux Ubuntu disponibilizada pelo GitHub.

---

## 4.1 Serviço MySQL

```yaml
services:
  mysql:
    image: mysql:8.0
    env:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: clientes_db
    ports:
      - 3306:3306
    options: --health-cmd="mysqladmin ping" --health-interval=10s --health-timeout=5s --health-retries=3
```

Aqui o workflow sobe um **container MySQL** para que seus testes possam usar banco de dados real.

### O que cada parte faz

- `image: mysql:8.0`  
  Usa a imagem oficial do MySQL 8.0.

- `MYSQL_ROOT_PASSWORD: password`  
  Define a senha do usuário root.

- `MYSQL_DATABASE: clientes_db`  
  Cria automaticamente um banco chamado `clientes_db`.

- `ports: 3306:3306`  
  Expõe a porta do MySQL.

- `options: --health-cmd=...`  
  Faz um health check para verificar se o banco está pronto para uso.

---

## 4.2 Checkout do código

```yaml
- name: Checkout code
  uses: actions/checkout@v3
```

Essa etapa baixa o código do repositório para dentro da máquina onde a pipeline está rodando.

Sem isso, o GitHub Actions não teria acesso aos arquivos do seu projeto.

---

## 4.3 Configuração do Python

```yaml
- name: Set up Python 3.9
  uses: actions/setup-python@v4
  with:
    python-version: '3.9'
```

Aqui o ambiente é preparado para usar **Python 3.9**.

---

## 4.4 Cache das dependências

```yaml
- name: Cache pip dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

Essa etapa salva o cache dos pacotes instalados pelo `pip`.

## Vantagem
Na próxima execução da pipeline, se o `requirements.txt` não mudar, o processo pode ficar mais rápido.

### Sobre a chave do cache

```yaml
key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

Essa chave muda quando o arquivo `requirements.txt` muda.

Ou seja:
- se as dependências continuarem iguais, o cache pode ser reaproveitado;
- se o `requirements.txt` mudar, o cache antigo deixa de servir e um novo será criado.

---

## 4.5 Instalação das dependências

```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```

Aqui o workflow:

1. atualiza o `pip`
2. instala as dependências do projeto

---

## 4.6 Espera o MySQL ficar disponível

```yaml
- name: Wait for MySQL
  run: |
    while ! mysqladmin ping -h"127.0.0.1" --silent; do
      sleep 1
    done
```

Mesmo que o container do MySQL já tenha sido iniciado, o banco pode ainda não estar pronto para conexões.

Esse laço fica testando até o MySQL responder.

---

## 4.7 Criação do banco de teste

```yaml
- name: Set up test database
  run: |
    mysql -h 127.0.0.1 -u root -ppassword -e "CREATE DATABASE IF NOT EXISTS clientes_db_test;"
```

Essa etapa cria um banco específico para testes:

- `clientes_db_test`

Isso é bom porque separa o banco principal do banco de testes.

---

## 4.8 Lint com flake8

```yaml
- name: Run linting with flake8
  run: |
    pip install flake8
    flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics
    flake8 src --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

Aqui o workflow analisa a qualidade do código.

### Primeira execução do flake8
```yaml
flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics
```

Essa linha é mais rígida. Ela procura erros críticos, como:

- erro de sintaxe
- nomes indefinidos
- alguns problemas graves de parsing

Se encontrar problema, o job falha.

### Segunda execução do flake8
```yaml
flake8 src --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

Essa linha mostra outros avisos de estilo e complexidade, mas usa `--exit-zero`.

Isso significa que ela **não derruba a pipeline**, apenas reporta.

### Observação importante
Se você quiser que o estilo do código também bloqueie o PR, o ideal é remover o `--exit-zero`.

---

## 4.9 Testes com cobertura

```yaml
- name: Run tests with coverage
  env:
    DATABASE_HOST: 127.0.0.1
    DATABASE_PORT: 3306
    DATABASE_NAME: clientes_db
    DATABASE_USER: root
    DATABASE_PASSWORD: password
    TEST_DATABASE_NAME: clientes_db_test
  run: |
    pytest --cov=src --cov-report=xml --cov-report=term-missing --cov-fail-under=80
```

Essa é uma das partes mais importantes.

### O que acontece aqui

- define variáveis de ambiente para o teste acessar o banco
- roda os testes com `pytest`
- mede cobertura com `pytest-cov`

### Explicando o comando

```bash
pytest --cov=src --cov-report=xml --cov-report=term-missing --cov-fail-under=80
```

- `--cov=src`  
  Mede a cobertura do código dentro da pasta `src`

- `--cov-report=xml`  
  Gera um arquivo `coverage.xml`

- `--cov-report=term-missing`  
  Mostra no terminal quais linhas não foram cobertas

- `--cov-fail-under=80`  
  Faz a pipeline falhar se a cobertura for menor que 80%

## Isso responde diretamente à sua ideia de requisito mínimo

Se você quiser aceitar PR só com cobertura mínima, esse comando já faz isso.

---

## 4.10 Envio da cobertura para o Codecov

```yaml
- name: Upload coverage to Codecov
  if: success()
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
    flags: unittests
    name: codecov-umbrella
```

Se tudo der certo, o arquivo `coverage.xml` é enviado ao Codecov.

### Para que serve
O Codecov mostra relatórios visuais de cobertura e pode comentar no PR.

### `if: success()`
Essa etapa só roda se as etapas anteriores tiverem funcionado.

---

# 5. Job `build`

```yaml
build:
  needs: test
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'
```

Esse job só começa depois que o job `test` passar, por causa de:

```yaml
needs: test
```

E ele só roda quando a referência atual for a branch `main`:

```yaml
if: github.ref == 'refs/heads/main'
```

## Na prática
- em PR para `main`, o job `test` roda;
- o `build` não necessariamente roda nesse PR, porque ele está condicionado ao branch ref ser `main`;
- quando há push direto na `main`, aí o `build` pode rodar.

---

## 5.1 Checkout do código

```yaml
- name: Checkout code
  uses: actions/checkout@v3
```

Baixa o código novamente para esse job.

Cada job tem seu próprio ambiente isolado, então precisa repetir algumas etapas.

---

## 5.2 Configuração do Python

```yaml
- name: Set up Python 3.9
  uses: actions/setup-python@v4
  with:
    python-version: '3.9'
```

Configura o Python 3.9 no job de build.

---

## 5.3 Instalação das dependências

```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```

Instala as dependências necessárias para o build.

---

## 5.4 Build da aplicação

```yaml
- name: Build application
  run: |
    echo "Building application..."
    # Add your build steps here if needed
```

No momento, esse passo não faz um build real. Ele apenas imprime uma mensagem.

Isso funciona como um placeholder para você colocar comandos reais depois, por exemplo:

- gerar imagem Docker
- compilar arquivos
- empacotar a aplicação
- gerar arquivos estáticos

---

## 5.5 Criação do artefato

```yaml
- name: Create deployment artifact
  run: |
    tar czf app.tar.gz src/ requirements.txt .env docker-compose.yml init.sql
```

Aqui a pipeline cria um arquivo compactado chamado:

- `app.tar.gz`

Esse arquivo contém:

- `src/`
- `requirements.txt`
- `.env`
- `docker-compose.yml`
- `init.sql`

### Cuidado importante
Incluir `.env` no artefato pode ser perigoso se ele tiver segredos reais.

O mais recomendado é não empacotar `.env` com credenciais sensíveis.

---

## 5.6 Upload do artefato

```yaml
- name: Upload artifact
  uses: actions/upload-artifact@v3
  with:
    name: app-artifact
    path: app.tar.gz
```

Esse passo salva o arquivo gerado como artefato da execução do GitHub Actions.

Depois você pode baixar esse arquivo diretamente pela interface do GitHub Actions.

---

# 6. Resumo do fluxo completo

## Quando faz push na `develop`
- roda o job `test`
- o job `build` não roda

## Quando faz push na `main`
- roda o job `test`
- se passar, roda o job `build`

## Quando abre PR para `main`
- roda o job `test`
- o `build` tende a não rodar por causa da condição da branch

---

# 7. Como isso ajuda a bloquear Pull Request

Se você configurar a branch `main` com proteção e exigir que esse workflow passe, você consegue impedir merge quando:

- houver erro de sintaxe
- testes falharem
- cobertura ficar abaixo de 80%

## Observação
No seu caso atual:

- a cobertura mínima de 80% **já está obrigatória**
- os erros críticos do flake8 **já podem falhar a pipeline**
- as regras de estilo do segundo flake8 **não bloqueiam** porque usam `--exit-zero`

---

# 8. Pontos de melhoria nesse workflow

Aqui estão algumas melhorias possíveis:

## 1. Instalar flake8 junto com requirements
Hoje ele é instalado separadamente:
```yaml
pip install flake8
```

Você pode colocar `flake8` no `requirements-dev.txt` ou no próprio arquivo de dependências de desenvolvimento.

---

## 2. Tornar o segundo flake8 obrigatório
Hoje ele só avisa:
```yaml
flake8 src --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

Se quiser bloquear PR por estilo e complexidade, remova `--exit-zero`.

---

## 3. Não empacotar `.env`
Se o `.env` tiver senha, token ou segredo, o ideal é gerar artefato sem ele.

---

## 4. Usar secrets do GitHub
Em vez de deixar senha fixa:
```yaml
MYSQL_ROOT_PASSWORD: password
```

Você pode usar secrets do GitHub para dados sensíveis.

---

## 5. Atualizar versões das actions
Hoje você usa:
- `actions/checkout@v3`
- `actions/setup-python@v4`
- `actions/cache@v3`
- `actions/upload-artifact@v3`

Dependendo do momento do projeto, pode valer a pena atualizar para versões mais recentes.

---

# 9. Exemplo do que esse workflow garante

Com esse pipeline, um PR para `main` só deve ser aceito com mais segurança se:

- o código estiver sem erros críticos de lint
- os testes passarem
- a cobertura for de pelo menos 80%

Depois, se você proteger a branch `main` e marcar esse workflow como obrigatório, o merge fica bloqueado até tudo passar.

---

# 10. Conclusão

Esse workflow já está bem próximo de uma pipeline útil de CI para projetos Python com MySQL.

Ele faz o básico importante:

- sobe banco de dados
- instala dependências
- executa lint
- roda testes
- valida cobertura mínima
- gera artefato em `main`

A principal ideia é:

- **job `test`** valida qualidade e confiabilidade
- **job `build`** prepara artefato para deploy, mas só na `main`

---

# 11. Sugestão de frase para README do projeto

Você pode incluir algo como:

> Este projeto utiliza GitHub Actions para executar lint, testes automatizados, validação de cobertura e geração de artefatos de build. Pull Requests destinados à branch principal podem ser protegidos exigindo a aprovação desses checks antes do merge.

---
