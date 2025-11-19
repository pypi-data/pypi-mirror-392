from bluer_objects.README.items import ImageItems

from bluer_ugv.README.swallow.consts import swallow_assets2, swallow_designs


items = ImageItems(
    {
        f"{swallow_designs}/kicad/swallow/exports/swallow.png": f"{swallow_designs}/kicad/swallow/exports/swallow.pdf",
        f"{swallow_designs}/kicad/swallow/exports/swallow-3d.png": "",
        f"{swallow_designs}/kicad/swallow/exports/swallow-3d-back.png": "",
        f"{swallow_designs}/kicad/swallow/exports/swallow-pcb.png": "",
        f"{swallow_assets2}/20251112_085331.jpg": "",
        f"{swallow_assets2}/20251112_181047.jpg": "",
        f"{swallow_assets2}/20251112_181053.jpg": "",
    }
)

v1_items = ImageItems(
    {
        f"{swallow_assets2}/20250614_102301.jpg": "",
    }
)

v2_items = ImageItems(
    {
        f"{swallow_assets2}/20250703_153834.jpg": "",
        f"{swallow_assets2}/20250925_213013.jpg": "",
        f"{swallow_assets2}/20250925_214017.jpg": "",
        f"{swallow_assets2}/20250928_160425.jpg": "",
        f"{swallow_assets2}/20250928_160449.jpg": "",
        f"{swallow_assets2}/20251002_103712.jpg": "",
        f"{swallow_assets2}/20251002_103720.jpg": "",
    }
)

docs = [
    {
        "path": "../docs/swallow/digital/design/shield/pcb.md",
        "items": items,
    },
    {
        "path": "../docs/swallow/digital/design/shield/v1.md",
        "items": v1_items,
    },
    {
        "path": "../docs/swallow/digital/design/shield/v2.md",
        "items": v2_items,
    },
]
