from bluer_objects.README.items import ImageItems

from bluer_sbc.README.design import design_doc
from bluer_sbc.README.designs.swallow import image_template
from bluer_sbc.README.designs.swallow.parts import parts
from bluer_sbc.README.designs.swallow import history
from bluer_sbc.README.designs.swallow import latest_version

items = ImageItems(
    {
        image_template(latest_version).format(f"{index+1:02}.jpg"): ""
        for index in range(6)
    }
)

docs = [
    design_doc(
        "swallow",
        items,
        parts,
        own_folder=True,
    )
] + history.docs
