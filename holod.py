from tkinter import *
from tkinter import simpledialog, messagebox
from datetime import *

ITEMS_PER_PAGE = 8
current_page = 1
current_page_copy = 1


# ------------------------------------------------------------------------------
# открывание и закрывание холодильника
def change_image():
    global current_image
    if current_image == image1:
        label.config(image=image2)
        current_image = image2
        btn1.config(text="Закрыть")
        toggle_search_frame(True)
        resize_and_center(625, 400)
    else:
        label.config(image=image1)
        current_image = image1
        btn1.config(text="Открыть")
        toggle_search_frame(False)
        resize_and_center(250, 390)


# ------------------------------------------------------------------------------
# начальная настройка
def Init():
    resize_and_center(250, 390)
    search_frame.grid(row=1, column=0, sticky="nsew")
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(1, weight=1)
    update_listbox()


# ------------------------------------------------------------------------------
# установка приложения по центру экрана
def resize_and_center(window_width, window_height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_cordinate = int((screen_width / 2) - (window_width / 2))
    y_cordinate = int((screen_height / 2) - (window_height / 2))
    root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))


# ------------------------------------------------------------------------------
# появление и исчезновение списка
def toggle_search_frame(visible):
    if visible:
        search_frame.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=15)
    else:
        search_frame.grid_forget()


# ------------------------------------------------------------------------------
# поисковик
def search_listbox(event=None):
    global current_page, current_page_copy
    search_term = search_entry.get().lower()
    update_listbox(search_term)
    if search_entry.get():
        current_page = 1
        update_listbox(search_term)
    if len(search_entry.get()) == 1:
        current_page = current_page_copy


# ------------------------------------------------------------------------------
# удаление продуктов из списка
def update_quantity(item, amount):
    item_quantities[item]["value"] += amount
    if item_quantities[item]["value"] <= 0:
        del item_quantities[item]["value"]
        del item_quantities[item]["date"]
    update_listbox()


# ------------------------------------------------------------------------------
# добавление продуктов
def add_item():
    new_item = new_item_entry.get()
    if new_item:
        if new_item in item_quantities:
            messagebox.showwarning("Ошибка", "Этот продукт уже существует!")
        else:
            item_quantities[new_item] = {"value": 0, "date": date(2024, 1, 1)}
            update_listbox()
            new_item_entry.delete(0, END)
    else:
        messagebox.showwarning("Ошибка", "Введите название продукта")


# --------------------------------------------------------------------------------------------------------------
# перезагрузка измененного списка
def update_listbox(search_term=""):
    global current_page
    start_index = (current_page - 1) * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE

    for widget in listbox.winfo_children():
        widget.destroy()

    filtered_items = [item for item, quantity in item_quantities.items() if search_term.lower() in item.lower()]
    displayed_items = filtered_items[start_index:end_index]

    for item in displayed_items:
        expiration_date = item_quantities[item]["date"].strftime('%d-%m-%Y')
        quantity = item_quantities[item]["value"]
        item_frame = Frame(listbox)
        item_frame.pack(fill=X)

        item_label = Label(item_frame, text=f"{item} ({quantity})", bg="white", width=22)
        item_label.pack(side=LEFT)
        expiration_label = Label(item_frame, text=f"до: {expiration_date}", bg="white", width=12)
        expiration_label.pack(side=LEFT)

        add_button = Button(item_frame, text="+", command=lambda item=item: update_quantity(item, 1), width=2)
        add_button.pack(side=RIGHT)
        sub_button = Button(item_frame, text="-", command=lambda item=item: update_quantity(item, -1), width=2)
        sub_button.pack(side=RIGHT)
        change_button = Button(item_frame, text="⌫", command=lambda item=item: update_expirations_date(item), width=2)
        change_button.pack(side=RIGHT)

    update_page_buttons()
    auto_prev_page()


# ------------------------------------------------------------------------------
# изменение даты до того как продукт просрочится
def update_expirations_date(item):
    try:
        new_date_str = simpledialog.askstring("Изменение срока годности",
                                              f"Введите новый срок годности продукта \"{item}\" в формате ДД.ММ.ГГГГ:",
                                              initialvalue=item_quantities.get(""))
        if new_date_str:
            new_date = datetime.strptime(new_date_str, "%d.%m.%Y").date()
            item_quantities[item]["date"] = new_date
            update_listbox()
    except ValueError:
        messagebox.showwarning("Ошибка", "Неверный формат даты. Используйте ДД.ММ.ГГГГ")
        update_expirations_date(item)


