import csv
import os

input_directory = 'refined_data'
output_directory = 'single_t_data'
os.makedirs(output_directory, exist_ok=True)

boat_data = {}

for filename in os.listdir(input_directory):
    if filename.startswith('refined-') and filename.endswith('.csv'):
        input_file = os.path.join(input_directory, filename)
        
        with open(input_file, mode='r', newline='') as infile:
            reader = csv.reader(infile)
            
            for row in reader:
                boat_id = row[0]  # a primeira coluna eh o ID da embarcacao
                
                if boat_id not in boat_data:
                    boat_data[boat_id] = []
                
                boat_data[boat_id].append(row)

# o proposito eh escrever cada embarcacao em um CSV separado pra considerar trajetórias longas
for boat_id, rows in boat_data.items():
    # nao add embarcacoes paradas, que nao se movem em momemnto algum
    has_movement = any(float(row[3]) > 0 for row in rows)  # velocidade = index 3
    
    if has_movement:
        output_file = os.path.join(output_directory, f'{boat_id}.csv')
        
        with open(output_file, mode='w', newline='') as outfile:
            writer = csv.writer(outfile)
            #writer.writerow(['ID', 'Data', 'Direção', 'Velocidade', 'Latitude', 'Longitude']) #def das colunas
            writer.writerows(rows)
        
        print(f"Arquivo criado para {boat_id} em {output_file}")
    else:
        print(f"Embarcação {boat_id} não possui movimento e foi ignorada.")

print("\033[32mTodos os arquivos de embarcação foram criados.\033[m")