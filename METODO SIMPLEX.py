import tkinter as tk
from tkinter import Entry, Label, Button, Frame, Scrollbar, Text, messagebox
from fractions import Fraction

class SimplexGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Método Simplex")

        self.numero_variables = 0
        self.numero_restricciones = 0
        self.funcion_obj = []
        self.restricciones = []
        self.cr = []

        self.frame_datos = Frame(root)
        self.frame_datos.pack(pady=0)

        self.label_variables = Label(self.frame_datos, text="Número de variables:")
        self.label_variables.pack()
        self.entry_variables = Entry(self.frame_datos)
        self.entry_variables.pack()

        self.label_restricciones = Label(self.frame_datos, text="Número de restricciones:")
        self.label_restricciones.pack()
        self.entry_restricciones = Entry(self.frame_datos)
        self.entry_restricciones.pack()

        self.btn_datos = Button(self.frame_datos, text="Ingresar Datos", command=self.ingresar_datos)
        self.btn_datos.pack()

        self.frame_resultados = Frame(root)
        self.frame_resultados.pack(pady=0)

        self.scrollbar = Scrollbar(self.frame_resultados)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_resultados = Text(self.frame_resultados, wrap=tk.NONE, yscrollcommand=self.scrollbar.set, width=100, height=20)
        self.text_resultados.pack(fill=tk.BOTH)
        self.scrollbar.config(command=self.text_resultados.yview)

    def ingresar_datos(self):
        try:
            self.numero_variables = int(self.entry_variables.get())
            self.numero_restricciones = int(self.entry_restricciones.get())

            self.frame_datos.destroy()

            self.frame_coef_obj = Frame(self.root)
            self.frame_coef_obj.pack(pady=10)

            self.label_coef_obj = Label(self.frame_coef_obj, text="Coeficientes de la función objetivo:")
            self.label_coef_obj.pack()

            for i in range(self.numero_variables):
                label = Label(self.frame_coef_obj, text=f"Coeficiente de x{i+1}:")
                label.pack()
                entry = Entry(self.frame_coef_obj)
                entry.pack()
                self.funcion_obj.append(entry)

            self.frame_coef_res = Frame(self.root)
            self.frame_coef_res.pack(pady=10)

            self.label_coef_res = Label(self.frame_coef_res, text="Coeficientes de las restricciones:")
            self.label_coef_res.pack()

            for j in range(self.numero_restricciones):
                frame_restriccion = Frame(self.frame_coef_res)
                frame_restriccion.pack()
                label_restriccion = Label(frame_restriccion, text=f"Restricción {j+1}:")
                label_restriccion.pack(side=tk.LEFT)

                restriccion = []
                for i in range(self.numero_variables):
                    entry = Entry(frame_restriccion)
                    entry.pack(side=tk.LEFT)
                    restriccion.append(entry)
                self.restricciones.append(restriccion)

            self.frame_cr = Frame(self.root)
            self.frame_cr.pack(pady=10)

            self.label_cr = Label(self.frame_cr, text="Coeficientes de las restricciones (CR):")
            self.label_cr.pack()

            for i in range(self.numero_restricciones):
                label = Label(self.frame_cr, text=f"CR {i+1}:")
                label.pack()
                entry = Entry(self.frame_cr)
                entry.pack()
                self.cr.append(entry)

            self.btn_calcular = Button(self.root, text="Calcular Simplex", command=self.calcular_simplex)
            self.btn_calcular.pack()
        except ValueError:
            messagebox.showerror("Error", "Ingrese números válidos para el número de variables y restricciones.")

    def calcular_simplex(self):
        funcion_obj_Z = [Fraction(entry.get()) for entry in self.funcion_obj]
        restricciones = [[Fraction(entry.get()) for entry in restricción] for restricción in self.restricciones]
        cr = [Fraction(entry.get()) for entry in self.cr]

        self.text_resultados.delete(1.0, tk.END)  # Borra el contenido anterior

        tableroInicial = self.nuevoModelo(funcion_obj_Z, restricciones, cr)
        tableroSimplex = [fila.copy() for fila in tableroInicial]  # Copia del tablero inicial
        iteracion = 1

        # Mostrar el tablero inicial
        self.text_resultados.insert(tk.END, "Tablero Inicial:\n")

        for fila in tableroInicial:
            fila_nombre = f"s{tableroInicial.index(fila)+1}" if tableroInicial.index(fila) < self.numero_restricciones else f"x{tableroInicial.index(fila)-self.numero_restricciones+1}"
            # Convierte los elementos a fracciones antes de mostrarlos
            fila_valores = [fila_nombre] + [Fraction(elemento).limit_denominator(100) if isinstance(elemento, Fraction) else elemento for elemento in fila]
            self.text_resultados.insert(tk.END, "\t".join(map(str, fila_valores)) + "\n")

        while self.tieneElementosNegativos(tableroSimplex[-1]):
            funcion_Z = tableroSimplex[-1]
            columnaPivote = funcion_Z.index(min(funcion_Z))

            ratios = []
            for fila in tableroSimplex[:-1]:
                if fila[columnaPivote] > 0:
                    ratio = fila[-1] / fila[columnaPivote]
                    # Redondea los ratios a fracciones con denominador limitado
                    ratio_fraccion = Fraction(ratio).limit_denominator(100)
                    ratios.append(ratio_fraccion)
                else:
                    ratios.append(float('inf'))

            filaPivote = ratios.index(min(ratios))
            elementoPivote = tableroSimplex[filaPivote][columnaPivote]

            for i in range(len(tableroSimplex[filaPivote])):
                tableroSimplex[filaPivote][i] /= elementoPivote

            for i in range(len(tableroSimplex)):
                if i != filaPivote:
                    factor = tableroSimplex[i][columnaPivote]
                    for j in range(len(tableroSimplex[i])):
                        tableroSimplex[i][j] -= factor * tableroSimplex[filaPivote][j]

            self.text_resultados.insert(tk.END, f"\nIteración {iteracion}:\n")

            nombres_columnas = ["VB"] + ["Z"] + [f"x{i+1}" for i in range(self.numero_variables)] + [f"s{i+1}" for i in range(self.numero_restricciones)] + ["CR"]
            self.text_resultados.insert(tk.END, "\t".join(nombres_columnas) + "\n")

            for fila in tableroSimplex:
                fila_nombre = f"s{tableroSimplex.index(fila)+1}" if tableroSimplex.index(fila) < self.numero_restricciones else f"x{tableroSimplex.index(fila)-self.numero_restricciones+1}"
                # Convierte los elementos a fracciones antes de mostrarlos
                fila_valores = [fila_nombre] + [Fraction(elemento).limit_denominator(100) if isinstance(elemento, Fraction) else elemento for elemento in fila]
                self.text_resultados.insert(tk.END, "\t".join(map(str, fila_valores)) + "\n")

            iteracion += 1

        valor_optimo = tableroSimplex[-1][-1]  # Usa el valor óptimo como una fracción
        self.text_resultados.insert(tk.END, f"\nValor Óptimo = {valor_optimo}\n\n")

    def nuevoModelo(self, funcion_obj_Z, restricciones, cr):
        tableroSimplex = []
        variable_holgura = [[1 if j == i else 0 for j in range(self.numero_restricciones)] for i in range(self.numero_variables)]

        # Verifica si la longitud de cr es igual al número de restricciones
        if len(cr) != self.numero_restricciones:
            messagebox.showerror("Error", "La longitud de la lista CR debe ser igual al número de restricciones.")
            return None  # Retorna None para indicar un error

        for i in range(self.numero_restricciones):
            fila = [0] + restricciones[i] + variable_holgura[i] + [cr[i]]
            tableroSimplex.append(fila)
        funcion_Z = [elemento * -1 for elemento in funcion_obj_Z]
        fila = [1] + funcion_Z + [0] * self.numero_restricciones + [0]
        tableroSimplex.append(fila)
        return tableroSimplex

    def tieneElementosNegativos(self, fila):
        for elemento in fila:
            if elemento < 0:
                return True
        return False

    def metodoSimplex(self, tableroSimplex):
        iteracion = 1
        while self.tieneElementosNegativos(tableroSimplex[-1]):
            funcion_Z = tableroSimplex[-1]
            columnaPivote = funcion_Z.index(min(funcion_Z))

            ratios = []
            for fila in tableroSimplex[:-1]:
                if fila[columnaPivote] > 0:
                    ratio = fila[-1] / fila[columnaPivote]
                    ratio_redondeado = round(ratio, 2)
                    ratios.append(ratio_redondeado)
                else:
                    ratios.append(float('inf'))

            filaPivote = ratios.index(min(ratios))
            elementoPivote = tableroSimplex[filaPivote][columnaPivote]

            for i in range(len(tableroSimplex[filaPivote])):
                tableroSimplex[filaPivote][i] /= elementoPivote

            for i in range(len(tableroSimplex)):
                if i != filaPivote:
                    factor = tableroSimplex[i][columnaPivote]
                    for j in range(len(tableroSimplex[i])):
                        tableroSimplex[i][j] = round(tableroSimplex[i][j] - factor * tableroSimplex[filaPivote][j], 2)

            iteracion += 1

        return tableroSimplex

if __name__ == "__main__":
    root = tk.Tk()
    app = SimplexGUI(root)
    root.mainloop()
