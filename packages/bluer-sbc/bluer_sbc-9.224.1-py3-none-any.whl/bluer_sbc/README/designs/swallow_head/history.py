from bluer_objects.README.items import ImageItems

from bluer_sbc.README.design import design_doc
from bluer_sbc.README.designs.swallow_head import image_template, latest_version
from bluer_sbc.README.designs.swallow_head.parts import parts

docs = [
    design_doc(
        f"swallow-head/v{version}",
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
    for version in range(1, latest_version)
]
