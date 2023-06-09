#
# Скрипт для экстракции файлов из дампа,
# имена и смещения файлов записаны в .csv таблице.
# Ссылка на репозиторий:
# https://github.com/NIODER/dumpfilerestoring
#

import argparse
import os
import csv
import pathlib
from os import listdir
from os.path import isfile, join

SECTOR_SIZE = 512

# парсинг csv с данныим файлов
def csv_parsing(table_name):
    with open(f'{args.tables}\\{table_name}', 'r') as csv_file:
        out_m = []
        for row in csv.reader(csv_file):
            if 'Fill' in row[0]:
                continue
            out_m.append(row)
        return out_m

# функция получения части файла из дампа
def get_part_from_dump(dump_name, file_name, start_sector, end_sector):
    with open(f'{args.dumps}\\{dump_name}', 'rb') as dump:
        data = dump.read()
    part_data = data[(SECTOR_SIZE * start_sector):(SECTOR_SIZE * end_sector + SECTOR_SIZE)]
    f_output = open(file_name, 'wb')
    f_output.write(part_data)
    f_output.close()

# функция получения файла из частей
def get_file_from_parts(dump, file_name):
    counter = 1
    file_name = file_name.split()[0]
    output = f'{args.output}\\{dump}'
    if not os.path.exists(output):
        os.makedirs(os.path.join(os.getcwd(), output))
    elif isfile(output):
        exit(-1)
    with open(f'{output}\\{file_name}', 'ab') as out_file:
        while True:
            try:
                with open(f'{file_name} ({counter})', 'rb') as f_part:
                    out_file.write(f_part.read())
                os.remove(f'{file_name} ({counter})')
                counter += 1
            except OSError:
                break
        out_file.close()

# точка входа
def main():
    dump_files = [f for f in listdir(args.dumps) if isfile(join(args.dumps, f))]
    for dump in dump_files:
        for row in csv_parsing(f'{dump.split(".")[0]}.csv'):
            get_part_from_dump(dump, row[0], int(row[2]), int(row[3]))
        for row in csv_parsing(f'{dump.split(".")[0]}.csv'):
            get_file_from_parts(dump, row[0])

# парсинг аргументов командной строки
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script extracting files from dump for 5 forensic lab.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-t', '--tables', help='Tables folder location (names should be alike dump names)',
                        required=True,
                        type=pathlib.Path,
                        metavar='TABLES_DIRECTORY')
    parser.add_argument('-d', '--dumps', help='Dumps folder location (names should be alike table names)',
                        required=True,
                        type=pathlib.Path,
                        metavar='DUMPS_DIRECTORY')
    parser.add_argument('-o', '--output', help='Output path',
                        required=False,
                        type=pathlib.Path,
                        default='output',
                        metavar='OUTPUT_DIRECTORY')
    args = parser.parse_args()
    main()
