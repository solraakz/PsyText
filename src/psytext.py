# este módulo tem as funções para análise de sentimento de texto em português,
# incluindo a geração de um html com frases coloridas de acordo com o sentimento,
# um gráfico de "affect grid" (valence vs arousal) e a exportação dos dados da análise para json

# imports locais
from defaults import paths as ph, english as st  # Importa configurações de caminhos do ficheiro defaults.py

# bibliotecas gerais
import os  # Para operações de sistema de ficheiros, como criar diretórios e manipular caminhos
import webbrowser  # Para abrir o ficheiro HTML no navegador
import json  # Para trabalhar com dados em formato JSON (exportação)
import nltk  # Natural Language Toolkit para processamento de linguagem natural (PLN)
import matplotlib.pyplot as plt  # Para gerar gráficos (affect grid)
import pandas as pd  # Para manipulação de dados, especialmente para o affect grid
from nltk.sentiment import SentimentIntensityAnalyzer  # Analisador de sentimento VADER do NLTK
from nltk.tokenize import word_tokenize # Para tokenização de palavras
import jinja2 # Para templating HTML
from nltk.downloader import Downloader # verifica e descarregar coisas do nltk
import textstat # Para cálculo de métricas de legibilidade

# recursos do nltk que são precisos
# Ver se o léxico vader já foi descarregado; se não, descarrega-o. isto evita estar sempre a descarregar o e mostrar mensagens chatas
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
    print("NLTK: vader_lexicon found.")
except nltk.downloader.DownloadError:
    print("NLTK: vader_lexicon not found. Downloading...")
    nltk.download('vader_lexicon', quiet=True) # quiet=True para suprimir output excessivo

try:
    nltk.data.find('tokenizers/punkt')
    print("NLTK: punkt tokenizer found.")
except nltk.downloader.DownloadError:
    print("NLTK: punkt tokenizer not found. Downloading...")
    nltk.download('punkt', quiet=True)

# personalização do VADER (replacements/substituições) por causa de nuances e cínica mal-interpretados
custom_vader_lexicon = {
    # O VADER classifica isto erradamente como positivo devido a "success" e "better"
    "success": 0.5,  # Reduzir positividade padrão (2.8)
    "better": 0.5,   # Reduzir positividade padrão (2.9)
    "cheat": -3.0,   # Enfatizar negatividade (padrão -1.6)
    "lie": -3.0,     # Enfatizar negatividade (padrão -1.8)
    "pretend": -1.5, # Tornar 'pretend' negativo (padrão 0.0)

    # O VADER não capta a negação forte ou a desesperança geral
    "stopped": -2.5, # Tornar 'stopped' fortemente negativo, especialmente quando implica a cessação de coisas positivas
    "hoping": 0.5,   # Reduzir positividade de 'hoping' (padrão 1.9)
    "good": 0.5,     # Reduzir positividade de 'good' (padrão 1.9)
    "smiled": 0.0,   # Tornar 'smiled' neutro para que negações como "can't remember smiling" não sejam positivas
    "can't": -2.0,   # Tornar "can't" explicitamente muito negativo
    "cannot": -2.0,  # Tornar "cannot" explicitamente muito negativo
    "fight": -0.5,   # Reduzir negatividade padrão de 'fight' (-1.5) para lidar melhor com contextos como "fight for you"

    # Outras palavras do texto extremamente negativo que o VADER pode não pontuar com força suficiente
    "pointless": -3.0,      # Tornar 'pointless' muito mais negativo (padrão -1.9)
    "disconnected": -2.0,   # Tornar 'disconnected' mais forte negativo (padrão -1.0)
    "heavier": -1.0,        # Adicionar 'heavier' como negativo
    "disappointment": -3.0, # Tornar mais forte (padrão -2.5)
    "failure": -3.0,        # Tornar mais forte (padrão -2.2)
    "emptiness": -3.0,      # Tornar mais forte (padrão -2.0)
    "broken": -3.0,         # Tornar mais forte (padrão -2.0)
    "dead end": -3.5,       # Adicionar "dead end" como muito negativo
    "nothing": -1.0,        # Tornar "nothing" explicitamente negativo
}

print("Initializing SentimentIntensityAnalyzer...")
sia = SentimentIntensityAnalyzer() # Initialize VADER with the default lexicon
print("Updating VADER lexicon with custom scores...")
sia.lexicon.update(custom_vader_lexicon) # Update the lexicon with custom values

