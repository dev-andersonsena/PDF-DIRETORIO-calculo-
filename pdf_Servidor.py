import os
import yaml
from datetime import datetime, timedelta
from PyPDF2 import PdfReader

def contar_paginas_pdf(diretorio, diretorio_saida, periodo_inicial, periodo_final, diretorio_saida_log):
    # Converter os períodos inicial e final para o formato datetime
    periodo_inicial_dt = datetime.strptime(periodo_inicial, "%d/%m/%Y")
    periodo_final_dt = datetime.strptime(periodo_final, "%d/%m/%Y")

    # Registro de início do processamento geral
    data_inicio_processamento = datetime.now().strftime("%H:%M:%S")
    data_inicio_processamento2 = datetime.now().strftime("%Y/%m/%d")

    
    registrar_inicio_fim_log( data_inicio_processamento, f'Inicio do processamento  {data_inicio_processamento2}', diretorio_saida, diretorio_saida_log)

    # Loop para cada dia dentro do período especificado
    while periodo_inicial_dt <= periodo_final_dt:
        # Definir o dia atual como período inicial
        dia_atual = periodo_inicial_dt.strftime("%Y/%m/%d")
        # Definir o período final como o mesmo dia
        periodo_final_atual = periodo_inicial_dt.strftime("%Y/%m/%d")

        # Lista todos os arquivos no diretório
        arquivos = os.listdir(diretorio)

        # Filtra apenas os arquivos PDF
        arquivos_pdf = [arq for arq in arquivos if arq.lower().endswith('.pdf')]

        # Organiza os arquivos pela data de criação
        arquivos_pdf = sorted(arquivos_pdf, key=lambda arq: os.path.getctime(os.path.join(diretorio, arq)))

        # Para cada arquivo PDF, conta o número de páginas e verifica o período de criação
        for arquivo in arquivos_pdf:
            caminho_arquivo = os.path.join(diretorio, arquivo)
            data_criacao_arquivo = datetime.fromtimestamp(os.path.getctime(caminho_arquivo))

            # Verifica se a data de criação do arquivo está dentro do período especificado
            if data_criacao_arquivo.date() == periodo_inicial_dt.date():
                with open(caminho_arquivo, 'rb') as f:
                    try:
                        # Obtenha a data e hora de processamento do arquivo
                        data_hora_processamento = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        num_paginas = contar_paginas(caminho_arquivo)
                        ano_pdf = data_criacao_arquivo.year
                        nome_arquivo_log = f'rep_pdf_{dia_atual.replace("/", "")}.csv'
                        registrar_em_log(arquivo, num_paginas, data_hora_processamento, caminho_arquivo, ano_pdf, diretorio_saida, nome_arquivo_log)
                    except Exception as e:
                        registrar_erro_log(arquivo, f'Erro ao processar o arquivo: {str(e)}', diretorio_saida)

        # Avançar para o próximo dia
        periodo_inicial_dt += timedelta(days=1)

    # Registro de fim do processamento geral
    data_fim_processamento = datetime.now().strftime("%H:%M:%S")
    
    registrar_inicio_fim_log(data_fim_processamento, f'Fim do processamento {data_inicio_processamento2}', diretorio_saida, diretorio_saida_log)
    
def registrar_inicio_fim_log(mensagem, data_hora, diretorio_saida, diretorio_saida_log):
    # Verificar se o diretório de saída existe, se não, criar
    if not os.path.exists(diretorio_saida_log):
        os.makedirs(diretorio_saida_log)

    # Corrigir o nome do arquivo de log para log_repPdf.log
    nome_arquivo_log = 'log_repPdf.log'

    # Abrir o arquivo de log para escrita no diretório_saida_log
    with open(os.path.join(diretorio_saida_log, nome_arquivo_log), 'a') as log_file:
        log_file.write(f"{mensagem} {data_hora}\n")

def registrar_erro_log(nome_arquivo, erro, diretorio_saida):
    if not os.path.exists(diretorio_saida):
        os.makedirs(diretorio_saida)
    with open(os.path.join(diretorio_saida, 'log_pdf.log'), 'a') as log_file:
        log_file.write(f"Erro ao processar o arquivo '{nome_arquivo}': {erro}\n")

def contar_paginas(caminho_arquivo):
    with open(caminho_arquivo, 'rb') as f:
        reader = PdfReader(f)
        return len(reader.pages) 

def registrar_em_log(nome_arquivo, num_paginas, data_hora_processamento, caminho_arquivo=None, ano_pdf=None, diretorio_saida=None, nome_arquivo_log=None):
    if diretorio_saida is None:
        print("O diretório de saída não está especificado no paramfile.yaml")
        return

    with open(os.path.join(diretorio_saida, nome_arquivo_log), 'a') as log_file:
        if nome_arquivo:
            if caminho_arquivo is not None:
                data_criacao = datetime.fromtimestamp(os.path.getctime(caminho_arquivo)).strftime("%d/%m/%Y")
            else:
                data_criacao = ''
            log_file.write(f'NOME_ARQUIVO; NUM_PAG \n')
            log_file.write(f'{nome_arquivo};{num_paginas}\n') # {data_criacao} 

def ler_parametros(paramfile):
    with open(paramfile, 'r') as file:
        parametros = yaml.safe_load(file)
    return parametros

def executar_tarefa():
    parametros = ler_parametros('paramfile.yaml')
    diretorio = parametros['diretorio']
    diretorio_saida = parametros['diretorio_saida']
    diretorio_saida_log = parametros['diretorio_saida_log']
    periodo_inicial = '01/01/2024'  # Defina o período inicial desejado
    periodo_final = '30/03/2024'  # Defina o período final desejado

    # Verifica se o diretório de saída não é None
    if diretorio_saida is not None:
        contar_paginas_pdf(diretorio, diretorio_saida, periodo_inicial, periodo_final, diretorio_saida_log)
    else:
        print("O diretório de saída não está definido no arquivo YAML.")

if __name__ == "__main__":
    # Executar a tarefa manualmente
    executar_tarefa()
