import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

DEFAULT_FILE = "movies.json"
GENRES = ["Боевик", "Комедия", "Драма", "Фантастика", "Ужасы", "Мультфильм", "Другое"]

class MovieLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library")
        self.root.geometry("1000x680")
        self.root.minsize(920, 600)
        self.movies = []
        self.movie_id = 1
        self.title_var = tk.StringVar()
        self.genre_var = tk.StringVar(value=GENRES[0])
        self.year_var = tk.StringVar()
        self.rating_var = tk.StringVar()
        self.filter_genre_var = tk.StringVar(value="Все")
        self.filter_year_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Готово к работе")
        self._build_ui()
        self.refresh_table()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(2, weight=1)

        form = ttk.LabelFrame(main, text="Добавление фильма", padding=10)
        form.grid(row=0, column=0, sticky="ew")
        for i in range(8):
            form.columnconfigure(i, weight=1)

        ttk.Label(form, text="Название").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.title_var).grid(row=1, column=0, sticky="ew", padx=(0, 8))
        ttk.Label(form, text="Жанр").grid(row=0, column=1, sticky="w")
        ttk.Combobox(form, textvariable=self.genre_var, values=GENRES, state="readonly").grid(row=1, column=1, sticky="ew", padx=(0, 8))
        ttk.Label(form, text="Год выпуска").grid(row=0, column=2, sticky="w")
        ttk.Entry(form, textvariable=self.year_var).grid(row=1, column=2, sticky="ew", padx=(0, 8))
        ttk.Label(form, text="Рейтинг (0-10)").grid(row=0, column=3, sticky="w")
        ttk.Entry(form, textvariable=self.rating_var).grid(row=1, column=3, sticky="ew", padx=(0, 8))
        ttk.Button(form, text="Добавить фильм", command=self.add_movie).grid(row=1, column=4, sticky="ew", padx=(0, 8))
        ttk.Button(form, text="Сохранить JSON", command=self.save_json).grid(row=1, column=5, sticky="ew", padx=(0, 8))
        ttk.Button(form, text="Загрузить JSON", command=self.load_json).grid(row=1, column=6, sticky="ew", padx=(0, 8))
        ttk.Button(form, text="Удалить выбранное", command=self.delete_selected).grid(row=1, column=7, sticky="ew")

        filt = ttk.LabelFrame(main, text="Фильтрация", padding=10)
        filt.grid(row=1, column=0, sticky="ew", pady=12)
        for i in range(6):
            filt.columnconfigure(i, weight=1)
        ttk.Label(filt, text="Жанр").grid(row=0, column=0, sticky="w")
        ttk.Combobox(filt, textvariable=self.filter_genre_var, values=["Все"] + GENRES, state="readonly").grid(row=1, column=0, sticky="ew", padx=(0, 8))
        ttk.Label(filt, text="Год").grid(row=0, column=1, sticky="w")
        ttk.Entry(filt, textvariable=self.filter_year_var).grid(row=1, column=1, sticky="ew", padx=(0, 8))
        ttk.Button(filt, text="Применить фильтр", command=self.apply_filter).grid(row=1, column=2, sticky="ew", padx=(0, 8))
        ttk.Button(filt, text="Сбросить фильтр", command=self.reset_filter).grid(row=1, column=3, sticky="ew")

        table_frame = ttk.LabelFrame(main, text="Коллекция фильмов", padding=10)
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        cols = ("id", "title", "genre", "year", "rating")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=16)
        headings = [("id", "ID", 60), ("title", "Название", 320), ("genre", "Жанр", 160), ("year", "Год", 100), ("rating", "Рейтинг", 100)]
        for key, text, width in headings:
            self.tree.heading(key, text=text)
            self.tree.column(key, width=width, anchor="center" if key != "title" else "w")
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        status = ttk.Label(main, textvariable=self.status_var, relief="sunken", anchor="w", padding=6)
        status.grid(row=3, column=0, sticky="ew", pady=(10, 0))

    def _validate_year(self, value):
        value = value.strip()
        if not value.isdigit():
            raise ValueError("Год должен быть числом.")
        year = int(value)
        if year < 1 or year > 9999:
            raise ValueError("Год введён некорректно.")
        return year

    def _validate_rating(self, value):
        try:
            rating = float(value.replace(",", "."))
        except ValueError:
            raise ValueError("Рейтинг должен быть числом.")
        if rating < 0 or rating > 10:
            raise ValueError("Рейтинг должен быть от 0 до 10.")
        return round(rating, 1)

    def add_movie(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("Ошибка", "Название не может быть пустым.")
            return
        try:
            year = self._validate_year(self.year_var.get())
            rating = self._validate_rating(self.rating_var.get())
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
            return
        movie = {"id": self.movie_id, "title": title, "genre": self.genre_var.get(), "year": year, "rating": rating}
        self.movies.append(movie)
        self.movie_id += 1
        self.refresh_table(self.movies)
        self.title_var.set("")
        self.year_var.set("")
        self.rating_var.set("")
        self.status_var.set(f"Фильм добавлен: {title}")

    def refresh_table(self, data=None):
        data = self.movies if data is None else data
        self.tree.delete(*self.tree.get_children())
        for m in data:
            self.tree.insert("", "end", values=(m["id"], m["title"], m["genre"], m["year"], f'{m["rating"]:.1f}'))

    def apply_filter(self):
        genre = self.filter_genre_var.get()
        year_text = self.filter_year_var.get().strip()
        try:
            year_filter = None
            if year_text:
                year_filter = self._validate_year(year_text)
        except ValueError as e:
            messagebox.showerror("Ошибка фильтра", str(e))
            return
        filtered = []
        for movie in self.movies:
            if genre != "Все" and movie["genre"] != genre:
                continue
            if year_filter is not None and movie["year"] != year_filter:
                continue
            filtered.append(movie)
        self.refresh_table(filtered)
        self.status_var.set(f"Фильтр применён. Найдено: {len(filtered)}")

    def reset_filter(self):
        self.filter_genre_var.set("Все")
        self.filter_year_var.set("")
        self.refresh_table(self.movies)
        self.status_var.set("Фильтр сброшен")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Удаление", "Выберите фильм в таблице.")
            return
        movie_id = int(self.tree.item(selected[0], "values")[0])
        self.movies = [m for m in self.movies if m["id"] != movie_id]
        self.refresh_table(self.movies)
        self.status_var.set(f"Удалён фильм ID {movie_id}")

    def save_json(self):
        path = filedialog.asksaveasfilename(title="Сохранить JSON", defaultextension=".json", initialfile=DEFAULT_FILE, filetypes=[("JSON files", "*.json")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.movies, f, ensure_ascii=False, indent=4)
        self.status_var.set(f"Сохранено: {os.path.basename(path)}")
        messagebox.showinfo("Сохранение", "Данные успешно сохранены.")

    def load_json(self):
        path = filedialog.askopenfilename(title="Загрузить JSON", filetypes=[("JSON files", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            loaded = []
            for i, m in enumerate(data, start=1):
                title = str(m.get("title", "")).strip()
                if not title:
                    raise ValueError("Название не может быть пустым.")
                genre = str(m.get("genre", "Другое")).strip() or "Другое"
                if genre not in GENRES:
                    genre = "Другое"
                year = self._validate_year(str(m.get("year", "")))
                rating = self._validate_rating(str(m.get("rating", "")))
                loaded.append({"id": i, "title": title, "genre": genre, "year": year, "rating": rating})
            self.movies = loaded
            self.movie_id = len(self.movies) + 1
            self.refresh_table(self.movies)
            self.status_var.set(f"Загружено фильмов: {len(self.movies)}")
            messagebox.showinfo("Загрузка", "Данные успешно загружены.")
        except (json.JSONDecodeError, OSError, ValueError) as e:
            messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить файл: {e}")


def main():
    root = tk.Tk()
    MovieLibraryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
