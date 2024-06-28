import re
from datetime import datetime, timedelta

from flask import Flask, request, send_file, render_template
import pandas as pd
from latters_and_symbols import TRANSLATION

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
        filename = 'uploaded.xlsx'
        file.save(filename)
        txt_filename = process_excel(filename)
        return send_file(txt_filename, as_attachment=True)
def process_excel(excel_file):
    df = pd.read_excel(excel_file)  # Excel faylini pandas DataFrame-ga yuklash
    txt_filename = 'output.txt'
    playlist_day = ''
    break_time = ''

    with (open(txt_filename, 'w') as txt_file):
        count = 1
        error_process = ''
        for index, row in df.iterrows():
            for_text = ''
            try:
                if index == 0:
                    playlist_day = row[3]
                    playlist_day = playlist_day.replace(".", "")
                    dm = playlist_day[:4]
                    playlist_day = dm + playlist_day[6:]
                    standart_day = playlist_day
                bt = str(row[3])
                if len(bt) == 8:
                    break_time = bt.replace(":", "")
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
                if type(row[4]) == int:
                    try:
                        if len(str(count)) < 4:
                            nr = f'{count:04d}'
                            for_text += nr + 'C'
                        else:
                            error_process += ' *** Tartib raqam 4 xonadan katta *** '
                            break
                        count += 1
                        if len(playlist_day) == 6:
                            for_text += playlist_day
                        else:
                            error_process += f' *** playlist_day_error_len {playlist_day} *** '
                            break
                        if len(break_time) == 4:
                            for_text += break_time
                        else:
                            error_process += f' *** break_time_error_len {break_time} *** '
                            break
                        pattern = r'\d+'
                        if str(row[4]).startswith('5'):
                            last_underscore_index5 = row[5].rfind('_')
                            if last_underscore_index5 != -1:
                                duration_of_spot5 = row[5]
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
                            last_underscore_index = row[5].rfind('_')
                            second_last_underscore_index = row[5].rfind('_', 0, last_underscore_index)
                            if second_last_underscore_index != -1 and last_underscore_index != -1:
                                duration_of_spot = row[5]
                                duration_of_spot = duration_of_spot[second_last_underscore_index + 1: last_underscore_index]
                                duration_of_spot = re.findall(pattern, duration_of_spot)
                                duration_of_spot = duration_of_spot[0]
                                if len(str(duration_of_spot)) == 1:
                                    for_text += '000' + duration_of_spot + '00'
                                elif len(str(duration_of_spot)) == 2:
                                    for_text += '00' + duration_of_spot + '00'
                                elif len(str(duration_of_spot)) == 3:
                                    for_text += '0' + duration_of_spot + '00'
                            else:
                                error_process += f' *** duration_of_spot_error1_len {row[5]} *** '
                                break
                        result = process_string(row[5])
                        for_text += result

                        if len(str(row[4])) < 10:
                            new_id = str(row[4]).ljust(10)
                            for_text += new_id
                        elif len(str(row[4])) == 10:
                            for_text += str(row[4])
                        else:
                            error_process += ' *** spot_id_error_len *** '
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
                            last_underscore_index = row[5].rfind('_')
                            second_last_underscore_index = row[5].rfind('_', 0, last_underscore_index)
                            third_last_underscore_index = row[5].rfind('_', 0, second_last_underscore_index)
                            if third_last_underscore_index != -1 and second_last_underscore_index != -1:
                                duration_of_spot = row[5]
                                duration_of_spot = duration_of_spot[third_last_underscore_index + 1: second_last_underscore_index]
                                duration_of_spot = re.findall(pattern, duration_of_spot)
                                duration_of_spot = duration_of_spot[0]
                                if len(str(duration_of_spot)) == 1:
                                    for_text += '000' + duration_of_spot + '00'
                                elif len(str(duration_of_spot)) == 2:
                                    for_text += '00' + duration_of_spot + '00'
                                elif len(str(duration_of_spot)) == 3:
                                    for_text += '0' + duration_of_spot + '00'
                            result = process_string(row[5])
                            for_text += result
                            if len(str(row[4])) < 10:
                                new_id = str(row[4]).ljust(10)
                                for_text += new_id
                            elif len(str(row[4])) == 10:
                                for_text += str(row[4])
                            else:
                                error_process += ' *** spot_id_error_len *** '
                                break
                            fill_with_space = ''.ljust(40)
                            for_text += fill_with_space
                            if int(nr) == 1:
                                txt_file.write(for_text)
                            else:
                                txt_file.write('\n' + for_text)
                            print(for_text, '****', 'LEN:', len(for_text), '**** try')
                        except:
                            print('Yozishda xatolik', e, row[5])
            except Exception as e:
                pass

        if len(error_process) > 0:
            txt_file.write(str(error_process))
            print(f'!!! {error_process} !!!')
        else:
            print(f"*** Ma'lumotlar yangi faylga muvaffaqiyatli yozildi. Qatorlar soni: {count-1}. ***")

    return txt_filename
def process_string(value):
    new_value = ''.join(TRANSLATION.get(char, char) for char in value)
    if len(new_value) < 30:
        new_value = new_value.ljust(30)
    return new_value[:30]

if __name__ == '__main__':
    app.run(debug=True)