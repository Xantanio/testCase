# testCase
## Test Case: Automação Robótica de Processos — _Documentação_
### 1. Introdução:
O objetivo do programa é desenvolver requisições HTTP para extrair (GET) e enviar (POST) informações para a API fictícia **https://jsonplaceholder.typicode.com/**. E assim, obter informações de Usuários e Posts por usuário, realizar cálculos a partir dos dados estruturados, lidar com cenários inesperados e capturar respostas inconsistentes e erros.

### 2. Ferramentas e Configurações:
A linguagem utilizada para a codificação do algoritmo foi o Python.
As bibliotecas utilizadas foram:
1. **time**
  + Módulo da biblioteca padrão do Python que fornece funções para trabalhar com tempo, como pausas (time.sleep) e medição de tempo.
  + Usado para implementar backoff exponencial.  

2. **logging**
  + Módulo da biblioteca padrão do Python para registrar mensagens de log (informações, avisos, erros, etc.).
  + Usado para registrar informações sobre o progresso do código, erros e avisos.

3. **http.HTTPStatus**
  + Módulo da biblioteca padrão do Python que contém constantes para códigos de status HTTP (por exemplo, HTTPStatus.OK, HTTPStatus.NOT_FOUND).
  + Usado para definir os códigos de status HTTP que devem ser tratados como erros temporários e repetidos.

4. **requests**
  + Biblioteca de terceiros para fazer requisições HTTP de forma simples e eficiente.
  + Usado para enviar requisições GET e POST para a API consumida.

5. **requests.exceptions**
  + Submódulo da biblioteca requests que contém exceções específicas para erros de requisição HTTP.
  + Usado para capturar e tratar exceções como RequestException, HTTPError, Timeout e ConnectionError.
6. **pandas**
  + Biblioteca de terceiros para manipulação e análise de dados, especialmente em formato tabular (DataFrames).
  + Usado para ler dados de um arquivo Excel (pd.read_excel) e criar um DataFrame (pd.DataFrame).

### 3. Detalhes da Operações:
1. **Requisição para obter usuários**: \
*Endpoint*: https://jsonplaceholder.typicode.com/users \
*Método*: GET \
*Payload*: não há payload.
```
response = requests.get(f"{url}/users", timeout=5)
```
Se a requisição for bem sucedida, espera-se uma mensagem "Requisição bem-sucedida" no terminal e uma lista de usuários JSON no seguinte modelo:
```
[
  {
    "id": 1,
    "name": "Leanne Graham",
    "username": "Bret",
    "email": "Sincere@april.biz",
    "address": {
      "street": "Kulas Light",
      "suite": "Apt. 556",
      "city": "Gwenborough",
      "zipcode": "92998-3874",
      "geo": {
        "lat": "-37.3159",
        "lng": "81.1496"
      }
    },
    "phone": "1-770-736-8031 x56442",
    "website": "hildegard.org",
    "company": {
      "name": "Romaguera-Crona",
      "catchPhrase": "Multi-layered client-server neural-net",
      "bs": "harness real-time e-markets"
    }
  },
  ...
]
```
Como a URL é válida, a saída real é uma lista JSON com todos os usuários. Requisição bem-sucedida!

2. **Requisição para obter posts dos usuários**: \
*Endpoint*: https://jsonplaceholder.typicode.com/posts?userId={user_id} \
*Método*: GET \
*Payload*: não há payload.
```
response = requests.get(f"{url}/posts?userId={user_id}", timeout=5)
```
Se a requisição for bem sucedida, espera-se uma mensagem "Requisição bem-sucedida" no terminal e uma lista de todos os posts por usuário de todos os usuários JSON no seguinte modelo:
```
[
  {
    "userId": 1,
    "id": 1,
    "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
    "body": "quia et suscipit\nsuscipit..."
  },
  ...
]
```
Como a URL é válida, a saída real é uma lista JSON com todos os usuários. Requisição bem-sucedida!

3. **Requisição para enviar relatatórios**: \
*Endpoint*: https://jsonplaceholder.typicode.com/send-email \
*Método*: POST \
*Payload*: O payload é um JSON contendo o relatório gerado:
```
{
  "report": [
    {
      "ID do usuário": 1,
      "Nome do usuário": "Leanne Graham",
      "Número de posts": 10,
      "Média de caracteres por post": 150
    },
    {
      "ID do usuário": 2,
      "Nome do usuário": "Ervin Howell",
      "Número de posts": 8,
      "Média de caracteres por post": 200
    },
    ...
  ]
}
```
```
response = requests.post(f"https://67acd8f13f5a4e1477dc0dbf.mockapi.io/testCase/send-email", json=payload, timeout=10)
```
Se a requisição for bem sucedida, espera-se uma mensagem "Relatório enviado com sucesso!" no terminal e uma lista JSON contendo "ID do usuário", "Nome do usuário", "Número de posts" e "Média de caracteres".
```
[
  "report": [
    {
      "ID do usuário": 1,
      "Nome do usuário": "Leanne Graham",
      "Número de posts": 10,
      "Média de caracteres por post": 150
    },
    {
      "ID do usuário": 2,
      "Nome do usuário": "Ervin Howell",
      "Número de posts": 8,
      "Média de caracteres por post": 200
    },
    ...
  ]
]
```
Como a URL é inválida, a saída real é um erro status 404. Requisição falhou!

### 4. **Problemas e soluções**: \
  1. Como tratar os erros e exceções e solucionar-los?
- A primeira dificuldade foi pensar em como tratar as exceções de forma adequada. Como o servidor tem um estado dinâmico, tratar exceções de caráter temporário, presentes em retry_codes, foi a decisão imediata. As funções usaram loops para continuar com a tentativa de conexão após exceções capturadas dentro do bloco try e tratadas no bloco except. Essa abordagem garantiu que o código fosse resiliente a falhas temporárias, como erros de rede, sobrecarga do servidor ou indisponibilidade momentânea. A estratégia de backoff exponencial, onde o tempo de espera entre as tentativas dobra a cada falha, foi implementada para evitar sobrecarregar o servidor e aumentar as chances de sucesso nas tentativas subsequentes.
- Além do tratamento de exceções relacionadas à conexão e às respostas da API, outra camada importante de robustez foi adicionada ao código: o tratamento de erros nos dados. Afinal, mesmo que a requisição seja bem-sucedida, os dados retornados podem estar incompletos, mal formatados ou inconsistentes. Para lidar com esses cenários, foi implementada uma verificação rigorosa dos dados. A função verify_data foi criada para garantir que todos os campos obrigatórios estivessem presentes nos dados retornados. Essa função não apenas verifica as chaves principais, como id, name, e email, mas também valida campos aninhados, como address e geo, garantindo que a estrutura dos dados esteja completa e correta. Caso algum campo esteja ausente, um aviso é registrado no log, e o item é descartado ou tratado de acordo com a lógica do programa.
  ```
  def verify_data(data, required_keys, context=""):
    missing_keys = required_keys - data.keys()
      if missing_keys:
          error_message = f"Faltam as chaves {missing_keys} no {context}."
          logger.warning(error_message)
          return False
      
      return True, None
  ```

### 5. **Conclusão**: \
Os resultados obtidos atenderam as expectativas de acordo com o que foi proposto no documento do Test Case. O algoritmo cumpre com todas as requisições, trata possíveis erros e exceções, realiza a consumação da API fictícia, gera o documento com os dados esperados e envia o payload para o endpoint **send-email**.
