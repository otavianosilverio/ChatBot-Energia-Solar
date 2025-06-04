from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from utils.logging_config import get_logger
import openai, json, os, requests

# Inicializando o logger com as configurações do logging_config.py.
logger = get_logger()
logger.info("Servidor iniciado")

# Carregar variáveis do arquivo .env
load_dotenv()

# Carregando variáveis de ambiente do arquivo .env.
openai.api_key = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

# Criando a aplicação no Flask e habilitando CORS(Para requisições externas, como Postman/Wordpress)
app = Flask(__name__)
CORS(app)
logger.info("Aplicação iniciada...")

# Inicializa a variável global que irá armazenar o id da thread
thread_id_global = None
logger.info("Thread Global iniciada")

# Mapa para associar chat_id do Telegram a thread_id do OpenAI
thread_map = {}


@app.route('/')
def home():
    return "Backend do Chatbot rodando no Azure!"

# Difine a rota para o método post
@app.route('/chat', methods=['POST'])

# Função chat para atender a requisição
def chat():
    global thread_id_global  # Para acessar e modificar a variável global
    data = request.get_json() # Lendo o valor da chave 'pergunta'
    pergunta = data.get('pergunta') 
    logger.info("Pergunta recebida: %s", pergunta)

    try:
        if thread_id_global is None: # É executado se ainda não existe uma thread_id_global
            thread = openai.beta.threads.create()
            thread_id_global = thread.id
            logger.info("Nova thread criada: %s", thread_id_global)
        else: # Se já existe thread ela é reutilizada
            # Utiliza o mesmo thread_id
            thread = openai.beta.threads.retrieve(thread_id_global)
            logger.info("Thread reutilizada: %s", thread_id_global)
        
        # Adiciona a mensagem do usuário como uma nova mensagem
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=pergunta
        )
        logger.info("Pergunta enviada")

        # Inicia execução do Assistente GPT associado à thread.
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        logger.info("Aguardando Resposta")
        # Aguardando a execução terminar
        while True:
            run_status = openai.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == 'completed':
                break

        # Buscando resposta final
        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        resposta_json = messages.data[0].content[0].text.value
        logger.info("Resposta bruta recebida: %s", resposta_json)

        # Conversão para JSON válido
        try:
            resposta_formatada = json.loads(resposta_json)  # Se veio JSON serializado
        except:
            resposta_formatada = {"resposta": resposta_json}  # Se veio como texto

        #logger.info("Resposta formatada: %s", resposta_formatada)
        return jsonify(resposta_formatada)

    # Tratando exceções 
    except Exception as e:
        print("Erro:", str(e))
        return jsonify({"erro": str(e)}), 500

# Inicia aplicação
if __name__ == '__main__':
    app.run(debug=True)
    
