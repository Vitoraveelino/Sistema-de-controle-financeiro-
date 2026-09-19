# 💰 Sistema de Controle Financeiro Pessoal

Aplicação web para registrar e acompanhar receitas e despesas, organizando os lançamentos por categoria. Permite consultar o saldo geral e o total gasto/recebido em cada categoria.

## Funcionalidades

- Registro de lançamentos (receitas e despesas) com descrição, valor, categoria, data e observações
- Listagem de lançamentos com filtro por tipo (receita/despesa)
- Exclusão de lançamentos
- Cálculo automático do saldo (receitas − despesas)
- Resumo de totais por categoria
- Categorias pré-cadastradas, podendo ser expandidas diretamente no banco

## Tecnologias utilizadas

- **Banco de dados:** MySQL
- **Back-end:** Python (Flask)
- **Front-end:** HTML, CSS e JavaScript (puro, sem frameworks)

## Estrutura do projeto

```
controle-financeiro/
├── app.py                  # Aplicação Flask (rotas da API e da página)
├── db.py                   # Conexão com o banco MySQL
├── requirements.txt        # Dependências Python
├── .env.example             # Modelo de variáveis de ambiente
├── database/
│   ├── schema.sql          # Criação das tabelas e categorias iniciais
│   └── queries.sql         # Consultas SQL de referência (saldo, gastos por categoria etc.)
└── static/
    ├── index.html           # Página principal
    ├── css/style.css        # Estilos
    └── js/app.js             # Lógica do front-end (consome a API)
```

## Como executar o projeto

### 1. Pré-requisitos

- Python 3.10+
- MySQL Server (local ou remoto)

### 2. Clonar o repositório

```bash
git clone https://github.com/<seu-usuario>/controle-financeiro.git
cd controle-financeiro
```

### 3. Criar o banco de dados

Execute o script `database/schema.sql` no seu servidor MySQL. Por exemplo, via terminal:

```bash
mysql -u root -p < database/schema.sql
```

Isso cria o banco `controle_financeiro`, as tabelas `categorias` e `lancamentos`, e insere algumas categorias padrão.

### 4. Configurar variáveis de ambiente

Copie o arquivo de exemplo e preencha com suas credenciais do MySQL:

```bash
cp .env.example .env
```

Edite o `.env` com o usuário, senha e nome do banco que você usa localmente.

### 5. Instalar as dependências

Recomenda-se usar um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 6. Rodar a aplicação

```bash
python app.py
```

Acesse **http://localhost:5000** no navegador.

## Endpoints da API

| Método | Rota                        | Descrição                                   |
|--------|-----------------------------|----------------------------------------------|
| GET    | `/api/categorias`           | Lista todas as categorias                     |
| GET    | `/api/lancamentos`          | Lista lançamentos (filtros: `tipo`, `categoria_id`, `mes`) |
| POST   | `/api/lancamentos`          | Cria um novo lançamento                       |
| DELETE | `/api/lancamentos/<id>`     | Exclui um lançamento                          |
| GET    | `/api/resumo`                | Retorna saldo geral e totais por categoria    |

### Exemplo de corpo para `POST /api/lancamentos`

```json
{
  "descricao": "Supermercado",
  "valor": 250.90,
  "tipo": "despesa",
  "categoria_id": 5,
  "data_lancamento": "2026-09-19",
  "observacoes": "Compra do mês"
}
```

## Consultas SQL de referência

O arquivo `database/queries.sql` traz consultas prontas para uso direto no MySQL, incluindo:

- Saldo geral (receitas − despesas)
- Total de gastos por categoria
- Total de receitas por categoria
- Resumo mensal (receitas, despesas e saldo por mês)
- Últimos lançamentos registrados

## Possíveis melhorias futuras

- Autenticação de usuários (múltiplos usuários no mesmo sistema)
- Edição de lançamentos já cadastrados
- Gráficos de gastos por categoria e por mês
- Exportação de relatórios em PDF/Excel

## Licença

Projeto de uso livre para fins de estudo e portfólio.
