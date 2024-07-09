import os
import re
import shutil
from datetime import datetime, timedelta, date

from flask import Flask, request, send_file, render_template
import pandas as pd
from latters_and_symbols import TRANSLATION, HARFLAR

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        sana = str(datetime.now().date())
        soat = str(datetime.now().time().hour) + str(datetime.now().time().minute) + str(datetime.now().time().second)
        file_name = sana + '_' + soat + '_' + str(file.filename[:file.filename.rfind('.')])
        input_destination_folder = './input_file/'
        output_destination_folder = './output_file/'
        filename = 'uploaded.xlsx'
        file.save(filename)
        shutil.copy(filename, os.path.join(input_destination_folder, f'{file_name}.xlsx'))
        txt_filename = process_excel(excel_file=filename, response_file_name=file_name)
        res_file = shutil.copy(txt_filename, os.path.join(output_destination_folder, f'final_{file_name}.txt'))
        remove_old_files()
        if os.path.exists(txt_filename):
            os.remove(txt_filename)
        else:
            print("The file does not exist")
        return send_file(res_file, as_attachment=True)
def process_excel(excel_file, response_file_name):
    df = pd.read_excel(excel_file)  # Excel faylini pandas DataFrame-ga yuklash
    txt_filename = f'{response_file_name}.txt'
    error_process = ''
    playlist_day = ''
    break_time = ''

    with (open(txt_filename, 'w') as txt_file):
        count = 1
        for index, row in df.iterrows():
            for_text = ''
            try:
                if index == 0:
                    playlist_day = row.iloc[3]
                    playlist_day = playlist_day.replace(".", "")
                    dm = playlist_day[:4]
                    playlist_day = dm + playlist_day[6:]
                    standart_day = playlist_day
                bt = str(row.iloc[3])
                if len(bt) == 8:
                    if bt[2] == ':':
                        break_time = bt.replace(":", "")
                    elif bt[2] == '.':
                        break_time = bt.replace(".", "")
                    else:
                        error_process += f' *** break_time_error Format {row.iloc[4]} *** '
                        break
                    break_time = break_time[:4]
                    if int(break_time[:2]) > 23:
                        break_time_minut = break_time[2:]
                        break_time = int(break_time[:2]) - 24
                        break_time = str(f'{break_time:02d}') + break_time_minut
                        if standart_day == playlist_day:
                            # Sana formatini aniqlash
                            date_format = '%d%m%y'
                            # Sana obyektiga aylantiramiz
                            given_date = datetime.strptime(playlist_day, date_format)
                            # Keyingi kuni topish
                            next_day = given_date + timedelta(days=1)
                            # Keyingi kuni string formatga o'tkazish
                            playlist_day = next_day.strftime(date_format)
                    else:
                        playlist_day = standart_day
                if type(row.iloc[4]) == int:
                    try:
                        if len(str(count)) < 4:
                            nr = f'{count:04d}'
                            for_text += nr + 'C'
                        else:
                            error_process += f' *** Tartib raqam 4 xonadan katta ***'
                            break
                        count += 1
                        if len(playlist_day) == 6:
                            for_text += playlist_day
                        else:
                            error_process += f' *** playlist_day_error_len {row.iloc[4]} *** '
                            break
                        if len(break_time) == 4:
                            for_text += break_time
                        else:
                            error_process += f' *** break_time_error_len {row.iloc[4]} *** '
                            break
                        pattern = r'\d+'
                        if str(row.iloc[4]).startswith('5'):
                            last_underscore_index5 = row.iloc[5].rfind('_')
                            if last_underscore_index5 != -1:
                                duration_of_spot5 = row.iloc[5]
                                duration_of_spot5 = duration_of_spot5[last_underscore_index5 + 1:]
                                duration_of_spot5 = re.findall(pattern, duration_of_spot5)
                                duration_of_spot5 = duration_of_spot5[0]
                                if len(str(duration_of_spot5)) == 1:
                                    for_text += '000' + duration_of_spot5 + '00'
                                elif len(str(duration_of_spot5)) == 2:
                                    for_text += '00' + duration_of_spot5 + '00'
                                elif len(str(duration_of_spot5)) == 3:
                                    for_text += '0' + duration_of_spot5 + '00'
                        else:
                            last_underscore_index = row.iloc[5].rfind('_')
                            second_last_underscore_index = row.iloc[5].rfind('_', 0, last_underscore_index)
                            if second_last_underscore_index != -1 and last_underscore_index != -1:
                                duration_of_spot = row.iloc[5]
                                duration_of_spot = duration_of_spot[second_last_underscore_index + 1: last_underscore_index]
                                duration_of_spot = re.findall(pattern, duration_of_spot)
                                if len(duration_of_spot) == 0:
                                    duration_of_spot = row.iloc[5]
                                    duration_of_spot = duration_of_spot[last_underscore_index + 1:]
                                    duration_of_spot = re.findall(pattern, duration_of_spot)
                                    duration_of_spot = duration_of_spot[0]
                                    if len(str(duration_of_spot)) == 1:
                                        for_text += '000' + duration_of_spot + '00'
                                    elif len(str(duration_of_spot)) == 2:
                                        for_text += '00' + duration_of_spot + '00'
                                    elif len(str(duration_of_spot)) == 3:
                                        for_text += '0' + duration_of_spot + '00'
                                else:
                                    duration_of_spot = duration_of_spot[0]
                                    if len(str(duration_of_spot)) == 1:
                                        for_text += '000' + duration_of_spot + '00'
                                    elif len(str(duration_of_spot)) == 2:
                                        for_text += '00' + duration_of_spot + '00'
                                    elif len(str(duration_of_spot)) == 3:
                                        for_text += '0' + duration_of_spot + '00'
                            else:
                                error_process += f' *** duration_of_spot_error_len {row.iloc[4]} *** '
                                break
                        result = almashtir(row.iloc[5])
                        for_text += result

                        if len(str(row.iloc[4])) < 10:
                            new_id = str(row.iloc[4]).ljust(10)
                            for_text += new_id
                        elif len(str(row.iloc[4])) == 10:
                            for_text += str(row.iloc[4])
                        else:
                            error_process += f' *** spot_id_error_len {row.iloc[4]} *** '
                            break
                        fill_with_space = ''.ljust(40)
                        for_text += fill_with_space
                        if int(nr) == 1:
                            txt_file.write(for_text)
                        else:
                            txt_file.write('\n' + for_text)
                        print(for_text, '****', 'LEN:', len(for_text), '****')
                    except Exception as e:
                        try:
                            # Total_2024_20_сек_узб xatolik uchun
                            last_underscore_index = row.iloc[5].rfind('_')
                            second_last_underscore_index = row.iloc[5].rfind('_', 0, last_underscore_index)
                            third_last_underscore_index = row.iloc[5].rfind('_', 0, second_last_underscore_index)
                            if third_last_underscore_index != -1 and second_last_underscore_index != -1:
                                duration_of_spot = row.iloc[5]
                                duration_of_spot = duration_of_spot[third_last_underscore_index + 1: second_last_underscore_index]
                                duration_of_spot = re.findall(pattern, duration_of_spot)
                                duration_of_spot = duration_of_spot[0]
                                if len(str(duration_of_spot)) == 1:
                                    for_text += '000' + duration_of_spot + '00'
                                elif len(str(duration_of_spot)) == 2:
                                    for_text += '00' + duration_of_spot + '00'
                                elif len(str(duration_of_spot)) == 3:
                                    for_text += '0' + duration_of_spot + '00'
                            else:
                                error_process += f' *** duration_of_spot_error_len {row.iloc[4]} *** '
                                break
                            result = almashtir(row.iloc[5])
                            for_text += result
                            if len(str(row.iloc[4])) < 10:
                                new_id = str(row.iloc[4]).ljust(10)
                                for_text += new_id
                            elif len(str(row.iloc[4])) == 10:
                                for_text += str(row.iloc[4])
                            else:
                                error_process += f' *** spot_id_error_len {row.iloc[4]}  *** '
                                break
                            fill_with_space = ''.ljust(40)
                            for_text += fill_with_space
                            if int(nr) == 1:
                                txt_file.write(for_text)
                            else:
                                txt_file.write('\n' + for_text)
                            print(for_text, '****', 'LEN:', len(for_text), '**** try')
                        except:
                            error_process += f' *** Yozishda xatolik {e, row.iloc[4]}  *** '
                            print('Yozishda xatolik', e, row.iloc[5])
            except Exception as e:
                pass

    if len(error_process) > 0:
        with open(txt_filename, 'w') as file:
            file.write(str(error_process))
        print(f'!!! {error_process} !!!')
    else:
        print(f"*** Ma'lumotlar yangi faylga muvaffaqiyatli yozildi. Qatorlar soni: {count-1}. ***")

    return txt_filename

