# 🍅 Pomodoro Focus Timer

Aplicación de temporizador Pomodoro local con interfaz futurista / profesional construida con Python puro (`tkinter`).

---

## ✨ Características

| Característica | Detalle |
|---|---|
| 🎨 UI futurista | Tema oscuro con arco de progreso circular y colores neón |
| ⏱ Ciclos automáticos | Work → Short Break → (×4) → Long Break |
| 🔧 Tiempos configurables | Spinboxes inline para ajustar minutos sin tocar código |
| 🔔 Notificaciones sonoras | Beeps del sistema al finalizar cada sesión (Windows) |
| 💡 Indicadores visuales | Puntos de progreso de ciclo, flash de color y etiqueta de modo |
| 📊 Estadísticas del día | Contador de pomodoros completados en pantalla |

---

## 🚀 Uso

```bash
# No requiere dependencias externas, sólo Python 3.8+
python pomodoro.py
```

---

## ⌨️ Controles

| Botón | Acción |
|---|---|
| ▶ START | Inicia la cuenta regresiva |
| ⏸ PAUSE | Pausa / reanuda el timer |
| ↺ RESET | Reinicia al inicio del ciclo de trabajo |

---

## 🎨 Paleta de colores

| Modo | Color |
|---|---|
| FOCUS SESSION | `#00f5ff` cyan |
| SHORT BREAK | `#a259ff` violet |
| LONG BREAK | `#00ff88` green |

---

## 📁 Estructura

```
pomodoro/
├── pomodoro.py   ← aplicación principal
└── README.md
```
