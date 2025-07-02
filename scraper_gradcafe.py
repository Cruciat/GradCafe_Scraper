import requests
from bs4 import BeautifulSoup
import re
import os
import csv
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
import time
import sys
import shutil
import pyfiglet
from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)

def print_title():
    """Stampa un titolo grande e colorato all'avvio."""
    title = pyfiglet.figlet_format("GradCafe Scraper", font="standard")
    colored_title = f"{Fore.CYAN}{Style.BRIGHT}{title}{Style.RESET_ALL}"
    print(colored_title)
    print(f"{Fore.YELLOW}{'='*50}{Style.RESET_ALL}\n")

def clear_line():
    """Pulisce la linea corrente nel terminale."""
    sys.stdout.write("\r" + " " * 100 + "\r")
    sys.stdout.flush()

def dynamic_status(page_num, last_page_num, total_items):
    """Mostra una barra di stato dinamica con emoji e colori."""
    progress = int(50 * page_num / last_page_num)
    bar = f"{Fore.GREEN}{'█'*progress}{Fore.YELLOW}{'-'*(50-progress)}{Style.RESET_ALL}"
    percent = 100 * page_num / last_page_num
    status = f"[{bar}] {percent:.1f}% | 📄 Pagina {page_num}/{last_page_num} | 📦 Voci: {total_items}"
    sys.stdout.write(f"\r{status}")
    sys.stdout.flush()

def extract_data_from_soup(soup):
    """Estrae i dati da un oggetto BeautifulSoup."""
    # 1. Trova il PRIMO <tr> nel documento
    start_tr = soup.find('tr')
    if not start_tr:
        raise Exception("Nessun <tr> trovato nella pagina")
    
    # 2. Esci dal <thead> (se esiste)
    thead = start_tr.find_parent('thead')
    
    # 3. Trova il primo <tbody> successivo
    tbody = start_tr.find_next('tbody')
    if not tbody:
        raise Exception("Nessun <tbody> trovato dopo il primo <tr>")
    
    # 4. Itera sui gruppi di <tr>
    results = []
    rows = tbody.find_all('tr', recursive=False)
    i = 0
    while i < len(rows):
        first_row = rows[i]
        group_data = {}

        # Estrazione parametri dalla PRIMA riga
        tds = first_row.find_all('td', recursive=False)

        # --- School: td[0] -> div -> div ---
        if len(tds) > 0:
            school_divs = tds[0].find_all('div', recursive=True)
            if len(school_divs) >= 2:
                group_data['School'] = school_divs[1].get_text(strip=True)
        
        # --- Program: td[1] -> div -> span + span ---
        if len(tds) > 1:
            program_div = tds[1].find('div')
            if program_div:
                spans = program_div.find_all('span')
                if len(spans) >= 1:
                    group_data['Program'] = spans[0].get_text(strip=True)
                if len(spans) >= 2:
                    group_data['Level'] = spans[1].get_text(strip=True)
        
        # --- Added on: td[2] -> Testo diretto ---
        if len(tds) > 2:
            added_on_text = tds[2].get_text(strip=True)
            if added_on_text:
                group_data['Added on'] = added_on_text
        
        # --- Decision: td[3] -> Solo la PRIMA PAROLA ---
        if len(tds) > 3:
            decision_text = tds[3].get_text(strip=True)
            if decision_text:
                group_data['Decision'] = decision_text.split()[0]

        i += 1

        # SECONDA RIGA: GPA, GRE, ecc.
        if i < len(rows) and 'tw-border-none' in rows[i].get('class', []):
            second_row = rows[i]
            td = second_row.find('td')
            if td:
                outer_div = td.find('div', class_=True)
                if outer_div:
                    inner_divs = outer_div.find_all('div')
                    if len(inner_divs) >= 1:
                        for div in inner_divs:
                            text = div.get_text(strip=True)
                            # Estrai GPA
                            gpa_match = re.search(r'GPA\D*(\d+\.?\d*)', text, re.IGNORECASE)
                            if gpa_match:
                                group_data['GPA'] = gpa_match.group(1)
                                continue
                            # Estrai GRE V
                            gre_v_match = re.search(r'GRE\s+V\s*(\d+)', text, re.IGNORECASE)
                            if gre_v_match:
                                group_data['GRE V'] = gre_v_match.group(1)
                                continue
                            # Estrai GRE Q
                            gre_q_match = re.search(r'GRE\s+Q\s*(\d+)', text, re.IGNORECASE)
                            if gre_q_match:
                                group_data['GRE Q'] = gre_q_match.group(1)
                                continue
                            # Estrai GRE AW
                            gre_aw_match = re.search(r'GRE\s+AW\s*(\d+\.?\d*)', text, re.IGNORECASE)
                            if gre_aw_match:
                                group_data['GRE AW'] = gre_aw_match.group(1)
                                continue
                            # Estrai GRE (generale)
                            gre_match = re.search(r'GRE\s*(\d+)', text, re.IGNORECASE)
                            if gre_match:
                                group_data['GRE'] = gre_match.group(1)
                                continue
            i += 1

            # TERZA RIGA: Comment (opzionale)
            if i < len(rows) and 'tw-border-none' in rows[i].get('class', []):
                third_row = rows[i]
                td_comment = third_row.find('td')
                if td_comment:
                    p_tag = td_comment.find('p')
                    if p_tag:
                        group_data['Comment'] = p_tag.get_text(strip=True)
                i += 1

        results.append(group_data)

    return results

