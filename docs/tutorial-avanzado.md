# Entrenamiento Personalizado

**Nivel**: Avanzado | **Tiempo**: Día completo  
**Requisitos previos**: [Análisis de Entropía](tutorial-entropia.md), PyTorch, familiaridad con LoRA y RLHF

---

## Visión General

La implementación actual usa **prompt engineering** para guiar a los modelos hacia el razonamiento dinámico. Funciona bien, pero depende de que el modelo siga instrucciones — es una capa conductual, no una capacidad del modelo.

El paper original de Think Anywhere propone **entrenar** el modelo para razonar de forma nativa, sin necesitar prompts estructurados. Este tutorial describe el pipeline completo de entrenamiento en tres etapas.

> ⚠️ **Nota**: El pipeline de entrenamiento requiere acceso a los pesos del modelo. Este tutorial describe la metodología con propósitos de investigación. La implementación demo usa únicamente prompt engineering.

---

## Etapa 1: Tokens Personalizados

### ¿Por Qué Tokens Personalizados?

En lugar de usar los textos `<THINK>` y `</THINK>`, el paper introduce tokens de vocabulario dedicados:

```
<THINK_ANYWHERE_START>
<THINK_ANYWHERE_END>
```

Esto separa los marcadores de razonamiento del texto regular, haciéndolos inequívocos para el modelo.

### Inicialización del Embedding

Un detalle clave: estos tokens **no se inicializan aleatoriamente**. El paper usa una inicialización semántica:

```python
# Implementación conceptual
embedding_think = (
    0.5 * media_embeddings(["think", "any", "where"])
    + 0.5 * embedding("<start_token>")
)
```

**Por qué**: La inicialización aleatoria requeriría que el modelo aprenda desde cero qué *significa* el token. La inicialización semántica le da al modelo ventaja — ya sabe que estos tokens están relacionados con "pensar" y con límites estructurales.

---

## Etapa 2: Supervised Fine-Tuning (SFT) con LoRA

### Generar Datos de Entrenamiento

Usa un modelo "teacher" fuerte (ej. GPT-4) para producir ~5000 ejemplos con el patrón:

```
código...
<THINK>
razonamiento...
</THINK>
continúa el código...
```

El teacher debe insertar bloques `<THINK>` en puntos de decisión genuinamente complejos — selección de algoritmo, elección de estructura de datos, manejo de casos borde — no en pasos triviales.

### Aplicar LoRA

```python
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM

# Cargar modelo base
model = AutoModelForCausalLM.from_pretrained("tu-modelo-base")

# Añadir nuevos tokens
tokenizer.add_tokens(["<THINK_ANYWHERE_START>", "<THINK_ANYWHERE_END>"])
model.resize_token_embeddings(len(tokenizer))

# Inicializar embeddings semánticamente
with torch.no_grad():
    palabras_think = ["think", "any", "where"]
    emb_medio = media([model.get_input_embeddings()(
        tokenizer.encode(w, return_tensors="pt")
    ) for w in palabras_think])
    emb_inicio = model.get_input_embeddings()(
        tokenizer.encode("<s>", return_tensors="pt")
    )
    nuevo_emb = 0.5 * emb_medio + 0.5 * emb_inicio
    model.get_input_embeddings().weight[-2] = nuevo_emb  # Token START

# Configurar LoRA
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# Entrenables: ~0.5% de los parámetros
```

### Entrenar con Datos SFT

```python
from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir="./sft-think-anywhere",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    warmup_steps=100,
    logging_steps=10,
    save_steps=500,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=sft_dataset,  # Tus ejemplos generados
)

trainer.train()
```

**Resultado tras SFT**: El modelo insertará bloques `<THINK>`, pero no consistentemente en los momentos correctos. SFT solo muestra mejora limitada — esto es esperado.

---

## Etapa 3: Reinforcement Learning con GRPO

SFT enseña la *forma* (cómo escribir bloques `<THINK>`). GRPO enseña *cuándo* usarlos, optimizando para la correctitud.