def cor_por_sentimento(pontuacao):
    """
    determina a cor com base na pontuação de sentimento (o compound score)

    Args:
        pontuacao (float): a pontuação de sentimento (geralmente entre -1 e 1)

    Returns:
        str: o nome da cor (ex: "darkgreen", "red", "orange")
    """
    if pontuacao >= 0.5:
        return "darkgreen"     # muito positivo
    elif pontuacao >= 0.2:
        return "green"         # positivo
    elif pontuacao >= 0.1:
        return "lightgreen"    # um pouco positivo
    elif pontuacao <= -0.5:
        return "darkred"       # muito negativo
    elif pontuacao <= -0.2:
        return "red"           # negativo
    elif pontuacao <= -0.1:
        return "lightcoral"    # um pouco negativo
    else:
        return "orange"        # neutro

def calcular_arousal(pontuacoes):
    """
    calcula uma estimativa simples de arousal (excitação/intensidade emocional)
    é baseado na amplitude entre as pontuações de sentimento positivo, negativo e neutro,
    excluindo a pontuação 'compound'

    Args:
        pontuacoes (dict): um dicionário com as pontuações de sentimento (neg, neu, pos, compound)

    Returns:
        float: o valor de arousal calculado
    """
    # exclui a pontuação 'compound' para calcular o arousal,
    # focando na variação entre as pontuações de sentimento positivo, negativo e neutro
    relevant_scores = {k: v for k, v in pontuacoes.items() if k != 'compound'}
    if not relevant_scores: # se por acaso não houver pontuações relevantes
        return 0
    return max(relevant_scores.values()) - min(relevant_scores.values())

def _analisar_frases(texto):
    """
    analisa cada frase do texto para sacar o sentimento, arousal e a cor
    esta é a função central de análise de frases para evitar repetição
    """
    frases = nltk.sent_tokenize(texto, language='english')
    frases_info = []
    for frase in frases:
        frase = frase.strip()
        if not frase:
            continue
        try:
            scores = sia.polarity_scores(frase)
            compound = scores['compound']
            arousal = calcular_arousal(scores)
            cor = cor_por_sentimento(compound)
            frases_info.append({
                "frase": frase,
                "valence": compound,
                "arousal": arousal,
                "cor": cor
            })
        except Exception as e:
            print(f"Error analyzing sentence: '{frase}'. Error: {str(e)}")
    return frases_info

def gerar_html_frases_coloridas(frases_info, output_path, estatisticas_gerais=None):
    """
    gera um ficheiro html com as frases do texto original coloridas de acordo com o seu sentimento

    Args:
        frases_info (list): lista de dicionários com os dados já analisados de cada frase
        output_path (str, optional): o caminho onde o ficheiro html será guardado
        estatisticas_gerais (dict, optional): dicionário com estatísticas gerais do texto
    """
    print(f"Starting HTML generation for output path: {output_path if output_path else 'default'}")

    # garante que a pasta de saída para o html existe
    output_dir_for_html = os.path.dirname(output_path)
    if output_dir_for_html: # vê se o dirname não está vazio (por exemplo, para não dar erro num ficheiro na raiz)
        os.makedirs(output_dir_for_html, exist_ok=True)
        print(f"Ensured output directory exists: {output_dir_for_html}")

    # configura o ambiente do jinja2 para carregar o template da pasta do script
    template_loader = jinja2.FileSystemLoader(searchpath=os.path.dirname(__file__))
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("template.html")

    # prepara os dados para o template
    context = {
        "frases_info": frases_info,
        "estatisticas_gerais": estatisticas_gerais,
        "st": st  # passa o dicionário de strings para o template
    }

    # renderiza o template com os dados
    html_output = template.render(context)

    try:
        # escreve o conteúdo html no ficheiro de saída
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_output)
        print(f"HTML successfully exported to: {output_path}")
    except Exception as e:
        print(f"Exception - error creating/writing HTML file at {output_path}: {str(e)}")

    print("Finished HTML generation.")

