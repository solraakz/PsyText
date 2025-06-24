# PsyText - Análise de Texto

![PsyText Logo/Screenshot](https://via.placeholder.com/600x300?text=PsyText+Screenshot)
*(Substitua esta imagem por uma captura de ecrã da sua aplicação)*

PsyText é uma aplicação para computador, feita em Python, que analisa textos. Ajuda a perceber o sentimento (emoções) e outras características do que escreve, criando relatórios em HTML, gráficos e dados que pode guardar.

## O que o PsyText faz?

*   **Análise de Sentimento:** Diz se as frases são positivas, negativas ou neutras. Usa um sistema chamado VADER, que foi melhorado para entender melhor textos mais complexos ou com ironia.
*   **Métricas do Texto:** Conta palavras, vê a média de palavras por frase, e mede a riqueza do vocabulário e a facilidade de leitura do texto.
*   **Contagem de Emoções e Pronomes:** Encontra e conta palavras ligadas a emoções (como alegria, tristeza) e diferentes tipos de pronomes.
*   **Relatórios Visuais:**
    *   **HTML Colorido:** Cria um ficheiro HTML onde cada frase do seu texto aparece com uma cor diferente, conforme o sentimento.
    *   **Gráficos:** Faz gráficos como o "Affect Grid" (mostra sentimento e intensidade emocional) e a "Trajetória de Sentimento" (como o sentimento muda ao longo do texto).
*   **Guarda Dados:** Permite guardar os resultados da análise em ficheiros JSON e CSV.
*   **Fácil de Usar:** Tem uma janela simples onde pode carregar ficheiros de texto ou escrever o seu próprio texto para analisar.

## Tecnologias Usadas

*   **Python 3.x:** A linguagem de programação principal.
*   **NLTK:** Para a análise de sentimento (VADER) e para dividir o texto.
*   **Textstat:** Para calcular a legibilidade do texto.
*   **Matplotlib e Pandas:** Para criar e gerir os gráficos.
*   **Jinja2:** Para criar os relatórios HTML.
*   **Tkinter:** Para a interface da aplicação.
*   **Pillow:** Para mostrar imagens na interface.

## Como Instalar

1.  **Obtenha o código:**
    ```bash
    git clone https://github.com/seu-usuario/psytext.git # Mude para o seu link
    cd psytext
    ```
2.  **Prepare o ambiente (recomendado):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # No Linux/macOS
    # venv\Scripts\activate   # No Windows (PowerShell)
    ```
3.  **Instale o que precisa:**
    ```bash
    pip install nltk matplotlib pandas jinja2 textstat Pillow
    ```
4.  **Recursos do NLTK:**
    O PsyText vai descarregar automaticamente o que precisa do NLTK na primeira vez que correr. Se quiser, pode descarregar manualmente:
    ```python
    import nltk
    nltk.download('punkt')
    nltk.download('vader_lexicon')
    ```

## Como Usar

1.  **Inicie a aplicação:**
    ```bash
    python interface.py
    ```
2.  **Na janela do PsyText:**
    *   **Escolha um ficheiro:** Clique em "Choose input file..." e selecione um `.txt`.
    *   **Ou escreva texto:** Clique em "Inserir manual text" para digitar ou colar o seu texto.
    *   **Analisar:** Clique em "Analyze Emotions" para ver o relatório HTML e as estatísticas.
    *   **Ver Gráficos:** Use os botões para "Output Affect Grid Graph" e "Sentiment Trajectory".
    *   **Exportar:** Clique em "Export Stats to CSV" para guardar os dados.
    *   Todos os resultados são guardados na pasta `output/`.