def build_page_url(url, page_num):
    """Costruisce l'URL per una pagina specifica, gestendo tutti i casi limite."""
    # Parsing dell'URL
    parsed = urlparse(url)
    
    # Parsing dei parametri di query
    query_params = parse_qs(parsed.query, keep_blank_values=True)
    
    # Aggiornamento del numero di pagina
    query_params['page'] = [str(page_num)]
    
    # Ricostruzione della query string (gestisce correttamente caratteri speciali)
    new_query = urlencode(query_params, doseq=True)
    
    # Ricostruzione dell'URL completo, mantenendo tutti i componenti originali
    new_parsed = parsed._replace(
        query=new_query,          # Aggiorna solo la query string
        scheme=parsed.scheme,     # Mantieni lo stesso protocollo (http/https)
        netloc=parsed.netloc,     # Mantieni lo stesso dominio
        path=parsed.path,         # Mantieni lo stesso percorso
        params=parsed.params,     # Mantieni i parametri (raramente usati)
        fragment=parsed.fragment  # Mantieni il fragment se presente
    )
    
    # Ritorna l'URL ricostruito
    return urlunparse(new_parsed)

def get_last_page_number(soup):
    """Trova il numero dell'ultima pagina tramite i link di paginazione."""
    # 1. Cerca il primo elemento che contiene la parola "Previous" (case-insensitive)
    text_node = soup.find(string=re.compile(r'\bPrevious\b', re.IGNORECASE))
    if not text_node:
        raise Exception("Testo 'Previous' non trovato")

    # 2. Risali al genitore <span> o <div> (o altro elemento)
    span_prev = text_node.parent
    if not span_prev:
        raise Exception("Nessun genitore trovato per 'Previous'")

    # 3. Risali fino alla div genitore (se necessario)
    div_container = span_prev.find_parent('div')
    if not div_container:
        div_container = span_prev  # Usa il genitore attuale se è già una div

    # 4. Vai alla div successiva
    next_div = div_container.find_next_sibling('div')
    if not next_div:
        raise Exception("Div successiva non trovata")

    # 5. Trova tutti i link <a> e prendi l'ultimo
    links = next_div.find_all('a')
    if not links:
        raise Exception("Nessun link trovato nella div successiva")

    last_link = links[-1]
    last_page_text = last_link.get_text(strip=True)

    # 6. Verifica che sia un numero
    if not last_page_text.isdigit():
        raise Exception(f"L'ultimo link non è un numero: {last_page_text}")

    return int(last_page_text)

def build_base_url(institution, program, degree):
    """Costruisce l'URL base con i parametri forniti."""
    url = "https://www.thegradcafe.com/survey/"  # ⚠️ Fix: URL senza spazi extra
    params = {
        'q': '',
        'sort': 'newest',
        'institution': institution,
        'program': program,
        'degree': degree,
        'season': '',
        'decision': '',
        'decision_start': '',
        'decision_end': '',
        'added_start': '',
        'added_end': '',
        'page': '1'
    }
    # Includi TUTTI i parametri, anche quelli vuoti
    query_string = urlencode(params, doseq=True)
    return f"{url}?{query_string}"

def clear_line():
    """Pulisce completamente la riga corrente nel terminale."""
    cols = shutil.get_terminal_size().columns
    sys.stdout.write('\r' + ' ' * cols + '\r')
    sys.stdout.flush()

def ask_input(prompt):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    value = input()
    # ANSI escape: ⬆️ torna alla riga del prompt, ⬛ la cancella
    sys.stdout.write('\033[F\033[K')
    return value

def select_degree():
    degree_options = {
        '1': '',       # Empty
        '2': 'PsyD',
        '3': 'IND',
        '4': 'Other',
        '5': 'EdD',
        '6': 'JD',
        '7': 'MBA',
        '8': 'MFA',
        '9': 'Masters',
        '10': 'PhD'
    }
    
    # Stampa la lista con controllo del cursore
    menu_lines = [
        "Seleziona un tipo di degree:",
        "1) [Vuoto]",
        "2) PsyD",
        "3) IND",
        "4) Other",
        "5) EdD",
        "6) JD",
        "7) MBA",
        "8) MFA",
        "9) Masters",
        "10) PhD"
    ]
    
    # Stampa ogni riga separatamente
    for line in menu_lines:
        sys.stdout.write(line + '\n')
    sys.stdout.flush()
    
    while True:
        choice = ask_input("Scelta: ").strip()
        
        # Cancella la lista (risali di len(menu_lines) righe e cancella)
        for _ in range(len(menu_lines) + 1):  # +1 per la riga "Scelta: "
            sys.stdout.write('\033[F\033[K')  # ⬆️ Cancella riga
        
        if choice in degree_options:
            return degree_options[choice]
        else:
            sys.stdout.write("❌ Scelta non valida. Riprova.\n")
            for line in menu_lines:
                sys.stdout.write(line + '\n')
            sys.stdout.flush()

