import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

P = ["Solicitante\n(navegador)", "rutas_incidencias\n/rechazar", "auth\nlogin_requerido", "servicios\nrechazar_solucion", "dominio\nvalidar_motivo", "SQLite"]
X = [2.6, 4.55, 6.5, 8.45, 10.4, 12.35]
fig, ax = plt.subplots(figsize=(13, 9.6))
ax.set_xlim(-0.3, 13.4); ax.set_ylim(-21.2, 1.2); ax.axis("off")
TINTA, GRIS, ACC = "#1e2a36", "#52606d", "#c4540a"
for x, p in zip(X, P):
    ax.add_patch(FancyBboxPatch((x-0.85, 0), 1.7, 0.95, boxstyle="round,pad=0.02", fc="#eef1f4", ec=TINTA, lw=1.2))
    ax.text(x, 0.47, p, ha="center", va="center", fontsize=8.6, fontweight="bold", color=TINTA)
    ax.plot([x, x], [0, -20.4], ls=(0, (4, 3)), color=GRIS, lw=0.9)
y = [-0.9]
def msg(a, b, texto, dy=1.0, ret=False, color=TINTA):
    y[0] -= dy
    ax.annotate("", xy=(X[b], y[0]), xytext=(X[a], y[0]),
                arrowprops=dict(arrowstyle="->", color=color, lw=1.1, ls="--" if ret else "-"))
    xm = (X[a] + X[b]) / 2 if a != b else X[a] + 0.9
    ax.text(xm, y[0] + 0.12, texto, ha="center", va="bottom", fontsize=7.9, color=color, bbox=dict(fc="white", ec="none", pad=0.6))
def propio(a, texto, color=TINTA):
    y[0] -= 1.0
    x = X[a]
    ax.plot([x, x + 0.45, x + 0.45, x + 0.05], [y[0] + 0.25, y[0] + 0.25, y[0] - 0.2, y[0] - 0.2], color=color, lw=1.1)
    ax.annotate("", xy=(x + 0.02, y[0] - 0.2), xytext=(x + 0.2, y[0] - 0.2), arrowprops=dict(arrowstyle="->", color=color, lw=1.1))
    ax.text(x + 0.55, y[0], texto, ha="left", va="center", fontsize=7.9, color=color)
def marco(y0, y1, titulo, color=GRIS):
    ax.add_patch(Rectangle((-0.25, y1), 13.55, y0 - y1, fill=False, ec=color, lw=1.0))
    ax.text(-0.15, (y0 + y1) / 2, titulo, fontsize=8, fontweight="bold", color=color, va="center", wrap=True,
            bbox=dict(fc="white", ec=color, lw=0.8, pad=2))

msg(0, 1, "POST /incidencias/INC-0001/rechazar  (motivo)")
msg(1, 2, "verificar sesión y rol SOLICITANTE")
y0 = y[0] - 0.35
msg(2, 0, "sin sesión → 302 /login · otro rol → 403", ret=True, color=ACC)
marco(y0, y[0] - 0.35, "alt\nacceso inválido", ACC)
y[0] -= 0.3
msg(1, 3, "rechazar_solucion(codigo, motivo, g.usuario, reloj)")
msg(3, 5, "BEGIN IMMEDIATE")
msg(3, 5, "SELECT id, estado, solicitante_id WHERE codigo = ?")
msg(5, 3, "fila", ret=True)
y1 = y[0] - 0.35
msg(3, 5, "no existe o no es del dueño → ErrorNoEncontrada → ROLLBACK", color=ACC)
msg(3, 5, "estado ≠ PENDIENTE_VALIDACION → ErrorEstado → ROLLBACK", color=ACC)
msg(3, 4, "validar_motivo(motivo)  (recorta espacios, 10–300)")
msg(4, 3, "fuera de límite → ErrorValidacion → ROLLBACK", ret=True, color=ACC)
marco(y1, y[0] - 0.35, "alt\nrechazo sin\ncambios", ACC)
y[0] -= 0.3
y2 = y[0] - 0.35
msg(3, 5, "UPDATE incidencias SET estado = 'EN_ATENCION'  (mismo técnico)")
msg(3, 5, "INSERT eventos (RECHAZAR, autor, fecha UTC, PEND_VALIDACION → EN_ATENCION, motivo)")
msg(3, 5, "COMMIT")
marco(y2, y[0] - 0.35, "transacción\nestado + evento\njuntos", TINTA)
y[0] -= 0.3
msg(3, 1, "ok", ret=True)
msg(1, 0, "302 → /incidencias/mis-reportes  (o 404 / 409 / 400 con el mensaje)", ret=True)
ax.text(6.6, -20.9, "La solución anterior y la asignación no se modifican; los triggers impiden editar o borrar eventos y soluciones.",
        ha="center", fontsize=8, color=GRIS, style="italic")
plt.savefig("secuencia.png", dpi=190, bbox_inches="tight", facecolor="white")
