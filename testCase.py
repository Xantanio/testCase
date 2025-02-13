import time
import logging
from http import HTTPStatus
import requests
from requests.exceptions import RequestException, HTTPError, Timeout, ConnectionError
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

url = "https://jsonplaceholder.typicode.com"
retries = 3
retry_codes = [
    HTTPStatus.TOO_MANY_REQUESTS,
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.BAD_GATEWAY,
    HTTPStatus.SERVICE_UNAVAILABLE,
    HTTPStatus.GATEWAY_TIMEOUT,
]

def verify_data(data, required_keys, context=""):
    """
    Verifies if a given dictionary contains all the required keys.

    Parameters:
    data (dict): The dictionary to be verified.
    required_keys (set): A set of keys that must be present in the dictionary.
    context (str, optional): A string describing the context or purpose of the verification. Defaults to an empty string.

    Returns:
    tuple: A tuple containing a boolean value indicating whether all required keys are present,
           and a string error message if any required keys are missing.
           If all required keys are present, the error message will be None.
    """
    missing_keys = required_keys - data.keys()
    if missing_keys:
        error_message = f"Faltam as chaves {missing_keys} no {context}."
        logger.warning(error_message)
        return False
    
    return True, None



def getUsers():
    """
    This function sends a GET request to the specified URL to retrieve a list of users.
    It handles potential errors, such as HTTP errors, timeouts, and connection errors,
    and implements exponential backoff for retrying failed requests.

    Parameters:
    None

    Returns:
    list: A list of user dictionaries. Each dictionary contains user information such as 'id', 'name', etc.
    """
    for attempt in range(retries):
        try:
            logger.info(f"Tentativa {attempt + 1} de {retries}")
            response = requests.get(f"{url}/users", timeout=5)
            response.raise_for_status()
            logger.info("Requisição bem-sucedida!")
            users = response.json()

            if not users:
                logger.warning("Nenhum usuário encontrado.")
                return []
            
            valid_users = []
            required_user_keys = {'id', 'name', 'username', 'email', 'address', 'phone', 'website', 'company'}
            for user in users:
                is_valid = verify_data(user, required_user_keys, context=f"usuário {user['id']}")
                if is_valid:
                    valid_users.append(user)

            return valid_users

        except (HTTPError, Timeout, ConnectionError) as e:
            code = e.response.status_code if isinstance(e, HTTPError) else None
            if code in retry_codes:
                wait_time = 2 ** attempt
                logger.warning(f"Erro {code}. Tentando novamente em {wait_time} segundos.")
                time.sleep(wait_time)
                continue
            logger.error(f"Erro {code}. Requisição falhou.")
            raise

        except RequestException as e:
            logger.error(f"Erro ao obter usuários: {e}")
            raise

        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            raise


def getPosts(user_id):
    """
    This function sends a GET request to the specified URL to retrieve a list of posts for a given user.
    It handles potential errors, such as HTTP errors, timeouts, and connection errors,
    and implements exponential backoff for retrying failed requests.

    Parameters:
    user_id (int): The ID of the user for which to retrieve posts.

    Returns:
    list: A list of post dictionaries. Each dictionary contains post information such as 'id', 'title', etc.
    """
    for attempt in range(retries):
        try:
            logger.info(f"Tentativa {attempt + 1} de {retries}")
            response = requests.get(f"{url}/posts?userId={user_id}", timeout=5)
            response.raise_for_status()
            logger.info(f"Requisição bem-sucedida!")
            posts = response.json()

            if not posts:
                logger.warning("Nenhum post encontrado para o usuário.")
                return []
            
            valid_posts = []
            required_post_keys = {'userId', 'id', 'title', 'body'}
            for post in posts:
                is_valid = verify_data(post, required_post_keys, context=f"post {post.get('id', 'sem ID')}")
                if is_valid:
                    valid_posts.append(post)

            return valid_posts

        except (HTTPError, Timeout, ConnectionError) as e:
            code = e.response.status_code if isinstance(e, HTTPError) else None
            if code in retry_codes:
                wait_time = 2 ** attempt
                logger.warning(f"Erro {code}. Tentando novamente em {wait_time} segundos.")
                time.sleep(wait_time)
                continue
            logger.error(f"Erro {code}. Requisição falhou.")
            raise

        except RequestException as e:
            logger.error(f"Erro ao obter posts: {e}")
            raise

        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            raise


def charAverage(posts):
    """
    Calculates the average number of characters in the body of posts.

    Parameters:
    posts (list): A list of dictionaries, where each dictionary represents a post.
                 Each post dictionary must contain a 'body' key with a string value.

    Returns:
    float: The average number of characters in the body of the posts.
           Returns 0 if the list of posts is empty.
    """
    total_chars = 0
    for post in posts:
        total_chars += len(post['body'])
    return total_chars / len(posts) if posts else 0

def generateReport():
    """
    Generates a report containing user information and post statistics.

    The function retrieves user data from the API, fetches posts for each user,
    calculates the average number of characters in the body of the posts,
    and stores the data in a pandas DataFrame.
    The DataFrame is then saved as an Excel file named 'report.xlsx'.

    Parameters:
    None

    Returns:
    None
    """
    report = []
    users = getUsers()
    for user in users:
        posts = getPosts(user['id'])
        user_id = user['id']
        user_name = user['name']
        char_average = charAverage(posts)
        report.append({
            'ID do usuário': user_id,
            'Nome do usuário': user_name,
            'Número de posts': len(posts),
            'Média de caracteres por post': char_average
        })
    df = pd.DataFrame(report)
    df.to_excel('report.xlsx', index=False)
    logger.info("Relatório gerado com sucesso!")


def postReport():
    """
    This function sends a POST request to a specified URL to send a report.
    The report data is read from an Excel file named 'report.xlsx', converted to a dictionary,
    and sent as JSON in the request body. The function handles potential errors, such as file not found,
    empty file, HTTP errors, timeouts, and connection errors, and implements exponential backoff
    for retrying failed requests.

    Parameters:
    None

    Returns:
    None
    """
    try:
        report_data = pd.read_excel('report.xlsx').to_dict(orient='records')
        if not report_data:
            logger.error("O arquivo report.xlsx está vazio.")
            return
        payload = {'report': report_data}

    except FileNotFoundError:
        logger.error("Arquivo report.xlsx não encontrado.")
        raise

    except pd.errors.EmptyDataError:
        logger.error("O arquivo report.xlsx está vazio ou mal formatado.")
        raise

    for attempt in range(retries):
        logger.info(f"Post method: Tentativa {attempt + 1} de {retries}")
        try:
            response = requests.post(f"{url}/send-email", json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Relatório enviado com sucesso!")
            return

        except (HTTPError, Timeout, ConnectionError) as e:
            code = e.response.status_code if isinstance(e, HTTPError) else None
            if code in retry_codes:
                wait_time = 2 ** attempt
                logger.warning(f"Erro {code}. Tentando novamente em {wait_time} segundos.")
                time.sleep(wait_time)
                continue
            logger.error(f"Erro {code}. Requisição falhou.")
            raise

        except RequestException as e:
            logger.error(f"Erro ao enviar relatório: {e}")
            raise

        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            raise


if __name__ == "__main__":
    users = getUsers()
    for user in users:
        print(user)
        total_chars = 0
        post = getPosts(user['id'])
        for p in post:
            total_chars += len(p['body'])
            print(p)
        print(f"Número total de caracteres: {total_chars}.\nNúmero de posts: {len(post)}.\nMédia de caracteres feitos por post: {charAverage(post)}.\n")
        print(f"------------------------------------------------------------------------------------------------")

    generateReport()
    postReport()
