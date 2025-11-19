from bluer_objects.README.items import ImageItems

from bluer_sbc.README.design import design_doc
from bluer_sbc.README.designs.swallow.consts import swallow_assets2
from bluer_sbc.README.designs.swallow import image_template, latest_version
from bluer_sbc.README.designs.swallow.parts import parts

docs = [
    design_doc(
        "swallow/v1",
        ImageItems(
            {
                f"{swallow_assets2}/20250609_164433.jpg": "",
                f"{swallow_assets2}/20250614_114954.jpg": "",
                f"{swallow_assets2}/20250615_192339.jpg": "",
            }
        ),
        parts,
    )
] + [
    design_doc(
        f"swallow/v{version}",
        ImageItems(
            {
                image_template(version).format(
                    f"{index+1:02}.jpg",
                ): ""
                for index in range(6)
            }
        ),
        parts,
    )
    for version in range(2, latest_version)
]
