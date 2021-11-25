import pandas as pd
import sys
import os

sys.path.append(os.getcwd())
path = './static/output_csv'
group = os.walk(path)
for path, dir_list, file_list in group:
    for file in file_list:
        if 'usd_perp' in file:
            file_path = os.path.join(path, file)
            data = pd.read_csv(file_path)
            new_file = file.replace('usd', 'usdt')
            new_info = new_file.replace('_', '|')[:-4]
            data['info'] = new_info
            data.to_csv(os.path.join(path, new_file), index=False)
            os.remove(file_path)
            # print(os.path.join(path, file) + '\t' + 'New')