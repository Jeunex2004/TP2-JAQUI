import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class GraficosMixin:
    def dibujar_grafico_embebido(self, serie, titulo, frame_destino):
        for widget in frame_destino.winfo_children():
            widget.destroy()

        if not serie or len(serie) == 0:
            return

        fig = Figure(figsize=(7, 4), dpi=100)
        
        ax1 = fig.add_subplot(121)
        if min(serie) >= 0.0 and max(serie) <= 1.0:
            rango_hist = (0.0, 1.0)
        else:
            rango_hist = None

        n, bins, barras = ax1.hist(serie, bins=10, range=rango_hist, edgecolor='black', alpha=0.7)
        ax1.axhline(y=len(serie)/10, color='r', linestyle='dashed', label='F. Esperada')
        ax1.set_title("Histograma", fontsize=10)
        ax1.legend(fontsize=8)

        ax2 = fig.add_subplot(122)
        puntos_scatter = ax2.scatter(serie[:-1], serie[1:], alpha=0.5, s=10)
        ax2.set_title("Dispersión (Rezago 1)", fontsize=10)
        
        fig.suptitle(titulo, fontsize=12, fontweight='bold')
        fig.tight_layout()

        annot1 = ax1.annotate("", xy=(0,0), xytext=(0, 15), textcoords="offset points",
                              bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="black", alpha=1.0),
                              arrowprops=dict(arrowstyle="->", connectionstyle="arc3"), zorder=100)
        annot1.set_clip_on(False)

        annot2 = ax2.annotate("", xy=(0,0), xytext=(0, 15), textcoords="offset points",
                              bbox=dict(boxstyle="round,pad=0.3", fc="lightcyan", ec="black", alpha=1.0),
                              arrowprops=dict(arrowstyle="->", connectionstyle="arc3"), zorder=100)
        annot2.set_clip_on(False)

        def on_hover(event):
            if event.inaxes is None:
                if annot1.get_visible() or annot2.get_visible():
                    annot1.set_visible(False)
                    annot2.set_visible(False)
                    if self.canvas_actual: self.canvas_actual.draw_idle()
                return

            if event.inaxes == ax1:
                annot2.set_visible(False)
                for barra in barras:
                    contiene, _ = barra.contains(event)
                    if contiene:
                        x = barra.get_x()
                        ancho = barra.get_width()
                        y = barra.get_height()
                        annot1.xy = (x + ancho / 2, y)
                        
                        if (x + ancho / 2) > (ax1.get_xlim()[1] * 0.6):
                            annot1.set_ha('right')
                        else:
                            annot1.set_ha('left')

                        texto = f"Frecuencia: {int(y)}\nIntervalo: [{x:.2f}, {x+ancho:.2f}]"
                        annot1.set_text(texto)
                        annot1.set_visible(True)
                        if self.canvas_actual: self.canvas_actual.draw_idle()
                        return
                
                if annot1.get_visible():
                    annot1.set_visible(False)
                    if self.canvas_actual: self.canvas_actual.draw_idle()

            elif event.inaxes == ax2:
                annot1.set_visible(False)
                contiene, indices = puntos_scatter.contains(event)
                if contiene and len(indices["ind"]) > 0:
                    idx = indices["ind"][0]
                    pos = puntos_scatter.get_offsets()[idx]
                    annot2.xy = pos
                    
                    if pos[0] > (ax2.get_xlim()[1] * 0.6):
                        annot2.set_ha('right')
                    else:
                        annot2.set_ha('left')
                        
                    texto = f"U_i: {pos[0]:.4f}\nU_i+1: {pos[1]:.4f}"
                    annot2.set_text(texto)
                    annot2.set_visible(True)
                    if self.canvas_actual: self.canvas_actual.draw_idle()
                else:
                    if annot2.get_visible():
                        annot2.set_visible(False)
                        if self.canvas_actual: self.canvas_actual.draw_idle()

        self.canvas_actual = FigureCanvasTkAgg(fig, master=frame_destino)
        self.canvas_actual.draw()
        self.canvas_actual.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas_actual.mpl_connect("motion_notify_event", on_hover)