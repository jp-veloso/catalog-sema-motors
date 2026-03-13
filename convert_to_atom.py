import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.request import urlopen, Request

INPUT_URL = "https://semamotors.com.br/fb-catalog.xml"
OUTPUT_FILE = "catalog-atom.xml"

ATOM_NS = "http://www.w3.org/2005/Atom"
G_NS = "http://base.google.com/ns/1.0"


def atom(tag):
    return f"{{{ATOM_NS}}}{tag}"


def g(tag):
    return f"{{{G_NS}}}{tag}"


def get_text(element, path):
    found = element.find(path)
    if found is None or found.text is None:
        return ""
    return found.text.strip()


def convert():
    ET.register_namespace("", ATOM_NS)
    ET.register_namespace("g", G_NS)

    req = Request(INPUT_URL, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/xml,application/xml,*/*",
    })
    with urlopen(req) as response:
        tree = ET.parse(response)
    root = tree.getroot()

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    feed = ET.Element(atom("feed"))

    feed_title = ET.SubElement(feed, atom("title"))
    feed_title.text = get_text(root, "title")

    # <link> no XML de entrada usa atributo href, não texto
    root_link_el = root.find("link")
    root_link_href = root_link_el.get("href", "") if root_link_el is not None else ""

    feed_link = ET.SubElement(feed, atom("link"))
    feed_link.set("href", root_link_href)

    feed_id = ET.SubElement(feed, atom("id"))
    feed_id.text = root_link_href or "vehicle-feed"

    feed_updated = ET.SubElement(feed, atom("updated"))
    feed_updated.text = now

    for listing in root.findall("listing"):
        entry = ET.SubElement(feed, atom("entry"))

        vehicle_id = get_text(listing, "vehicle_id")
        title_text = get_text(listing, "title")
        description = get_text(listing, "description")
        url = get_text(listing, "url")
        price = get_text(listing, "price")
        make = get_text(listing, "make")
        model = get_text(listing, "model")
        year = get_text(listing, "year")
        body_style = get_text(listing, "body_style")
        fuel_type = get_text(listing, "fuel_type")
        state_of_vehicle = get_text(listing, "state_of_vehicle")
        transmission = get_text(listing, "transmission")
        exterior_color = get_text(listing, "exterior_color")

        mileage_el = listing.find("mileage")
        mileage_value = get_text(mileage_el, "value") if mileage_el is not None else ""
        mileage_unit = get_text(mileage_el, "unit") if mileage_el is not None else "KM"

        image_url_el = listing.find("image/url")
        image_url = image_url_el.text.strip() if (image_url_el is not None and image_url_el.text) else ""

        # Campos padrão do Atom
        ET.SubElement(entry, atom("id")).text = vehicle_id
        ET.SubElement(entry, atom("title")).text = title_text
        ET.SubElement(entry, atom("summary")).text = description
        entry_link = ET.SubElement(entry, atom("link"))
        entry_link.set("href", url)
        ET.SubElement(entry, atom("updated")).text = now

        # Campos de veículo no namespace g: (exigido pelo Facebook)
        ET.SubElement(entry, g("id")).text = vehicle_id
        ET.SubElement(entry, g("make")).text = make
        ET.SubElement(entry, g("model")).text = model
        ET.SubElement(entry, g("year")).text = year
        ET.SubElement(entry, g("price")).text = price
        ET.SubElement(entry, g("image_link")).text = image_url
        ET.SubElement(entry, g("link")).text = url
        ET.SubElement(entry, g("description")).text = description
        ET.SubElement(entry, g("body_style")).text = body_style
        ET.SubElement(entry, g("fuel_type")).text = fuel_type
        ET.SubElement(entry, g("state_of_vehicle")).text = state_of_vehicle
        ET.SubElement(entry, g("transmission")).text = transmission
        ET.SubElement(entry, g("exterior_color")).text = exterior_color
        ET.SubElement(entry, g("availability")).text = "in stock"

        if mileage_value:
            mileage_tag = ET.SubElement(entry, g("mileage"))
            ET.SubElement(mileage_tag, g("value")).text = mileage_value
            ET.SubElement(mileage_tag, g("unit")).text = mileage_unit

    ET.indent(feed, space="  ")
    tree_out = ET.ElementTree(feed)
    tree_out.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
    print(f"Arquivo ATOM gerado com sucesso: {OUTPUT_FILE}")


if __name__ == "__main__":
    convert()