def almashtir(matn):
    yangi_matn = ""
    for belgi in matn:
        if belgi.isdigit():
            yangi_matn += belgi
        elif belgi in HARFLAR:
            yangi_matn += belgi
        else:
            if belgi in TRANSLATION:
                yangi_matn += TRANSLATION[belgi]
            else:
                yangi_matn += "_"
    if len(yangi_matn) < 30:
        yangi_matn = yangi_matn.ljust(30)
    else:
        yangi_matn = yangi_matn[:28]
        yangi_matn = yangi_matn.ljust(30)
    return yangi_matn
def remove_old_files():
    papka_input = 'input_file'
    papka_output = 'output_file'

    joriy_sana = date.today()
    ochirish_limiti = joriy_sana - timedelta(days=10)

    for fayl in os.listdir(papka_input):
        if os.path.isfile(os.path.join(papka_input, fayl)):
            try:
                # Fayl nomini dataga o'girish
                fayl_sanasi_str = fayl.split('_')[0]
                fayl_sanasi = datetime.strptime(fayl_sanasi_str, '%Y-%m-%d').date()

                # Agar fayl joriy sanadan 10 kun o'tgan bo'lsa, uni o'chiramiz
                if fayl_sanasi < ochirish_limiti:
                    os.remove(os.path.join(papka_input, fayl))
                    print(f"{fayl} fayli o'chirildi.")
            except ValueError:
                continue  # Fayl nomi sana formatiga mos kelmaydi

    for fayl in os.listdir(papka_output):
        if os.path.isfile(os.path.join(papka_output, fayl)):
            try:
                # Fayl nomini dataga o'girish
                fayl_sanasi_str = fayl.split('_')[0]
                fayl_sanasi = datetime.strptime(fayl_sanasi_str, '%Y-%m-%d').date()

                # Agar fayl joriy sanadan 10 kun o'tgan bo'lsa, uni o'chiramiz
                if fayl_sanasi < ochirish_limiti:
                    os.remove(os.path.join(papka_output, fayl))
                    print(f"{fayl} fayli o'chirildi.")
            except ValueError:
                continue  # Fayl nomi sana formatiga mos kelmaydi

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)