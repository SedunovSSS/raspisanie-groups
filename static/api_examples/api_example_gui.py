from tkinter import *
from tkinter import ttk
import requests

root = Tk()
root['bg'] = 'black'
root.minsize(600, 200)
root.maxsize(600, 700)
root.title('Расписание API GUI')
server_address = 'http://127.0.0.1:5000'


def get_data():
    global tree
    string = ''
    group = group_entry.get()
    date = date_entry.get()
    res = requests.get(f'{server_address}/api?group={group}&date={date}')

    if res.text != 'Error':
        result = res.text.replace('<br>', '\n').split('\n')
        time = result[0].split('.')
        cab = result[1].split('.')
        data = result[2].split('.')
        tree.destroy()
        tree = ttk.Treeview(columns=columns, show="headings")
        tree.pack(fill=BOTH)
        tree.heading("Время", text="Время")
        tree.heading("Кабинет", text="Кабинет")
        tree.heading("Предмет", text="Предмет")

        for i in range(len(time)):
            string += f"{time[i]} {cab[i]} {data[i]}\n"
            tree.insert("", END, values=(time[i], cab[i], data[i]))
        print(string)

    else:
        print('ERROR')


columns = ("Время", "Кабинет", "Предмет")
group_label = Label(text='ГРУППА: ', font='Arial 15 bold', bg='black', fg='white')
group_label.pack(pady=5)
group_entry = Entry(width=30)
group_entry.pack(pady=5)
group_label = Label(text='ДАТА (1999-01-01)/today: ', font='Arial 15 bold', bg='black', fg='white')
group_label.pack(pady=5)
date_entry = Entry(width=30)
date_entry.pack(pady=5)
btn = Button(text='ПОЛУЧИТЬ API', font='Arial 15 bold', command=lambda: get_data())
btn.pack(pady=5)
tree = ttk.Treeview(columns=columns, show="headings")
tree.heading("Время", text="Время")
tree.heading("Кабинет", text="Кабинет")
tree.heading("Предмет", text="Предмет")
root.mainloop()