# ------------------------------------------------------------------------------
# блокировка кнопок навигации
def update_page_buttons():
    total_pages = (len(item_quantities) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    prev_button.config(state=("disabled" if (current_page == 1) else "normal"))
    next_button.config(state=("disabled" if (current_page == total_pages or len(item_quantities) == 0) else "normal"))
    if search_entry.get():
        prev_button.config(state="disabled")
        next_button.config(state="disabled")


# ------------------------------------------------------------------------------
# переход на предыдущую страницу
def prev_page():
    global current_page, current_page_copy
    current_page -= 1
    update_listbox()
    current_page_copy = current_page


# ------------------------------------------------------------------------------
# переход на следующую страницу
def next_page():
    global current_page, current_page_copy
    current_page += 1
    update_listbox()
    current_page_copy = current_page


# ------------------------------------------------------------------------------
# автопереход на предыдущую страницу если вы находились
# на последней странице и на ней кончились элементы
def auto_prev_page():
    global current_page
    if (current_page == ((len(item_quantities) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE) + 1) and current_page > 1:
        current_page -= 1
        update_listbox()


# ------------------------------------------------------------------------------
root = Tk()
root.title("Холодильник")
root.resizable(False, False)

item_quantities = {
    "Яблоко": {"value": 5, "date": date(2024, 2, 15)},
    "Банан": {"value": 3, "date": date(2024, 2, 28)},
    "Апельсин": {"value": 2, "date": date(2024, 3, 8)},
    "Груша": {"value": 1, "date": date(2024, 3, 8)},
    "Киви": {"value": 2, "date": date(2024, 3, 8)},
    "Манго": {"value": 7, "date": date(2024, 3, 8)},
    "Ананас": {"value": 4, "date": date(2024, 2, 15)},
    "Виноград": {"value": 9, "date": date(2024, 3, 8)},
    "Арбуз": {"value": 3, "date": date(2024, 2, 15)},
    "Дыня": {"value": 2, "date": date(2024, 3, 8)},
    "Персик": {"value": 3, "date": date(2024, 2, 15)},
    "Нектарин": {"value": 5, "date": date(2024, 2, 15)}
}

image1 = PhotoImage(file="hl.1.png.")
image2 = PhotoImage(file="hl.2.png.")

btn1 = Button(root, text="Открыть", command=change_image, bg="white")
btn1.grid(row=0, column=0, sticky="nw", padx=90)

search_frame = Frame(root)
toggle_search_frame(False)
# ---------------------------------------------------------------------------------------
# строка поиска
search_label = Label(search_frame, text="Поиск:")
search_entry = Entry(search_frame)

search_label.grid(row=0, column=0, sticky="w", padx=5)
search_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
search_entry.bind("<KeyRelease>", search_listbox)
# ---------------------------------------------------------------------------------------
current_image = image1
label = Label(root, image=image1)
label.grid(row=1, column=0, sticky="nsew")

listbox = Frame(search_frame)
listbox.grid(row=1, column=0, columnspan=2, pady=5, sticky="nsew")
# ----------------------------------------------------------------------------------------
# навигация
page_controls = Frame(search_frame)
page_controls.grid(row=2, column=0, columnspan=2, pady=5)

prev_button = Button(page_controls, text="Назад", command=prev_page, state="disabled")
prev_button.pack(side=LEFT)
next_button = Button(page_controls, text="Вперед", command=next_page)
next_button.pack(side=RIGHT)

add_item_frame = Frame(search_frame)
add_item_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

# ----------------------------------------------------------------------------------------
# добавление продуктов
new_item_label = Label(add_item_frame, text="Добавить продукт:")
new_item_label.grid(row=0, column=0, sticky="w")
new_item_entry = Entry(add_item_frame)
new_item_entry.grid(row=0, column=1, sticky="ew", padx=5)
add_item_button = Button(add_item_frame, text="Добавить", command=add_item)
add_item_button.grid(row=0, column=2, padx=5)
# -----------------------------------------------------------------------------------------

Init()

root.mainloop()
