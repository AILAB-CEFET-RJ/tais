import csv
from datetime import datetime, timedelta
import os

# esse é o período de tempo que eu peguei dos arquivos disponibilizados pelo Pablo da Marinha
# os arquivos estavam em uma pasta chamada 1DN, dentro da pasta compactada AIS-distritos
start_date = datetime(2024, 6, 1)
end_date = datetime(2024, 8, 22)

# essas sao as colunas importantes que é preciso extrair:
#id da embarcacao, data (YYYY-MM-DD HH:MM:SS), direção do barco, velocidade, latitude e longitude
columns_to_extract = [0, 6, 8, 9, 12, 13]

input_dir = 'data'
output_dir = 'refined_data'
os.makedirs(output_dir, exist_ok=True)

current_date = start_date
while current_date <= end_date:
    month = current_date.strftime('%m')
    day = current_date.strftime('%d') 
    #o bom é que todos os arquivos seguem um padrao de nomea, ent dá pra extrair tudo direto:
    input_file = os.path.join(input_dir, f'dataset-{month}-{day}.csv')
    output_file = os.path.join(output_dir, f'refined-{month}-{day}.csv')

    try:
        with open(input_file, mode='r', newline='') as infile, open(output_file, mode='w', newline='') as outfile:
            reader = csv.reader(infile, delimiter='\t')  # tab, as colunas nao sao separados por virgulas
            writer = csv.writer(outfile)
            
            # olhar pra cada coluna no arquivo que queremos refinar
            for row_number, row in enumerate(reader):
                if len(row) > max(columns_to_extract):
                    refined_row = [row[i] for i in columns_to_extract]
                    writer.writerow(refined_row)
                else:
                    print(f"WARNING: Pulando coluna {row_number + 1} em {input_file} porque nao tem colunas suficientes.")
        
        print(f"Processou {input_file} -> {output_file}")
    
    except FileNotFoundError:
        print(f"Arquivo {input_file} não encontrado. Pulando...")
    
    current_date += timedelta(days=1)

print("\033[32mTODOS OS ARQUIVOS PROCESSADOS.\033[m")