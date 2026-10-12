# Hero candidates (comparative evaluation)

Comparative hero experiments. Files here use **HHP project-to-art v2.1** (or CurveCodex as its generative engine)—**not** wired into the README hero until human approval. The banner currently in the README predates this folder; see the caption under the hero image.

| File | Description |
|------|-------------|
| `think-anywhere-hero-v2-frontera-candidate-a.png` | Direction A — fallback raster script (legacy) |
| `think-anywhere-hero-v2-frontera-curvecodex.png` | Direction A — **CurveCodex** v2 (seed 42, defaults) |
| `think-anywhere-hero-v3-frontera-curvecodex.png` | Direction A — **CurveCodex v3** — **APPROVED FOR FINAL COMPARISON** (ChatGPT 2026-10-12); not README hero yet |
| `*-external.png` | Optional: external generator using production prompt in hub brief |

Canonical brief (hub): HALETHEIA `.procontext/.../think-anywhere/THINK-ANYWHERE-ARTISTIC-PRODUCTION-TEST-v1.md`

Regenerate (preferred — from CurveCodex repo):

```bash
cd /path/to/CurveCodex && pip install -e .
python examples/03_regime_transition_banner.py -o /path/to/candidates/think-anywhere-hero-v3-frontera-curvecodex.png \
  --seed 20261012 --streamlines 190 --dpi 110 --transition-start 0.32 --transition-end 0.55 --linewidth 0.52
```

Legacy fallback: `python docs/images/candidates/generate_frontera_candidate.py`

Do **not** replace `docs/images/think-anywhere-hero.png` without explicit maintainer approval (external review: comparativa OK, swap not recommended yet).

### Reproducibility (CurveCodex)

| Field | v2 CurveCodex | v3 CurveCodex |
|-------|---------------|---------------|
| Motor repo | [drhiidden/CurveCodex](https://github.com/drhiidden/CurveCodex) @ `e3855c8` (or later tag) |
| PyPI package name | `art-with-equations` (`pip install -e .`) |
| Entrypoint | `examples/03_regime_transition_banner.py` |
| Seed | `42` (defaults) | `20261012` |
| Streamlines / transition | 140, 0.38–0.62 | 190, 0.32–0.55, linewidth 0.52, dpi 110 |
| Tests | `pytest tests/test_regime_fields.py` (file size + deterministic seed) |

**Artistic vs project data:** transition band position and palette are **artistic choices**, not measured τ or entropy from this repo.

### Gallery captions (when promoting a candidate)

**EN:** *The Boundary of Uncertainty* — artistic interpretation of adaptive reasoning; ordered trajectories → interference; **not** measured entropy or benchmark results.

**ES:** *La frontera de la incertidumbre* — mismo sentido; metáfora conceptual, no visualización de mediciones reales.

Full wording: hub brief `THINK-ANYWHERE-ARTISTIC-PRODUCTION-TEST-v1.md` §8 (private `.procontext`, not required to clone this repo).
