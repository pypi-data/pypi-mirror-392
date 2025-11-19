from bluer_objects.README.items import ImageItems

from bluer_ugv.README.swallow.consts import swallow_assets2

items = ImageItems(
    {
        f"{swallow_assets2}/20251113_205142.jpg": "",
        f"{swallow_assets2}/20251113_210730.jpg": "",
        f"{swallow_assets2}/20251113_210706.jpg": "",
    },
)

docs = [
    {
        "path": "../docs/swallow/digital/design/shield/testing.md",
        "items": items,
    },
]
