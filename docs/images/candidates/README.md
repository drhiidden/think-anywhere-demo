# Hero candidates (comparative evaluation)

Comparative hero experiments. Files here use **HHP project-to-art v2.1** (or CurveCodex as its generative engine)—**not** wired into the README hero until human approval. The banner currently in the README predates this folder; see the caption under the hero image.

| File | Description |
|------|-------------|
| `think-anywhere-hero-v2-frontera-candidate-a.png` | Direction A — fallback raster script (legacy) |
| `think-anywhere-hero-v2-frontera-curvecodex.png` | Direction A — **CurveCodex** v2 (seed 42, defaults) |
| `think-anywhere-hero-v3-frontera-curvecodex.png` | Direction A — **CurveCodex v3** (seed 20261012, 190 streamlines, transition 0.32–0.55) — **revisor** |
| `*-external.png` | Optional: external generator using production prompt in hub brief |

Canonical brief (hub): HALETHEIA `.procontext/.../think-anywhere/THINK-ANYWHERE-ARTISTIC-PRODUCTION-TEST-v1.md`

Regenerate (preferred — from CurveCodex repo):

```bash
cd /path/to/CurveCodex && pip install -e .
python examples/03_regime_transition_banner.py -o /path/to/candidates/think-anywhere-hero-v3-frontera-curvecodex.png \
  --seed 20261012 --streamlines 190 --dpi 110 --transition-start 0.32 --transition-end 0.55 --linewidth 0.52
```

Legacy fallback: `python docs/images/candidates/generate_frontera_candidate.py`

Do **not** replace `docs/images/think-anywhere-hero.png` without explicit review.

**Commit policy:** no `git commit` en think-anywhere-demo por candidatos hasta **hero v3** regenerada con CurveCodex y aprobada para comparativa/sustitución.
