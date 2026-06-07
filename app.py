import ttkbootstrap as ttk
import sqlite3

# CORRECCIÓN: Heredar de ttk.Window, NO de tk.Tk
class MiAplicacion(ttk.Window):
    def __init__(self, **kwargs):
        # Ahora super() llamará al constructor de ttkbootstrap que SÍ acepta "theme"
        super().__init__(**kwargs)
        
        self.title("Mi App con SQLite")
        self.geometry("600x400")
        self.iconbitmap("Hojalata.ico")
        # crea la base de datos y la tabla si no existen
        self.setup_database()
        # crea los widgets de la interfaz
        self.create_widgets()

    def setup_database(self):
        self.conn = sqlite3.connect("inventario_simple.db")
        self.cursor = self.conn.cursor()

        #crear tabla productos
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                precio REAL NOT NULL,
                cantidad INTEGER DEFAULT 1
            )
        """)

    def create_widgets(self):
        """ Aquí puedes agregar tus widgets, como botones, entradas, etc. """
        # Frame principal
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        title_label = ttk.Label(
            main_frame, 
            text="Gestión de Inventario", 
            font=("Helvetica", 18)
        )
        title_label.pack(pady=(0, 20))

        # Frame para agregar productos
        input_frame = ttk.LabelFrame(main_frame, text="Agregar Producto", padding=15)
        input_frame.pack(fill="x", pady=(0, 20))

        ttk.Label(input_frame, text="Nombre:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.nombre_entry = ttk.StringVar()
        ttk.Entry(input_frame, textvariable=self.nombre_entry).grid(row=0, column=1, padx=10, pady=5)
        
        
        """
        ttk.Label(input_frame, text="Precio:").grid(row=1, column=0, sticky="w")
        self.precio_entry = ttk.Entry(input_frame)
        self.precio_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(input_frame, text="Cantidad:").grid(row=2, column=0, sticky="w")
        self.cantidad_entry = ttk.Entry(input_frame)
        self.cantidad_entry.grid(row=2, column=1, padx=10, pady=5)

        # Botón para agregar producto
        agregar_btn = ttk.Button(input_frame, text="Agregar Producto")
        agregar_btn.grid(row=3, column=0, columnspan=2, pady=10)
        """

# Para iniciar la aplicación:
if __name__ == "__main__":
    # Aquí puedes pasar de manera segura el parámetro 'themename' (u otros kwargs)
    app = MiAplicacion(themename="superhero")
    app.mainloop()
