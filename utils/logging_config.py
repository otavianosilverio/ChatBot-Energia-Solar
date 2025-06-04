import logging

def get_logger():
    # Criação de logger personalizado
    logger = logging.getLogger("meu_chatbot")
    logger.setLevel(logging.DEBUG)  # Aceita tudo de DEBUG até CRITICAL

    # Handler para gravar em arquivo
    file_handler = logging.FileHandler("Logs.log")
    file_handler.setLevel(logging.DEBUG)  

    # Formatação dos logs
    formatter = logging.Formatter(
        "%(asctime)s::%(levelname)s::%(filename)s::%(lineno)d::%(message)s"
    )
    file_handler.setFormatter(formatter)

    # Adiciona o handler ao logger
    logger.addHandler(file_handler)

    return logger