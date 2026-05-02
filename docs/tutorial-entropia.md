# Análisis de Entropía

**Nivel**: Intermedio | **Tiempo**: 2 horas  
**Requisitos previos**: [Introducción a Think Anywhere](tutorial-basico.md), NumPy básico, teoría de probabilidad

---

## Entropía de Shannon: Las Matemáticas

### Definición

Para una distribución de probabilidades discreta `p = [p₁, p₂, ..., pₙ]`:

```
H(p) = -Σ pᵢ · log₂(pᵢ)
         i
```

### Entropía Normalizada

Para comparar entre distribuciones de distintos tamaños, normalizamos por la entropía máxima posible:

```
H_norm(p) = H(p) / log₂(n)
```

Esto da `H_norm ∈ [0, 1]`:
- **0** → certeza perfecta (un token tiene p ≈ 1)
- **1** → máxima incertidumbre (distribución uniforme)

### Ejemplos Resueltos

```python
import numpy as np

def entropia_normalizada(probs):
    probs = np.clip(probs, 1e-10, 1.0)
    H = -np.sum(probs * np.log2(probs))
    return H / np.log2(len(probs))

# Caso 1: Seguro
p1 = [0.95, 0.03, 0.02]
print(f"Seguro:      H = {entropia_normalizada(p1):.3f}")  # ≈ 0.22

# Caso 2: Dos opciones en competencia
p2 = [0.5, 0.4, 0.1]
print(f"Compitiendo: H = {entropia_normalizada(p2):.3f}")  # ≈ 0.85

# Caso 3: Uniforme (máxima incertidumbre)
p3 = [0.33, 0.33, 0.34]
print(f"Uniforme:    H = {entropia_normalizada(p3):.3f}")  # ≈ 1.00
```

---

## Por Qué la Entropía Funciona como Activador

Cuando un modelo asigna probabilidades casi iguales a múltiples completions, está genuinamente indeciso. Cualquier elección sería algo arbitraria — exactamente el momento donde el razonamiento explícito ayuda.

Observación empírica en 1000 generaciones de código:

| Rango de Entropía | % de Tokens | Interpretación |
|-------------------|-------------|----------------|
| `[0.0, 0.3)` | ~65% | Tokens sintácticos/obvios (`def`, `return`, `:`) |
| `[0.3, 0.7)` | ~25% | Elecciones moderadas (nombres de variables, operadores) |
| `[0.7, 1.0]` | ~10% | Bifurcaciones reales: algoritmo, estructura de datos, naming |

Think Anywhere actúa solo en ese **10% de tokens** donde razonar realmente importa.

---

## Visualizando la Entropía Durante la Generación

```python
from think_anywhere import EntropyDetector
import matplotlib.pyplot as plt

detector = EntropyDetector(threshold=0.7)

# Secuencia de tokens con sus distribuciones
# (en producción, vienen de los logprobs del modelo)
secuencia = [
    {"token": "def",        "probs": [0.92, 0.04, 0.04]},
    {"token": "quicksort",  "probs": [0.41, 0.30, 0.29]},  # ← ALTA
    {"token": "(",          "probs": [0.98, 0.01, 0.01]},
    {"token": "arr",        "probs": [0.55, 0.30, 0.15]},
    {"token": "pivote",     "probs": [0.38, 0.35, 0.27]},  # ← ALTA
    {"token": "=",          "probs": [0.96, 0.02, 0.02]},
]

entropias = [
    detector.calculate_entropy(item["probs"])
    for item in secuencia
]
tokens = [item["token"] for item in secuencia]

plt.figure(figsize=(10, 4))
colores = ["#ff6b6b" if e >= 0.7 else "#6bcf7f" for e in entropias]
plt.bar(tokens, entropias, color=colores, edgecolor="black")
plt.axhline(y=0.7, color="red", linestyle="--", label="Umbral (0.7)")
plt.ylim(0, 1.1)
plt.ylabel("Entropía Normalizada")
plt.title("Entropía por Token Durante la Generación de Código")
plt.legend()
plt.tight_layout()
plt.savefig("entropy_analysis.png", dpi=150)
print("Guardado en entropy_analysis.png")
```

Las **barras rojas** indican dónde se activarían los bloques `<THINK>`.

---

## Selección del Umbral

El umbral controla con qué frecuencia se activa el razonamiento. Hay un trade-off fundamental:

| Umbral | Frecuencia de Razonamiento | Costo en Tokens | Riesgo |
|--------|---------------------------|-----------------|--------|
| 0.3 | Muy frecuente | Alto | Sobre-pensar código simple |
| 0.5 | Balanceado | Medio | — |
| **0.7** | Selectivo | **Bajo** | **Recomendado** |
| 0.9 | Raro | Muy bajo | Perderse decisiones importantes |

### Estrategia de Umbral Adaptativo

```python
def umbral_adaptativo(tipo_tarea):
    """
    Ajusta el umbral según el tipo de tarea.
    Mayor complejidad → umbral más bajo (razonar más).
    """
    if tipo_tarea == "diseño_algoritmo":
        return 0.5   # Razonar más — muchas decisiones de diseño
    elif tipo_tarea == "boilerplate":
        return 0.85  # Razonar menos — pocas decisiones reales
    else:
        return 0.7   # Por defecto
```

---

## Estadísticas de Entropía en Múltiples Generaciones

```python
from think_anywhere import ThinkingAgent

agent = ThinkingAgent(entropy_threshold=0.7)

prompts = [
    "Implementa quicksort",
    "Implementa búsqueda binaria",
    "Diseña una API REST",
    "Escribe una tabla hash",
    "Crea una capa de caché",
]

for prompt in prompts:
    agent.generate(prompt)

stats = agent.get_statistics()
print(stats.summary())
```

**Ejemplo de salida**:
```
Think Anywhere Statistics:
  Total generations: 5
  Total reasoning blocks: 8
  Avg reasoning/generation: 1.60
  Avg entropy at reasoning: 0.776
  Entropy range: [0.721, 0.831]
  High-entropy events: 8
  Token efficiency: 37.8%
```

---

## Insight Clave: Teoría de la Información y Código

La razón por la que el razonamiento basado en entropía funciona específicamente para generación de código es que el código tiene una **estructura de incertidumbre bimodal**:

1. **Baja incertidumbre** — tokens sintácticos (keywords, puntuación, nombres obvios): el modelo está casi seguro
2. **Alta incertidumbre** — decisiones semánticas (elección de algoritmo, estructura de datos, estrategia de naming): múltiples opciones válidas con probabilidad similar

Think Anywhere explota esta estructura. CoT razona también sobre las partes de baja incertidumbre — desperdiciando tokens. Think Anywhere razona *solo* en los puntos de decisión semántica.

---

## Próximos Pasos

- **Avanzado**: [Entrenamiento Personalizado](tutorial-avanzado.md) — construye un modelo que active el razonamiento de forma nativa, sin prompting

---

**Paper Original**: [arXiv:2603.29957](https://arxiv.org/pdf/2603.29957)  
**Video**: [Presentación en YouTube](https://www.youtube.com/watch?v=wXGUiMfgL18)