def print_summary(institution, program, degree, degree_map):
    """Stampa un riepilogo stilizzato dei parametri."""
    summary = f"""
    {Fore.GREEN}🔍 Parametri della query:{Style.RESET_ALL}
  • {Fore.CYAN}Istituzione:{Style.RESET_ALL} {institution or f'{Fore.RED}[Nessuna]{Style.RESET_ALL}'}
  • {Fore.CYAN}Programma:{Style.RESET_ALL} {program or f'{Fore.RED}[Nessun programma]{Style.RESET_ALL}'}
  • {Fore.CYAN}Degree:{Style.RESET_ALL} {degree or f'{Fore.RED}[Nessun grado]{Style.RESET_ALL}'} ({Fore.MAGENTA}{degree_map.get(degree, 'N/A')}{Style.RESET_ALL})
    """
    print(summary)

def main():
    print_title()

    # Richiedi i parametri all'utente
    institution = ask_input("Istituzione (lascia vuoto per nessuna): ")
    program = ask_input("Programma (lascia vuoto per nessuno): ")
    degree = select_degree()
    
    # Mappa il grado selezionato per il riepilogo
    degree_map = {v: k for k, v in {
        '1': '',       
        '2': 'PsyD',
        '3': 'IND',
        '4': 'Other',
        '5': 'EdD',
        '6': 'JD',
        '7': 'MBA',
        '8': 'MFA',
        '9': 'Masters',
        '10': 'PhD'
    }.items()}

    # Mostra riepilogo parametri
    print_summary(institution, program, degree, degree_map)

    # Costruisci l'URL base
    base_url = build_base_url(institution, program, degree)
    # print(f"\n🌐 URL costruito: {base_url}\n")

    all_data = []
    page_num = 1

    # Scarica la prima pagina per ottenere il numero massimo di pagina
    first_page_url = build_page_url(base_url, 1)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
    }

    response = requests.get(first_page_url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Errore nella pagina iniziale: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    try:
        last_page_num = get_last_page_number(soup)
        # print(f"🔢 Numero massimo di pagina: {last_page_num}")
    except Exception as e:
        print(f"⚠️ Errore nel trovare il numero massimo di pagina: {e}")
        return

    # Inizia il download delle pagine
    start_time = time.time()
    while page_num <= last_page_num:
        current_url = build_page_url(base_url, page_num)
        response = requests.get(current_url, headers=headers)
        if response.status_code != 200:
            clear_line()
            print(f"\n⚠️ Errore nella pagina {page_num}: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        
        try:
            data = extract_data_from_soup(soup)
            all_data.extend(data)
        except Exception as e:
            clear_line()
            print(f"\n⚠️ Errore nell'estrazione dei dati: {e}")
            break

        # Aggiorna la barra di stato
        elapsed = time.time() - start_time
        speed = len(all_data) / elapsed if elapsed > 0 else 0
        clear_line()
        dynamic_status(page_num, last_page_num, len(all_data))
        page_num += 1
        time.sleep(0.5)  # Riduci il rischio di blocco

    # Fine del processo
    dynamic_status(last_page_num, last_page_num, len(all_data))  # Mostra stato finale completo
    print(f"\n{Fore.GREEN}✅ Estrazione completata.{Style.RESET_ALL}")
    
    # Salva i risultati in CSV
    output_dir = "output_csv"
    os.makedirs(output_dir, exist_ok=True)

    # Costruisci il nome del file dinamicamente
    filename_parts = []
    
    # Aggiungi istituzione se presente
    if institution.strip():
        filename_parts.append(institution.strip().replace(' ', '_'))
    
    # Aggiungi programma se presente
    if program.strip():
        filename_parts.append(program.strip().replace(' ', '_'))
    
    # Aggiungi degree se presente
    if degree.strip():
        filename_parts.append(degree.strip().replace(' ', '_'))
    
    # Aggiungi data corrente in formato europeo (GGMMYYYY)
    date_str = datetime.now().strftime('%d%m%Y')  # Modificato da %Y%m%d a %d%m%Y
    filename_parts.append(date_str)
    
    # Crea il nome del file senza maiuscole e con underscore
    csv_filename = '_'.join(filename_parts) + '.csv'
    csv_file = os.path.join(output_dir, csv_filename)

    # Scrivi i dati nel file CSV
    fieldnames = ['School', 'Program', 'Level', 'Added on', 'Decision', 'GPA', 'GRE V', 'GRE Q', 'GRE AW', 'Comment']
    processed_data = [{k: entry.get(k, "") for k in fieldnames} for entry in all_data]
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_data)
    
    print(f"{Fore.BLUE}📁 Dati salvati in: {csv_file}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()