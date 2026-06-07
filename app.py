import ttkbootstrap as ttk
import sqlite3
from ttkbootstrap.dialogs import Messagebox
import ctypes

# 1. TRUCO PARA LA BARRA DE TAREAS (Agregar aquí)
try:
    myappid = 'hojalata.app.sqlite.v1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

class MiAplicacion(ttk.Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)      
        self.title("Mi App con SQLite")
        self.geometry("1800x1000")

        # Agregar un icono a la app
        self.iconbitmap("Hojalata.ico")
        
        # Inicializa la base de datos y la interfaz
        self.setup_database()
        self.create_widgets()
        self.load_products()

    def setup_database(self):
        self.conn = sqlite3.connect("inventario_simple.db")
        self.conn.row_factory = sqlite3.Row # este comando permite trabajar con los nombre de campo, NO sus indices
        self.cursor = self.conn.cursor()

        # Crear tabla productos
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                precio REAL NOT NULL,
                cantidad INTEGER DEFAULT 1
            )
        """)
        self.conn.commit()

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        title_label = ttk.Label(
            main_frame, 
            text="Gestión de Inventario", 
            font=("Helvetica", 18)
        )
        title_label.pack(pady=(0, 20))

        input_frame = ttk.LabelFrame(main_frame, text="Nuevo Producto")
        input_frame.pack(fill="x", pady=(0, 20), ipadx=15, ipady=15)

        # Campos de entrada
        # label nombre
        ttk.Label(input_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        # texto: nombre
        self.nombre_entry = ttk.StringVar()
        self.txt_nombre = ttk.Entry(input_frame, textvariable=self.nombre_entry, width=20)
        self.txt_nombre.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.txt_nombre.focus_set()

        # label precio
        ttk.Label(input_frame, text="Precio:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        # texto: precio
        self.precio_entry = ttk.DoubleVar()
        self.txt_precio = ttk.Entry(input_frame, textvariable=self.precio_entry, width=15)
        self.txt_precio.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # label cantidad
        ttk.Label(input_frame, text="Cantidad:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        # texto: cantidad
        self.cantidad_entry = ttk.IntVar(value=1)
        self.txt_cantidad = ttk.Entry(input_frame, textvariable=self.cantidad_entry, width=10)
        self.txt_cantidad.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        # Botón para agregar producto
        add_button = ttk.Button(
            input_frame, 
            text="Agregar Producto", 
            command=self.agregar_producto,
            style="success.TButton"
        )
        add_button.grid(row=0, column=6, padx=10, pady=5)

                # Frame para mostrar productos
        list_frame = ttk.LabelFrame(main_frame, text="Lista de productos")
        list_frame.pack(fill="both", expand=True)

        # Crear treeview para la lista de productos
        columns = ("id", "nombre", "precio", "cantidad")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)

        # Definir encabezados de las columnas
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("precio", text="Precio")
        self.tree.heading("cantidad", text="Cantidad")

        # Definir anchos de las columnas
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nombre", width=250, anchor="w")
        self.tree.column("precio", width=100, anchor="e")
        self.tree.column("cantidad", width=80, anchor="center")

        # Scrollbar 
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # === CORRECCIÓN DE ORDEN DE EMPAQUETADO ===
        # 1. Empaquetamos la barra PRIMERO a la derecha
        scrollbar.pack(side="right", fill="y")
        
        # 2. SEGUNDO empaquetamos el Treeview (ocupará todo el espacio restante hasta tocar la barra)
        self.tree.pack(side="left", fill="both", expand=True)

        # 3. AL FINAL creamos el botón de eliminar abajo de todo, fuera de la lista
        delete_frame = ttk.Frame(main_frame)
        delete_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(
            delete_frame,
            text="Eliminar producto",
            bootstyle="danger",
            command=self.delete_product
        ).pack(side="right")

        # Empaquetar el treeview
        self.tree.pack(fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def agregar_producto(self):
        """Agregar un nuevo producto"""
        nombre = self.nombre_entry.get().strip()
        cantidad = self.cantidad_entry.get()

        if not nombre:
            ttk.dialogs.Messagebox.show_error("El nombre del producto no puede estar vacio", "Error")
            return
        
        try:
            precio = float(self.txt_precio.get())
            if precio <= 0:
                raise ValueError("El precio no puede ser menor que cero")
        except:
            ttk.dialogs.Messagebox.show_error(
                "El precio debe ser mayor que cero",
                "Error"
            )
            return
    
        # inserta el registro en la base de datos
        self.cursor.execute(
            "INSERT INTO productos (nombre, precio, cantidad) VALUES (?, ?, ?)",
            (nombre, precio, cantidad)
        )
        self.conn.commit()
        
        self.load_products() # recarga los productos
        ttk.dialogs.Messagebox.show_info("Producto agregado correctamente", "Informacion")

        # limpiar campos
        self.nombre_entry.set("")
        self.precio_entry.set(0.0)
        self.cantidad_entry.set(1)
        self.txt_nombre.focus_set()

    def load_products(self):
        """Cargar los productos desde la base de datos"""
        # limpiar la tabla actual
        for item in self.tree.get_children():
            self.tree.delete(item)
        # cargar los productos desde la db
        self.cursor.execute("SELECT * FROM PRODUCTOS ORDER BY id DESC")
        productos = self.cursor.fetchall()
        # insertar los registros
        for producto in productos:
            self.tree.insert("", "end", values=(
                producto['id'],
                producto['nombre'],
                f"${producto['precio']:.2f}",
                producto['cantidad']
            ))

    def delete_product(self):
        """Eliminar el producto seleccionado"""
        # verifica si existe algun elemento seleccionado
        selection = self.tree.selection()
        if not selection:
            ttk.dialogs.Messagebox.show_warning("No existe ningun producto seleccionado", "Advertencia")
            return
        
        # obtener el elemento seleccionado
        item = self.tree.item(selection[0])
        product_id = item["values"][0]

        # confirmacion de la eliminacion
        confirm = ttk.dialogs.Messagebox.yesno(
            "¿Esta seguro que desea eliminar este producto?",
            "Confirmacion"
        )

        if confirm == "Yes":
            self.cursor.execute("DELETE FROM PRODUCTOS WHERE id = ?", (product_id,))
            self.conn.commit()

            # recarga los productos
            self.load_products();
            ttk.dialogs.Messagebox.show_info("Producto eliminado correctamente", "Informacion")

    def on_close(self):
        """Cierra la conexion a la base de datos"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            print("Conexion a la base de datos cerrada correctamente")
        self.destroy()

if __name__ == "__main__":
    app = MiAplicacion(themename="darkly")
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()