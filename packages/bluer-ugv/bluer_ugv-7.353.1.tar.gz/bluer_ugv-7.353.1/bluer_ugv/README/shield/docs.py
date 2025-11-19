from bluer_ugv.README.shield import box, pcb, schematics, testing


docs = (
    [
        {
            "path": "../docs/swallow/digital/design/shield",
        },
        {
            "path": "../docs/swallow/digital/design/shield/connectors-v1.md",
        },
    ]
    + box.docs
    + pcb.docs
    + schematics.docs
    + testing.docs
)
