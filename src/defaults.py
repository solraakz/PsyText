default_title = "PsyText"

paths = {
    "html_output": "output.html",
    "nltk": "./nltk_data/",
    "output_dir": "output",
    "html_suffix": "_emotions.html",
    "affect_grid_suffix": "_affect_grid.png",
    "json_suffix": "_analysis.json"
}

# texto do botão "Analyze Emotions" tambem reusado no texto ajuda
_analyze_emotions_label_text = "Analyze Emotions"
_sentiment_trajectory_label_text = "Sentiment Trajectory"
_export_stats_to_csv_label_text = "Export Stats to CSV"

english = {
    
    # Outras strings
    "success": "Success",
    "warning": "Warning",
    "error": "Error",
    "gen": "generating",
    "sel_file": "Selected file: ",
    "file_to_open": "File to open",
    "no_file": "No file selected",
    "please_file": "Please select a file.",
    "please_text": "Please insert some text first.",
    "please_file2": "You must generate a HTML file first in order to obtain data.",
    "dialog_text_files": "Text files",
    "dialog_all_files": "All files",
    "choose_input": "Choose input file...", # Button text
    "colors_to_html": _analyze_emotions_label_text, # Button text
    "sentiment_trajectory_btn": _sentiment_trajectory_label_text, # Button text
    "export_csv_btn": _export_stats_to_csv_label_text, # Button text
    "to_affect_grid": "Output Affect Grid Graph",
    "html_file": "HTML file",
    "ag_file": "Affect Grid",
    "saved_to": "saved to",
    "open_browser_q": "View HTML on browser?",
    "manual_analysis": "Insert manual text",
    "or_manual": "Or manually insert your text here",
    "clear_interface": "Clear",
    "status_ready": "Ready",
    "status_analysing": "Analysing text...",
    "status_generating_html": "Generating HTML...",
    "status_html_done": "HTML generated: ",
    "status_generating_grid": "Generating Affect Grid...",
    "status_grid_done": "Affect Grid saved: ",
    "status_cleared": "Interface cleared.",
    "status_loading_model": "Loading sentiment model... Please wait.",
    "model_loading_failed_message": "Failed to load sentiment model.",
    "model_not_loaded_warning": "The sentiment model is still loading. Please wait.",
    "stats_title": "Overall Text Statistics:",
    "stats_num_sentences": "Number of sentences:",
    "stats_avg_valence": "Average Valence:",
    "stats_avg_arousal": "Average Arousal:",
    "stats_perc_positive": "% Positive Sentences:",
    "stats_perc_negative": "% Negative Sentences:",
    "stats_perc_neutral": "% Neutral Sentences:",
    "stats_total_words": "Total Words:",
    "stats_avg_words_sentence": "Avg. Words/Sentence:",
    "stats_ttr": "Type-Token Ratio (Vocab. Richness):",
    "stats_flesch_ease": "Flesch Reading Ease:",
    "stats_emotion_counts_title": "Emotion Word Counts:",
    "stats_pronoun_counts_title": "Pronoun Counts:",
    "csv_export_success_title": "CSV Export Successful",
    "csv_export_success_message": "Statistics exported to:\n{}",
    "csv_export_error_title": "CSV Export Error",
    "csv_export_error_message": "Could not export statistics to CSV.\nError: {}",
    "csv_no_data_warning": "No statistics data available to export. Please analyze a file first.",
    "menu_help": "Help",
    "menu_help_content": "How to Use / Info",
    "menu_about": "About PsyText",
    "about_title": "About PsyText",
    "about_content": "PsyText - Text Psychological Analyzer\n\nVersion: 1.0\nDeveloped by: [O TEU NOME AQUI]\n\nThis application performs sentiment analysis and provides basic textual metrics.",
    "help_title": "PsyText - Help / Info",
    "help_content": (
        "How to Use:\n"
        "1. Click 'Choose input file...' to select a .txt file.\n"
        f"2. Click on '{_analyze_emotions_label_text}' to generate an HTML report with sentiment analysis and overall statistics. "
        "You'll be prompted to open it in your browser.\n"
        "3. Click 'Output Affect Grid Graph' to view a chart of valence vs. arousal for the analyzed sentences. "
        "This graph will open in a new window.\n"
        f"4. Click '{_sentiment_trajectory_label_text}' to view a chart of sentiment changes throughout the text.\n"
        "5. Alternatively, click 'Insert manual text' to type or paste text for analysis.\n"
        f"6. Click '{_export_stats_to_csv_label_text}' to save the current analysis statistics to a CSV file.\n"
        "7. Click 'Clear' to reset the interface.\n\n"
        "Metrics:\n"
        "- Valence: Positivity/negativity of text.\n"
        "- Arousal: Estimated emotional intensity.\n"
        "- Flesch Reading Ease: Score indicating text readability (higher is easier).\n"
        "- Type-Token Ratio: Measure of vocabulary richness."
    )
}

# # Lexicons para contagem de emoções por palavra (inglês) # Comentado para desativar a contagem de emoções
# emotion_lexicons_en = { # Comentado para desativar a contagem de emoções
#     "joy": ["happy", "joy", "glad", "elated", "pleased", "delighted", "ecstatic", "cheerful"], # Comentado para desativar a contagem de emoções
#     "sadness": ["sad", "unhappy", "sorrow", "grief", "miserable", "depressed", "gloomy", "dejected"], # Comentado para desativar a contagem de emoções
#     "anger": ["angry", "mad", "furious", "rage", "irritated", "annoyed", "enraged", "resentful"], # Comentado para desativar a contagem de emoções
#     "fear": ["fear", "scared", "afraid", "terrified", "anxious", "nervous", "worried", "dread"], # Comentado para desativar a contagem de emoções
#     "surprise": ["surprise", "surprised", "amazed", "astonished", "startled"] # Comentado para desativar a contagem de emoções
# } # Comentado para desativar a contagem de emoções

# categorias de pronomes (em ingles)
pronoun_categories_en = {
    "first_person_singular": ["i", "me", "my", "mine", "myself"],
    "first_person_plural": ["we", "us", "our", "ours", "ourselves"],
    "second_person": ["you", "your", "yours", "yourself", "yourselves"],
    "third_person_singular_masc": ["he", "him", "his", "himself"],
    "third_person_singular_fem": ["she", "her", "hers", "herself"],
    "third_person_singular_neutral": ["it", "its", "itself"], # 'it' can be tricky
    "third_person_plural": ["they", "them", "their", "theirs", "themselves"]
}