def gerar_affect_grid(frases_info, output_path):
    """
    Gera um gráfico "Affect Grid" (Valence vs. Arousal) e guarda-o como uma imagem.

    Args:
        frases_info (list): Lista de dicionários com informações das frases (requer 'valence', 'arousal', 'cor').
        output_path (str): Caminho onde a imagem do gráfico será guardada.
    """
    if not frases_info:
        print("Sem dados para gerar o Affect Grid.")
        return

    print(f'Attempting to generate Affect Grid to: {output_path}...')
    df = pd.DataFrame(frases_info)

    fig, ax = plt.subplots(figsize=(8, 8))  # Cria uma figura e um conjunto de subplots
    ax.axhline(0, color='black', lw=0.5)  # linha horizontal no eixo y=0
    ax.axvline(0, color='black', lw=0.5)  # linha vertical no eixo x=0
    # scatter plot: valence no x, arousal no y, e a cor baseada no sentimento
    ax.scatter(df["valence"], df["arousal"], c=df["cor"], alpha=0.6)

    ax.set_title("Affect Grid (Valence vs Arousal)")
    ax.set_xlabel("Valence (Negative <-> Positive)")
    ax.set_ylabel("Arousal (Passive <-> Active)")
    ax.grid(True)  # adiciona uma grelha ao gráfico

    try:
        # garante que a pasta de saída para o gráfico existe
        output_dir_for_grid = os.path.dirname(output_path) # saca o diretório do caminho de saída
        if output_dir_for_grid:
            os.makedirs(output_dir_for_grid, exist_ok=True)
            print(f"Ensured output directory for grid exists: {output_dir_for_grid}")
        fig.savefig(output_path)  # guarda a figura no caminho que foi dito
        print(f"Affect Grid saved to: {output_path}")
    except Exception as e:
        print(f"Exception - error saving Affect Grid to {output_path}: {str(e)}")
    finally:
        plt.close(fig)  # fecha a figura para libertar memória, o que é importante se for executado várias vezes

def exportar_json(frases_info, output_path):
    """
    Exporta as informações das frases analisadas para um ficheiro JSON.

    Args:
        frases_info (list): Lista de dicionários com informações das frases.
        output_path (str): Caminho onde o ficheiro JSON será guardado.
    """
    if not frases_info:
        print("Sem dados para exportar para JSON.")
        return

    print(f'Attempting to export JSON to: {output_path}...')
    try:
        # garante que o caminho existe
        output_dir_for_json = os.path.dirname(output_path)
        if output_dir_for_json:
            os.makedirs(output_dir_for_json, exist_ok=True)
            print(f"Ensured output directory for JSON exists: {output_dir_for_json}")
        # escreve no ficheiro json
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(frases_info, f, indent=4, ensure_ascii=False)
        print(f"JSON successfully exported to: {output_path}")
    except Exception as e:
        print(f"Error exporting JSON to {output_path}: {str(e)}")

def calcular_descritores_textuais(texto):
    """
    calcula descritores de texto básicos: contagem de palavras, média de palavras por frase e type-token ratio
    usa nltk.sent_tokenize para uma melhor contagem de frases

    Args:
        texto (str): O texto original.

    Returns:
        dict: Um dicionário com os descritores calculados.
    """
    print("A calcular descritores textuais...")
    try:
        # NLTK tentará usar 'portuguese'
        frases = nltk.sent_tokenize(texto, language='english')
        num_frases_nltk = len(frases)
        # aqui usou-se 'portuguese' como um "placeholder" dado que o nltk trata do idioma inglês por defeito se não houver recursos portugueses do punkt
        # a sua implementação não foi contiunuada no psytext portanto isto em específico foi deixado de lado
        palavras = nltk.word_tokenize(texto.lower(), language='english')
        # tira a pontuação da lista de palavras para as contagens serem mais certas
        palavras = [palavra for palavra in palavras if palavra.isalnum()]
        num_palavras = len(palavras)
        
        avg_palavras_frase = num_palavras / num_frases_nltk if num_frases_nltk > 0 else 0
        
        palavras_unicas = set(palavras)
        num_palavras_unicas = len(palavras_unicas)
        ttr = num_palavras_unicas / num_palavras if num_palavras > 0 else 0
        
        return {
            "total_palavras": num_palavras,
            "avg_palavras_frase": avg_palavras_frase,
            "ttr": ttr,
            "num_frases_nltk": num_frases_nltk # usado para os cálculos dos descritores serem consistentes
        }
    except Exception as e:
        print(f"Error calculating textual descriptors: {e}")
        return {"total_palavras": "N/A", "avg_palavras_frase": "N/A", "ttr": "N/A", "num_frases_nltk": "N/A"}

def calcular_legibilidade_flesch(texto):
    """calcula o flesch reading ease com a biblioteca textstat"""
    print("Calculating Flesch Reading Ease...")
    try:
        # nota: o textstat pode não ser 100% certo para português sem uma configuração de idioma específica
        # ou adaptação das regras de contagem de sílabas
        # para texto em inglês, deve ser certinho
        return textstat.flesch_reading_ease(texto)
    except Exception as e:
        print(f"Error calculating Flesch Reading Ease with textstat: {e}")
        return "N/A"