### Función de Recompensa

La recompensa tiene dos componentes:

```python
def calcular_recompensa(salida_generada, salida_esperada):
    """
    Recompensa = 0.1 * puntuación_estructura + 0.9 * puntuación_correctitud
    """
    punt_estructura = evaluar_estructura(salida_generada)
    punt_correctitud = evaluar_correctitud(salida_generada, salida_esperada)

    return 0.1 * punt_estructura + 0.9 * punt_correctitud


def evaluar_estructura(salida):
    """
    Verificar validez estructural de los bloques THINK.
    - Tiene al menos un bloque THINK (0.33)
    - Todos los bloques THINK cerrados correctamente (0.33)
    - Al menos un bloque de razonamiento inicial (0.33)
    """
    punt = 0.0
    tiene_think = "<THINK>" in salida
    balanceado = salida.count("<THINK>") == salida.count("</THINK>")
    tiene_intro = salida.strip().startswith("<THINK>")

    if tiene_think:
        punt += 0.33
    if balanceado:
        punt += 0.33
    if tiene_intro:
        punt += 0.34

    return punt


def evaluar_correctitud(salida, esperado):
    """
    Ejecutar el código generado contra los casos de prueba.
    Binario: pasa todos (1.0) o no (0.0).
    """
    codigo = extraer_codigo(salida)  # Eliminar bloques THINK
    return ejecutar_tests(codigo, esperado)
```

### ¿Por Qué 10% / 90%?

El peso del 90% en correctitud asegura que el modelo se centre en escribir código que **funcione**. El 10% en estructura evita que el modelo aprenda a simplemente omitir bloques `<THINK>` para maximizar el 90%.

Esta es una decisión de diseño crítica: sin el término de estructura, GRPO probablemente convergiría a no razonar nunca (más simple, frecuentemente correcto). Con él, el modelo aprende que razonar es esperado y recompensado cuando lleva a código correcto.

---

## Resultados Esperados

| Etapa | HumanEval | MBPP | Eficiencia de Tokens |
|-------|-----------|------|----------------------|
| Modelo base | 67.3% | 72.1% | baseline |
| + SFT | 71.2% | 75.8% | -5% |
| + GRPO | **79.7%** | **84.1%** | **-30%** |

La etapa GRPO proporciona la mayor mejora. SFT solo es insuficiente — el modelo aprende el formato pero no el juicio de *cuándo* razonar.

---

## Evaluación: Reproducir Benchmarks

Una vez entrenado, evalúa contra los benchmarks estándar:

```python
from think_anywhere.evaluation import HumanEvalRunner, MBPPRunner

runner = HumanEvalRunner(agent=agente_entrenado)
resultados = runner.run(n_problems=164, temperature=0.2)

print(f"Pass@1: {resultados.pass_at_1:.1%}")
print(f"Tokens promedio: {resultados.avg_tokens:.0f}")
print(f"Bloques THINK promedio: {resultados.avg_think_blocks:.2f}")
```

---

## Direcciones Futuras

1. **GRPO con control de entropía**: Solo computar recompensa de THINK cuando la entropía de logprob era realmente alta en el punto de inserción — esto afina la señal de entrenamiento
2. **Evaluación multi-lenguaje**: Benchmarks en Python, JavaScript, Rust para probar generalización
3. **Compresión de razonamiento**: Bloques `<THINK>` más cortos con igual o mejor correctitud

---

## Trabajo Relacionado

- **GRPO** (Group Relative Policy Optimization): Usado aquí para entrenamiento RL
- **LoRA** (Hu et al., 2022): Adaptación de bajo rango para fine-tuning eficiente
- **Pipeline SFT → RLHF**: Patrón estándar, aquí adaptado para correctitud de código en lugar de preferencias humanas

---

**Paper Original**: [arXiv:2603.29957](https://arxiv.org/pdf/2603.29957)  
**Video**: [Presentación en YouTube](https://www.youtube.com/watch?v=wXGUiMfgL18)
