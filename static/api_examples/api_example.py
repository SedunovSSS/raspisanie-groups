import requests

server_address = 'http://127.0.0.1:5000'
date = 'today'
group = '1'
string = ''

res = requests.get(f'{server_address}/api?group={group}&date={date}')

if res.text != 'Error':
    result = res.text.replace('<br>', '\n').split('\n')
    time = result[0].split('.')
    cab = result[1].split('.')
    data = result[2].split('.')

    for i in range(len(time)):
        string += f"{time[i]} {cab[i]} {data[i]}\n"

else:
    string = 'ERROR'

print(string)