# def count_emotion_words(text, emotion_lexicons):
#     """
#     conta as palavras de emoção que aparecem no texto, com base nos léxicos
#
#     Args:
#         text (str): O texto de entrada.
#         emotion_lexicons (dict): Um dicionário onde as chaves são nomes de emoções
#                                  e os valores são listas de palavras para essa emoção.
#
#     Returns:
#         dict: Um dicionário com nomes de emoções como chaves e as suas contagens de palavras como valores.
#     """
#     print("Counting emotion words...")
#     emotion_counts = {emotion: 0 for emotion in emotion_lexicons}
#     try:
#         # outra vez o "placeholder"
#         words = word_tokenize(text.lower(), language='english')
#         for emotion, lexicon in emotion_lexicons.items():
#             for word in lexicon:
#                 emotion_counts[emotion] += words.count(word.lower())
#     except Exception as e:
#         print(f"Error counting emotion words: {e}")
#     return emotion_counts

def count_pronouns(text, pronoun_categories):
    """
    conta os pronomes que aparecem, com base nas categorias definidas

    Args:
        text (str): O texto de entrada.
        pronoun_categories (dict): Um dicionário onde as chaves são nomes de categorias de pronomes
                                   e os valores são listas de pronomes nessa categoria.

    Returns:
        dict: Um dicionário com nomes de categorias de pronomes como chaves e as suas contagens como valores.
    """
    print("Counting pronouns...")
    pronoun_counts = {category: 0 for category in pronoun_categories}
    try:
        
        words = word_tokenize(text.lower(), language='english')
        for category, pronouns_in_category in pronoun_categories.items():
            for pronoun in pronouns_in_category:
                pronoun_counts[category] += words.count(pronoun.lower()) # garante que o pronome no léxico também está em minúsculas
    except Exception as e:
        print(f"Error counting pronouns: {e}")
    return pronoun_counts

def generate_sentiment_trajectory_graph(frases_info, output_path):
    """
    gera um gráfico de linhas da trajetória do sentimento (a valência) ao longo das frases

    Args:
        frases_info (list): Lista de dicionários, cada um com uma chave 'valence'.
        output_path (str): Caminho para guardar a imagem do gráfico gerado.
    """
    print(f"Generating sentiment trajectory graph to: {output_path}")
    if not frases_info:
        print("No data for sentiment trajectory graph.")
        return
    
    valences = [info['valence'] for info in frases_info]
    sentence_indices = range(1, len(valences) + 1)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(sentence_indices, valences, marker='o', linestyle='-', color='b')
    ax.axhline(0, color='grey', lw=0.8, linestyle='--') # linha de referência no zero
    ax.set_title("Sentiment Trajectory Over Sentences")
    ax.set_xlabel("Sentence Index")
    ax.set_ylabel("Valence Score")
    ax.grid(True)
    
    try:
        output_dir_for_graph = os.path.dirname(output_path)
        if output_dir_for_graph:
            os.makedirs(output_dir_for_graph, exist_ok=True)
        fig.savefig(output_path)
        print(f"Sentiment trajectory graph saved to: {output_path}")
    except Exception as e:
        print(f"Error saving sentiment trajectory graph: {e}")
    finally:
        plt.close(fig)

