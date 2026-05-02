# Introducción a Think Anywhere

**Nivel**: Básico | **Tiempo**: 30 minutos  
**Requisitos previos**: Python básico, familiaridad con LLMs

---

## ¿Qué es Think Anywhere?

Cuando un LLM genera código, predice tokens uno a uno. En cada paso, el modelo asigna probabilidades a todos los posibles tokens siguientes. La mayoría de las veces, una opción es claramente dominante — **baja incertidumbre, baja entropía**. Pero a veces el modelo genuinamente no sabe qué camino tomar — **alta incertidumbre, alta entropía**.

**Think Anywhere** usa esta señal para activar el razonamiento *solo en esos momentos críticos*, en lugar de pensar por adelantado (Chain-of-Thought) o a intervalos fijos (Interleaved Thinking).

---

## Conceptos Fundamentales

### Entropía como Incertidumbre

La entropía de Shannon mide qué tan dispersa está una distribución de probabilidades:

```
H(X) = -Σ p(x) · log₂(p(x))
```

**Ejemplo**:

```python
# Seguro: una opción obvia
probs_seguro = [0.95, 0.03, 0.02]
# H ≈ 0.24  → Entropía baja → Continuar

# Inseguro: opciones en competencia
probs_inseguro = [0.35, 0.35, 0.30]
# H ≈ 0.99  → Entropía alta → PENSAR
```

### El Bloque THINK

Cuando se detecta alta entropía, el modelo inserta un bloque de razonamiento estructurado:

```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr

    # <THINK>
    # La estrategia del pivote afecta el peor caso.
    # Primer elemento → O(n²) en input ordenado.
    # Elemento medio → balanceado para casos comunes.
    # Elegir el del medio por simplicidad.
    # </THINK>

    pivot = arr[len(arr) // 2]
    ...
```

El razonamiento está **embebido en el código**, no separado de él.

---

## Tu Primer Experimento

### Paso 1: Instalar

```bash
git clone https://github.com/drhiidden/think-anywhere-demo.git
cd think-anywhere-demo
pip install -e .
```

### Paso 2: Ejecutar el ejemplo de quicksort

```bash
python examples/01_quicksort.py
```

**Salida esperada**:
```
Código generado:
def quicksort(arr):
    ...
    # <THINK>
    # La selección del pivote es crítica...
    # </THINK>
    pivot = arr[len(arr) // 2]
    ...

Puntos de razonamiento:
  💭 La selección del pivote es crítica para el rendimiento...

Tokens usados: 280
Eficiencia: 37.5% vs CoT
```

### Paso 3: Explorar el umbral

Cambia `entropy_threshold` y observa la diferencia:

```python
from think_anywhere import ThinkingAgent

# Conservador: razonar solo cuando muy inseguro
agente_alto = ThinkingAgent(entropy_threshold=0.9)

# Agresivo: razonar con más frecuencia
agente_bajo = ThinkingAgent(entropy_threshold=0.4)

prompt = "Implementa búsqueda binaria"

resultado_alto = agente_alto.generate(prompt)
resultado_bajo = agente_bajo.generate(prompt)

print(f"Umbral alto — bloques de razonamiento: {len(resultado_alto.thoughts)}")
print(f"Umbral bajo  — bloques de razonamiento: {len(resultado_bajo.thoughts)}")
```

---

## Comparación con Chain-of-Thought

Ejecuta el ejemplo de comparación para ver las tres estrategias lado a lado:

```bash
python examples/02_comparison.py
```

| Método | Razonamiento | Tokens | Cuándo |
|--------|-------------|--------|--------|
| Sin razonamiento | Ninguno | 150 | Nunca |
| CoT | Todo por adelantado | 450 | Siempre |
| Interleaved | Intervalos fijos | 380 | Periódicamente |
| **Think Anywhere** | **Adaptativo** | **280** | **Cuando se necesita** |

---

## Conclusiones Clave

- La **entropía** mide la incertidumbre del modelo token a token
- **Think Anywhere** solo activa el razonamiento cuando `H ≥ umbral`
- **Resultado**: menos tokens, mejor calidad de razonamiento
- El umbral es configurable — ajústalo para tu caso de uso

---

## Próximos Pasos

- **Intermedio**: [Análisis de Entropía](tutorial-entropia.md) — entiende las matemáticas y visualiza patrones de entropía
- **Avanzado**: [Entrenamiento Personalizado](tutorial-avanzado.md) — fine-tuning con LoRA y GRPO

---

**Paper Original**: [arXiv:2603.29957](https://arxiv.org/pdf/2603.29957)  
**Video**: [Presentación en YouTube](https://www.youtube.com/watch?v=wXGUiMfgL18)
