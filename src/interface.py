# bibliotecas locais
from defaults import default_title as dtitle, english as st, paths as ph
import psytext

# Bibliotecas gerais
import os, webbrowser, tkinter as tk, csv
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from PIL import Image, ImageTk # PIL/pillow melhor manuseamento de imagens
import pandas as pd

class App:
    """
    classe principal da aplicação de interface gráfica (gui) para o psicoanalisador
    permite ao utilizador escolher um ficheiro de texto ou inserir texto manualmente,
    gerar uma visualização html das emoções e um gráfico "affect grid"
    """
    def __init__(self, root):
        """
        inicializa a janela principal da aplicação e os seus componentes

        Args:
            root (tk.Tk): o widget raiz do tkinter para a aplicação
        """
        print("Initializing App GUI...")
        self.root = root
        self.root.title(dtitle) # definir título da janela a partir de defaults
        self.initial_width = 700
        self.initial_height = 750 # altura aumentada para uma melhor vista inicial
        self.center_window(self.initial_width, self.initial_height)

        self.frases_info = None
        self.file_path = None
        self.canvas_grid = None # isto era para um gráfico embutido, mas agora os gráficos estão em janelas toplevel
        self.current_stats_data = None # para guardar as estatísticas da análise mais recente

        print("Setting up GUI layout...")
        self.root.resizable(True, True) # x e y
        self.root.minsize(550, 500) # tamanho mínimo

        # layout da interface. strings vazias são fontes do sistema
        label_title = tk.Label(root, text=dtitle, font=("", 80, "bold"))
        label_title.pack(pady=(10, 5))

        # esta label mostra o nome do ficheiro que foi escolhido
        self.label_arquivo = tk.Label(root, text=st['no_file'])
        self.label_arquivo.pack(padx=10, pady=5)

        # esta frame agrupa os botões de ação principais, e tem sub-frames lá dentro
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5) # padding vertical para a zona dos botões

        ### PRIMEIRA COLUNA ###
        row1_buttons_frame = tk.Frame(btn_frame)
        row1_buttons_frame.pack()

        # botão para escolher um ficheiro de input
        btn_abrir = tk.Button(row1_buttons_frame, text=st['choose_input'], command=self.escolher_ficheiro)
        btn_abrir.pack(side=tk.LEFT, padx=5, pady=2) # pady mais pequeno para os botões que estão nas linhas

        # botão para gerar o html com emoções coloridas
        btn_html = tk.Button(row1_buttons_frame, text=st['colors_to_html'], command=self.gerar_html)
        btn_html.pack(side=tk.LEFT, padx=5, pady=2)

        # botão para gerar o gráfico affect grid (mantido)
        btn_grid = tk.Button(row1_buttons_frame, text=st['to_affect_grid'], command=self.gerar_grid)
        btn_grid.pack(side=tk.LEFT, padx=5, pady=2)
        
        ### SEGUNDA COLUNA ###
        row2_buttons_frame = tk.Frame(btn_frame)
        row2_buttons_frame.pack()

        # botão para gerar o gráfico de trajetória de sentimento
        btn_trajectory = tk.Button(row2_buttons_frame, text=st['sentiment_trajectory_btn'], command=self.gerar_trajetoria_sentimento)
        btn_trajectory.pack(side=tk.LEFT, padx=5, pady=2)

        # botão para exportar estatísticas para csv
        btn_export_csv = tk.Button(row2_buttons_frame, text=st['export_csv_btn'], command=self.exportar_stats_csv)
        btn_export_csv.pack(side=tk.LEFT, padx=5, pady=2)

        # botão para abrir uma janela de inserção manual de texto
        btn_manual_popup = tk.Button(root, text=st['manual_analysis'], command=self.abrir_janela_manual)
        btn_manual_popup.pack(pady=10)

        ### FRAME DE ESTATÍSTICAS ###
        stats_outer_frame = tk.LabelFrame(root, text=st['stats_title'], padx=5, pady=5)
        stats_outer_frame.pack(padx=10, pady=10, fill="both", expand=True) # permitir que este frame se expanda

        # canvas que dá para fazer scroll
        stats_canvas = tk.Canvas(stats_outer_frame)
        stats_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # a scrollbar
        stats_scrollbar = tk.Scrollbar(stats_outer_frame, orient=tk.VERTICAL, command=stats_canvas.yview)
        stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        stats_canvas.configure(yscrollcommand=stats_scrollbar.set)

        # esta frame tem as estatísticas todas e dá para fazer scroll
        self.scrollable_inner_stats_frame = tk.Frame(stats_canvas)
        stats_canvas.create_window((0, 0), window=self.scrollable_inner_stats_frame, anchor="nw")

        ### scrollable_inner_stats_frame ###
        self.label_num_frases = tk.Label(self.scrollable_inner_stats_frame, text=f"{st['stats_num_sentences']} -")
        self.label_num_frases.pack(anchor="w")
        self.label_avg_valence = tk.Label(self.scrollable_inner_stats_frame, text=f"{st['stats_avg_valence']} -")
        self.label_avg_valence.pack(anchor="w")
        self.label_avg_arousal = tk.Label(self.scrollable_inner_stats_frame, text=f"{st['stats_avg_arousal']} -")
        self.label_avg_arousal.pack(anchor="w")
        self.label_perc_pos = tk.Label(self.scrollable_inner_stats_frame, text=f"{st['stats_perc_positive']} -")
        self.label_perc_pos.pack(anchor="w")
        self.label_perc_neg = tk.Label(self.scrollable_inner_stats_frame, text=f"{st['stats_perc_negative']} -")
        self.label_perc_neg.pack(anchor="w")
        self.label_perc_neu = tk.Label(self.scrollable_inner_stats_frame, text=f"{st['stats_perc_neutral']} -")
        self.label_perc_neu.pack(anchor="w")
        # descritores e legibilidade
        self.label_total_words = tk.Label(self.scrollable_inner_stats_frame, text=f"{st['stats_total_words']} -")
        self.label_total_words.pack(anchor="w")
        self.label_avg_words_sentence = tk.Label(self.scrollable_inner_stats_frame, text=f"{st['stats_avg_words_sentence']} -")
        self.label_avg_words_sentence.pack(anchor="w")
        self.label_ttr = tk.Label(self.scrollable_inner_stats_frame, text=f"{st['stats_ttr']} -")
        self.label_ttr.pack(anchor="w")
        self.label_flesch = tk.Label(self.scrollable_inner_stats_frame, text=f"{st['stats_flesch_ease']} -")
        self.label_flesch.pack(anchor="w")
        
        # contagem de emoções (labels dinâmicos)
        # self.emotion_labels_frame = tk.LabelFrame(self.scrollable_inner_stats_frame, text=st.get('stats_emotion_counts_title', 'Emotion Word Counts:'), padx=5, pady=5) # Comentado para desativar a contagem de emoções
        # self.emotion_labels_frame.pack(anchor="w", fill="x", pady=(5,0)) # Comentado para desativar a contagem de emoções
        # self.emotion_labels = {} # para guardar os labels de emoção # Comentado para desativar a contagem de emoções

        # contagem de pronomes (labels dinâmicos)
        self.pronoun_labels_frame = tk.LabelFrame(self.scrollable_inner_stats_frame, text=st.get('stats_pronoun_counts_title', 'Pronoun Counts:'), padx=5, pady=5)
        self.pronoun_labels_frame.pack(anchor="w", fill="x", pady=(5,0))
        self.pronoun_labels = {} # para guardar os labels de pronome

        # (este frame já não se usa para a affect grid porque agora abre numa janela à parte!!!!!)
        # self.frame_canvas = tk.Frame(root)
        # self.frame_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5) # comentado

        ### BOTÃO LIMPAR E LABEL ESTADO ###
        action_feedback_frame = tk.Frame(root)
        action_feedback_frame.pack(fill=tk.X, padx=10, pady=(5, 10))

        btn_clear = tk.Button(action_feedback_frame, text=st['clear_interface'], command=self.limpar_interface)
        btn_clear.pack(side=tk.LEFT, padx=(0,10))

        self.status_label = tk.Label(action_feedback_frame, text=st['status_ready'], bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # define o que fazer quando se fecha a janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        ### BARRA DE MENU ###
        menubar = tk.Menu(self.root)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label=st['menu_help_content'], command=self.mostrar_ajuda_info)
        helpmenu.add_separator()
        helpmenu.add_command(label=st['menu_about'], command=self.mostrar_sobre)
        menubar.add_cascade(label=st['menu_help'], menu=helpmenu)
        self.root.config(menu=menubar)

        # se o user carregar no f1, mostra a ajuda (mesmo já havendo o botão no menu)
        self.root.bind("<F1>", lambda event: self.mostrar_ajuda_info())

        # atualiza a scrollregion sempre que o frame de dentro muda de tamanho
        self.scrollable_inner_stats_frame.bind(
            "<Configure>",
            lambda e: stats_canvas.configure(scrollregion=stats_canvas.bbox("all"))
        )
        # também liga o redimensionamento do canvas para atualizar a largura do frame de dentro
        stats_canvas.bind(
            "<Configure>",
            lambda e: stats_canvas.itemconfig(stats_canvas.create_window((0,0), window=self.scrollable_inner_stats_frame, anchor='nw'), width=e.width)
        )
        # para ativar o scroll do rato na frame das estatísticas
        def _on_mousewheel(event):
            if event.num == 5 or event.delta < 0: # scroll para baixo
                stats_canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta > 0: # scroll para cima
                stats_canvas.yview_scroll(-1, "units")

        stats_canvas.bind_all("<MouseWheel>", _on_mousewheel) # windows e macos (+/- 120 por clique)
        stats_canvas.bind_all("<Button-4>", _on_mousewheel)   # linux scroll para cima
        stats_canvas.bind_all("<Button-5>", _on_mousewheel)   # linux scroll para baixo

        self.limpar_dados_analise() # inicializa os labels das estatísticas
        print("App GUI initialized.")

    def center_window(self, width, height):
        """
        centra a janela principal no ecrã
        """
        # print(f"Centering window with width={width}, height={height}") # demasiado "verbose" por isso fica comentado
        # garante que as dimensões da janela estão atualizadas
        self.root.update_idletasks()
        # calcula a posição x e y para centrar a janela
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        # define a geometria da janela
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def escolher_ficheiro(self):
        """
        abre uma caixa de diálogo para o user escolher um ficheiro de texto e atualiza o label com o caminho do ficheiro selecionado e redefine `frases_info`
        """
        print("Choosing input file...")
        caminho = filedialog.askopenfilename(
            filetypes=[(st['dialog_text_files'], "*.txt"), (st['dialog_all_files'], "*.*")]
        )
        if caminho:
            self.file_path = caminho
            self.label_arquivo.config(text=f"{st['file_to_open']}: {caminho}")
            print(f"File selected: {caminho}")
            self.status_label.config(text=f"{st['sel_file']} {os.path.basename(caminho)}")
            self.limpar_dados_analise() # limpa as análises e gráficos antigos


    def gerar_html(self):
        """
        gera o ficheiro html com as frases coloridas com base no ficheiro selecionado e pede confirmação para abrir no browser
        """
        print("Generate HTML button clicked.")
        if not self.file_path:
            messagebox.showwarning(st['warning'], st['please_file'])
            print("Warning: No file selected for HTML generation.")
            return
        
        self.status_label.config(text=st['status_analysing'])
        self.root.update_idletasks() # para forçar a atualização do label

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                print(f"Reading content from: {self.file_path}")
                texto = f.read()

            self.status_label.config(text=st['status_generating_html'])
            print("Calling psytext.analisar_texto for HTML generation...")
            self.root.update_idletasks()

            os.makedirs(ph["output_dir"], exist_ok=True) # o output existe? vamos garantir que sim
            filename = os.path.basename(self.file_path)

            # chama o 'psytext' para gerar o html e buscar as infos das frases
            output_html_path, stats_data, detailed_frases_info = psytext.analisar_texto(texto, base_filename=filename)

            if output_html_path and stats_data:
                self.current_stats_data = stats_data # para a exportação csv
                self.atualizar_labels_estatisticas(stats_data)
                self.frases_info = detailed_frases_info # atribui a lista detalhada para o grid
                self.status_label.config(text=f"{st['status_html_done']} {os.path.basename(output_html_path)}")
                print(f"HTML and stats generated. HTML at: {output_html_path}")
                if messagebox.askyesno(st['success'], f"{st['html_file']} {st['saved_to']}:\n{output_html_path}\n\n{st['open_browser_q']}"):
                    print(f"User chose to open HTML in browser: {output_html_path}")
                    webbrowser.open(f"file://{os.path.abspath(output_html_path)}")
            else:
                self.status_label.config(text=st['error'])
                print("Error: HTML/stats generation failed or returned no data.")
                messagebox.showerror(st['error'], f"{st['error']} {st['gen']} {st['html_file']}")

        except Exception as e:
            print(f"Exception during HTML generation: {str(e)}")
            messagebox.showerror(st['error'], f"{st['error']} {st['gen']} {st['html_file']}:\n{str(e)}")

    def _iniciar_analise(self, texto, base_filename, janela_manual=None):
        """
        método central para começar a análise do texto, seja de um ficheiro ou de entrada manual
        """
        self.status_label.config(text=st['status_analysing'])
        self.root.update_idletasks()
        try:
            os.makedirs(ph["output_dir"], exist_ok=True)
            
            self.status_label.config(text=st['status_generating_html'])
            self.root.update_idletasks()

            output_html_path, stats_data, detailed_frases_info = psytext.analisar_texto(texto, base_filename=base_filename)

            if output_html_path and stats_data:
                self.current_stats_data = stats_data
                self.atualizar_labels_estatisticas(stats_data)
                self.frases_info = detailed_frases_info
                self.status_label.config(text=f"{st['status_html_done']} {os.path.basename(output_html_path)}")
                print(f"Analysis complete. HTML at: {output_html_path}")
                if messagebox.askyesno(st['success'], f"{st['html_file']} {st['saved_to']}:\n{output_html_path}\n\n{st['open_browser_q']}"):
                    webbrowser.open(f"file://{os.path.abspath(output_html_path)}")
                if janela_manual:
                    janela_manual.destroy()
            else:
                self.status_label.config(text=st['error'])
                print("Error: Analysis failed or returned no data.")
                messagebox.showerror(st['error'], f"{st['error']} {st['gen']} {st['html_file']}")
        except Exception as e:
            print(f"Exception during text analysis: {str(e)}")
            self.status_label.config(text=st['error'])
            messagebox.showerror(st['error'], f"{st['error']} {st['gen']} {st['html_file']}:\n{str(e)}")


    def abrir_janela_manual(self):
        """
        abre uma janela nova para o user meter texto à mão e analisá-lo
        """
        janela = tk.Toplevel(self.root)
        janela.title(st['manual_analysis'])
        print("Opening manual text input window.")
        janela.geometry(f"+{janela.winfo_screenwidth() // 2 - janela.winfo_reqwidth() // 2}+{janela.winfo_screenheight() // 2 - janela.winfo_reqheight() // 2}") # para centrar

        tk.Label(janela, text=st['or_manual']).pack(pady=5)
        # campo de texto para inserir o texto à mão
        text_area = tk.Text(janela, height=10, width=60)
        text_area.pack(padx=10, pady=5)

        def analisar_texto():
            """
            esta função interna analisa o texto que foi metido na janela toplevel
            """
            texto = text_area.get("1.0", tk.END).strip()
            if not texto:
                print("Warning: No text entered for manual analysis.")
                messagebox.showwarning(st['warning'], st['please_text'])
                return
            
            self._iniciar_analise(texto, "manual_input", janela_manual=janela)

        btn_analisar = tk.Button(janela, text=st['colors_to_html'], command=analisar_texto)
        btn_analisar.pack(pady=10)


    def gerar_grid(self):
        """
        * gera e mostra o gráfico "affect grid" (valence vs. arousal) na interface
        * o gráfico também é guardado como uma imagem
        * requer que "self.frases_info" tenha sido preenchido antes, ou seja, através da função "gerar_html"
        """
        print("Generate Affect Grid button clicked.")
        if self.frases_info is None:
            messagebox.showwarning(st['warning'], st['please_file2'])
            print("Warning: No data (frases_info) available to generate Affect Grid.")
            return

        try:
            self.status_label.config(text=st['status_generating_grid'])
            self.root.update_idletasks()

            filename_base = os.path.basename(self.file_path) if self.file_path else "manual_input"
            output_img_path = os.path.join(ph["output_dir"], f"{filename_base}{ph['affect_grid_suffix']}")

            # 1. chama a função do psytext para criar e guardar o gráfico
            psytext.gerar_affect_grid(self.frases_info, output_img_path)
            # 2. usa o método auxiliar para mostrar a imagem que foi guardada
            self._mostrar_imagem_em_janela(output_img_path, f"Affect Grid ({filename_base})")
            self.status_label.config(text=f"{st['status_grid_done']} {os.path.basename(output_img_path)}")
        except Exception as e:
            print(f"Exception during Affect Grid generation: {str(e)}")
            self.status_label.config(text=st['error'])
            messagebox.showerror(st['error'], f"{st['error']} {st['gen']} {st['ag_file']}: \n{str(e)}")
    
    def atualizar_labels_estatisticas(self, stats_data):
        print(f"Updating statistics labels with data: {stats_data is not None}")
        """atualiza os labels da interface com as estatísticas do texto"""
        if stats_data:
            self.label_num_frases.config(text=f"{st['stats_num_sentences']} {stats_data.get('num_frases', '-')}")
            self.label_avg_valence.config(text=f"{st['stats_avg_valence']} {stats_data.get('media_valencia', 0.0):.2f}")
            self.label_avg_arousal.config(text=f"{st['stats_avg_arousal']} {stats_data.get('media_arousal', 0.0):.2f}")
            self.label_perc_pos.config(text=f"{st['stats_perc_positive']} {stats_data.get('perc_positivas', 0.0):.2f}% ({stats_data.get('cont_positivas', 0)})")
            self.label_perc_neg.config(text=f"{st['stats_perc_negative']} {stats_data.get('perc_negativas', 0.0):.2f}% ({stats_data.get('cont_negativas', 0)})")
            self.label_perc_neu.config(text=f"{st['stats_perc_neutral']} {stats_data.get('perc_neutras', 0.0):.2f}% ({stats_data.get('cont_neutras', 0)})")
            self.label_total_words.config(text=f"{st['stats_total_words']} {stats_data.get('total_palavras', '-')}")
            self.label_avg_words_sentence.config(text=f"{st['stats_avg_words_sentence']} {stats_data.get('avg_palavras_frase', 0.0):.2f}")
            self.label_ttr.config(text=f"{st['stats_ttr']} {stats_data.get('ttr', 0.0):.3f}")
            self.label_flesch.config(text=f"{st['stats_flesch_ease']} {stats_data.get('flesch_reading_ease', '-')}")

            # atualizar ou criar os labels da contagem de emoções
            # for widget in self.emotion_labels_frame.winfo_children(): # para limpar os anteriores # Comentado para desativar a contagem de emoções
            #     widget.destroy() # Comentado para desativar a contagem de emoções
            # self.emotion_labels = {} # Comentado para desativar a contagem de emoções
            # if 'emotion_counts' in stats_data: # Comentado para desativar a contagem de emoções
            #     for emotion, count in stats_data['emotion_counts'].items(): # Comentado para desativar a contagem de emoções
            #         display_emotion = emotion.replace("_", " ").capitalize() # Comentado para desativar a contagem de emoções
            #         label_text = f"{display_emotion}: {count}" # Comentado para desativar a contagem de emoções
            #         self.emotion_labels[emotion] = tk.Label(self.emotion_labels_frame, text=label_text) # Comentado para desativar a contagem de emoções
            #         self.emotion_labels[emotion].pack(anchor="w") # Comentado para desativar a contagem de emoções
            
            # atualizar ou criar os labels da contagem de pronomes
            for widget in self.pronoun_labels_frame.winfo_children(): # para limpar os anteriores
                widget.destroy()
            self.pronoun_labels = {}
            if 'pronoun_counts' in stats_data:
                for category, count in stats_data['pronoun_counts'].items():
                    display_category = category.replace("_", " ").capitalize()
                    label_text = f"{display_category}: {count}"
                    self.pronoun_labels[category] = tk.Label(self.pronoun_labels_frame, text=label_text)
                    self.pronoun_labels[category].pack(anchor="w")

        else: # ou então limpa os labels
            self.current_stats_data = None
            # for widget in self.emotion_labels_frame.winfo_children(): widget.destroy() # Comentado para desativar a contagem de emoções
            # self.emotion_labels = {} # Comentado para desativar a contagem de emoções
            for widget in self.pronoun_labels_frame.winfo_children(): widget.destroy()
            self.pronoun_labels = {}
            self.label_num_frases.config(text=f"{st['stats_num_sentences']} -")
            self.label_avg_valence.config(text=f"{st['stats_avg_valence']} -")
            self.label_avg_arousal.config(text=f"{st['stats_avg_arousal']} -")
            self.label_perc_pos.config(text=f"{st['stats_perc_positive']} -")
            self.label_perc_neg.config(text=f"{st['stats_perc_negative']} -")
            self.label_perc_neu.config(text=f"{st['stats_perc_neutral']} -")
            self.label_total_words.config(text=f"{st['stats_total_words']} -")
            self.label_avg_words_sentence.config(text=f"{st['stats_avg_words_sentence']} -")
            self.label_ttr.config(text=f"{st['stats_ttr']} -")
            self.label_flesch.config(text=f"{st['stats_flesch_ease']} -")

    def limpar_dados_analise(self):
        """limpa os dados da análise anterior (frases_info, estatísticas, gráfico)"""
        print("Clearing previous analysis data")
        # o self.current_stats_data é reiniciado pela função atualizar_labels_estatisticas(none)
        self.frases_info = None
        self.atualizar_labels_estatisticas(None) # limpa os labels de estatísticas
        # o self.canvas_grid era para o affect grid embutido, que agora está numa toplevel
        if self.canvas_grid: # se alguma vez se voltar a meter um canvas embutido
            self.canvas_grid.get_tk_widget().destroy()
            self.canvas_grid = None

    def on_closing(self):
        """
        o que fazer quando se fecha a janela principal e se encerra o python
        """
        print("Main window closing...")
        self.root.destroy()
        import sys
        sys.exit() # é uma forma um bocado súbita, mas é mais eficaz para o psytext
    
    def limpar_interface(self):
        """limpa a seleção do ficheiro, os dados da análise e o gráfico"""
        print("User clicked on clear button.\nClearing interface...")
        self.file_path = None
        self.label_arquivo.config(text=st['no_file'])
        self.limpar_dados_analise()
        self.status_label.config(text=st['status_cleared'])

    def mostrar_sobre(self):
        print("Showing 'About' window")
        """mostra a janela 'sobre'"""
        messagebox.showinfo(st['about_title'], st['about_content'])

    def mostrar_ajuda_info(self):
        print("Showing 'Help/Info' window.")
        """mostra a janela de ajuda/informações"""
        help_text = st['help_content']
        messagebox.showinfo(st['help_title'], help_text)
        
    def gerar_trajetoria_sentimento(self):
        """
        gera e mostra uma trajetória de sentimentos (sentiment trajectory) numa nova janela 'toplevel'
        """
        print("Generate Sentiment Trajectory button clicked.")
        if self.frases_info is None:
            messagebox.showwarning(st['warning'], st['please_file2']) # o user tem de gerar primeiro um html
            print("Warning: No data (frases_info) available to generate Sentiment Trajectory.")
            return

        try:
            self.status_label.config(text="Generating Sentiment Trajectory graph...")
            print("Generating Sentiment Trajectory graph...")
            self.root.update_idletasks()

            os.makedirs(ph["output_dir"], exist_ok=True)
            filename_base = os.path.basename(self.file_path) if self.file_path else "manual_input"
            output_img_path = os.path.join(ph["output_dir"], f"{filename_base}_sentiment_trajectory.png")

            # chama a função do psytext.py para gerar e guardar o gráfico
            # esta função vai criar a sua própria figura e fechá-la
            psytext.generate_sentiment_trajectory_graph(self.frases_info, output_img_path)

            self._mostrar_imagem_em_janela(output_img_path, f"Sentiment Trajectory ({filename_base})")
            self.status_label.config(text=f"Sentiment Trajectory graph saved: {os.path.basename(output_img_path)}")

        except Exception as e:
            print(f"Exception during Sentiment Trajectory generation: {str(e)}")
            self.status_label.config(text=st['error'])
            messagebox.showerror(st['error'], f"Error generating Sentiment Trajectory graph:\n{str(e)}")
    
    def _mostrar_imagem_em_janela(self, image_path, window_title):
        """mostra uma imagem guardada numa janela toplevel de tamanho fixo"""
        if not os.path.exists(image_path):
            print(f"Error: Image not found at {image_path}")
            messagebox.showerror(st['error'], f"Could not display graph. File not found:\n{image_path}")
            return

        window = tk.Toplevel(self.root)
        window.title(window_title)
        window.grab_set()
        window.focus_set()
        window.resizable(False, False) # impede que se mude o tamanho da janela

        try:
            # carrega a imagem com o pillow
            pil_image = Image.open(image_path)
            # converte para um formato que o tkinter percebe
            photo_image = ImageTk.PhotoImage(pil_image)

            # cria um label para ter a imagem
            image_label = tk.Label(window, image=photo_image)
            # guarda uma referência à imagem para o garbage collector não a apagar
            image_label.image = photo_image
            image_label.pack(padx=10, pady=10)
            print(f"Displaying graph in new Toplevel window from: {image_path}")
        except Exception as e:
            print(f"Error displaying image with Pillow: {e}")
            messagebox.showerror(st['error'], f"Could not display image:\n{e}")
            window.destroy()

    def exportar_stats_csv(self):
        """exporta as estatísticas gerais atuais para um ficheiro csv"""
        print("Export Stats to CSV button clicked.")
        if not self.current_stats_data:
            messagebox.showwarning(st['warning'], st['csv_no_data_warning'])
            print("Warning: No statistics data to export.")
            return

        filename_base = os.path.basename(self.file_path) if self.file_path else "manual_input"
        csv_filename = f"{filename_base}_statistics.csv"
        csv_path = os.path.join(ph["output_dir"], csv_filename)

        try:
            os.makedirs(ph["output_dir"], exist_ok=True)
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                # temos de lidar com dicionários dentro de outros, como o emotion_counts e o pronoun_counts
                flat_stats = {}
                for key, value in self.current_stats_data.items():
                    if isinstance(value, dict): # para lidar com emotion_counts e pronoun_counts
                        for sub_key, sub_value in value.items():
                            # cria uma chave mais descritiva para o cabeçalho do csv
                            flat_stats[f"{key.replace('_counts', '')}_{sub_key}"] = sub_value
                    else:
                        flat_stats[key] = value
                
                # usa as chaves do dicionário "achatado" como cabeçalhos
                if not flat_stats: # não deve acontecer se o self.current_stats_data existir
                    print("Error: No data to write to CSV after flattening.")
                    messagebox.showerror(st['csv_export_error_title'], "No data to write to CSV.")
                    return

                writer = csv.DictWriter(csvfile, fieldnames=flat_stats.keys())
                writer.writeheader()
                writer.writerow(flat_stats)
            
            print(f"Statistics successfully exported to CSV: {csv_path}")
            messagebox.showinfo(st['csv_export_success_title'], st['csv_export_success_message'].format(csv_path))
            self.status_label.config(text=f"Stats exported to: {csv_filename}")
        except Exception as e:
            print(f"Error exporting statistics to CSV: {str(e)}")
            messagebox.showerror(st['csv_export_error_title'], st['csv_export_error_message'].format(str(e)))
            self.status_label.config(text="Error exporting CSV.")

# condição principal (quando se abre e fecha a app)
if __name__ == "__main__":
    print(f"Welcome!")
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    print("Goodbye!")