def analisar_texto(texto, base_filename="analysis_default"):
    """
    faz uma análise completa do texto: gera html colorido, affect grid e ficheiro json,
    os ficheiros de saída são guardados na pasta definida em `ph["output_dir"]`
    com nomes baseados em `base_filename` e sufixos de `ph`

    Args:
        texto (str): O texto em português a ser analisado.
        base_filename (str, optional): O nome base para os ficheiros de saída.
                                       Defaults to "analysis_default".

    Returns:
        tuple: (caminho_html, estatisticas) ou (None, None) se a geração falhar.
               estatisticas é um dicionário com as métricas agregadas do texto.
               frases_info_completas é a lista detalhada de informações de cada frase.
    """
    print(f"Starting full text analysis for base filename: {base_filename}...")
    output_dir = ph["output_dir"] # pasta de saída principal
    os.makedirs(output_dir, exist_ok=True)  # garante que a pasta de saída principal existe

    trajectory_graph_suffix = "_sentiment_trajectory.png" # define o sufixo para o gráfico da trajetória
    # constrói os caminhos completos para os ficheiros de saída
    html_out_path = os.path.join(output_dir, f"{base_filename}{ph['html_suffix']}")

    # 1. analisa as frases do texto só uma vez
    frases_info_completas = _analisar_frases(texto)

    print("Calculating Aggregate Statistics...")
    # inicializa o dicionário das estatísticas
    estatisticas = {"num_frases": 0, "media_valencia": 0.0, "media_arousal": 0.0,
                    "perc_positivas": 0.0, "perc_negativas": 0.0, "perc_neutras": 0.0,
                    "cont_positivas": 0, "cont_negativas": 0, "cont_neutras": 0}
    
    # 2. calcula as estatísticas a partir dos dados que já foram analisados
    if frases_info_completas:
        estatisticas["num_frases"] = len(frases_info_completas)
        if estatisticas["num_frases"] > 0:
            # mudei o nome para 'media_valencia' para ser consistente com o que o html espera
            estatisticas["media_valencia"] = sum(f['valence'] for f in frases_info_completas) / estatisticas["num_frases"]
            estatisticas["media_arousal"] = sum(f['arousal'] for f in frases_info_completas) / estatisticas["num_frases"]
        else: # para evitar a divisão por zero se não houver frases válidas
            estatisticas["media_valencia"] = 0.0
            estatisticas["media_arousal"] = 0.0
        estatisticas["cont_positivas"] = sum(1 for f in frases_info_completas if f['valence'] >= 0.05)
        estatisticas["cont_negativas"] = sum(1 for f in frases_info_completas if f['valence'] <= -0.05)
        estatisticas["cont_neutras"] = estatisticas["num_frases"] - estatisticas["cont_positivas"] - estatisticas["cont_negativas"]
        if estatisticas["num_frases"] > 0:
            estatisticas["perc_positivas"] = (estatisticas["cont_positivas"] / estatisticas["num_frases"]) * 100
            estatisticas["perc_negativas"] = (estatisticas["cont_negativas"] / estatisticas["num_frases"]) * 100
            estatisticas["perc_neutras"] = (estatisticas["cont_neutras"] / estatisticas["num_frases"]) * 100

    # calcula os descritores do texto e a legibilidade
    estatisticas.update(calcular_descritores_textuais(texto))
    estatisticas['flesch_reading_ease'] = calcular_legibilidade_flesch(texto)

    # calcula e adiciona as contagens de emoções e pronomes
    # garante que estes léxicos estão definidos no defaults.py e que foram importados
    from defaults import pronoun_categories_en # garante que estes são importados
    # estatisticas['emotion_counts'] = count_emotion_words(texto, emotion_lexicons_en) # Comentado para desativar a contagem de emoções
    estatisticas['pronoun_counts'] = count_pronouns(texto, pronoun_categories_en)

    # 3. gera o html a partir dos dados que já foram analisados
    gerar_html_frases_coloridas(frases_info_completas, output_path=html_out_path, estatisticas_gerais=estatisticas)
    
    if frases_info_completas:  # só continua se a geração do html (e das frases_info_completas) correr bem
        # constrói aqui os caminhos para os outros ficheiros de saída
        grid_out_path = os.path.join(output_dir, f"{base_filename}{ph['affect_grid_suffix']}")
        json_out_path = os.path.join(output_dir, f"{base_filename}{ph.get('json_suffix', '_analysis.json')}")

        # 4. gera os outros outputs
        gerar_affect_grid(frases_info_completas, output_path=grid_out_path)
        exportar_json(frases_info_completas, output_path=json_out_path)
        print(f"Full text analysis completed for {base_filename}.")
        return html_out_path, estatisticas, frases_info_completas
    print(f"Full text analysis failed or produced no data for {base_filename}.")
    return None, None, None



# condição principal
if __name__ == "__main__":
    try:
        input_file_path = "message.txt"  # ficheiro de exemplo para testar
        # tira a extensão do nome do ficheiro para usar como base_filename
        base_name = os.path.splitext(os.path.basename(input_file_path))[0]

        print(f"Running psytext.py as main script with input file: {input_file_path}")
        with open(input_file_path, "r", encoding="utf-8") as f:
            texto = f.read()
            print(f"Read {len(texto)} characters from {input_file_path}")

        # faz a análise completa do texto do ficheiro
        generated_html_file, stats, _ = analisar_texto(texto, base_filename=base_name) # ignora o frases_info_completas aqui

        # se o ficheiro html foi gerado bem, abre-o no browser
        if generated_html_file and os.path.exists(generated_html_file):
            print(f"Opening generated HTML in browser: {generated_html_file}")
            webbrowser.open(f"file://{os.path.abspath(generated_html_file)}") # o file:// é para o browser o abrir bem
        else:
            print(f"Output HTML file not found or not generated.")
    except FileNotFoundError:
        print(f"Input file '{input_file_path}' not found.")
    except Exception as e:
        # apanha qualquer outra exceção que possa acontecer durante a execução principal
        print(f"An error occurred in the main execution of psytext.py: {str(e)}")
