import json
import re
from datetime import datetime


def pluralize(number, singular="", plural="s"):
    """countr{{ num_countries|pluralize:("y","ies") }} See
    https://stackoverflow.com/questions/11714614/how-to-pluralize-a-name-in-a-
    template-with-jinja2/22336061#22336061."""
    if number == 1:
        return singular
    else:
        return plural


def get_year(value: str, short: bool = False, format: str = "%Y-%m-%d") -> str:
    """The date format is the default from sql result queries; if short is
    enabled only the last 2 digits of the year are included."""
    date_obj = datetime.strptime(value, format)
    year = date_obj.strftime("%Y")
    return year if not short else f"'{year[-2:]}"


def readable_date(value: str, format: str = "%Y-%m-%d") -> str:
    """The date format is the default from sql result queries; if short is
    enabled only the last 2 digits of the year are included."""
    date_obj = datetime.strptime(value, format)
    readable = date_obj.strftime("%B %-d, %Y")
    return readable


def make_unique_titles(value: str) -> str:
    """The titles may consist of duplicate text since the official title might
    also be the short title, etc."""
    texts = value.split("; ")
    uniques = set(texts)
    return "; ".join(uniques)


def extract_units(raw_units: str) -> list[dict]:
    """Removes the initial `1.` material path which maps to the title of the
    tree; the units start with the content."""
    units = json.loads(raw_units)
    if units:
        return units[0]["units"]
    return []


def valid_mp(candidate_unit_id: str) -> str:
    """Each unit id is material path following the format: 1.1.1.1.

    etc. where all root nodes start with 1. and all branches / leaves
    terminate in the same fashion, e.g. 1.2.13.16.

    The root's identifier `materialized_path` is always 1. and the value of
    the specific branch can be determined through the addition of other
    identifier's to the root. e.g. '1.1.1.2' of 'mv-2022-ra-386-v1'
    will yield all material nodes of the tree from the root to the specified
    `mp` branch.
    """
    mp_pattern = re.compile(r"(\d+\.)+")
    if mp_pattern.fullmatch(candidate_unit_id):
        return candidate_unit_id
    raise Exception(f"Bad {candidate_unit_id=}")


def shorten_item(text: str):
    """Replace the item's long form keyword with its shorthand format, if
    possible."""
    if "Republic Act" in text:
        return re.sub(r"Republic\s+Act\s+No\.", "RA", text)
    if "Presidential Decree" in text:
        return re.sub(r"Presidential\s+Decree\s+No\.", "PD", text)
    if "Batas Pambansa" in text:
        return re.sub(r"Batas\s+Pambansa\s+Blg\.", "BP", text)
    if "Executive Order" in text:
        return re.sub(r"Executive\s+Order\s+No\.", "EO", text)
    if "Commonwealth Act" in text:
        return re.sub(r"Commonwealth\s+Act\s+No\.", "CA", text)
    if "Administrative Matter" in text:
        return re.sub(r"Administrative\s+Matter\s+No\.", "AM", text)
    if "Bar Matter" in text:
        return re.sub(r"Bar\s+Matter\s+No\.", "BM", text)
    if "Administrative Circular" in text:
        return re.sub(r"Administrative\s+Circular\s+No\.", "AC", text)
    if "Paragraph" in text:
        return re.sub(r"Paragraph", "Par.", text)
    if "Article" in text:
        return re.sub(r"Article", "Art.", text)
    if "Section" in text:
        return re.sub(r"Section", "Sec.", text)
    if "Book" in text:
        return re.sub(r"Book", "Bk.", text)
    if "Chapter" in text:
        return re.sub(r"Chapter", "Ch.", text)
    if "Sub-Container" in text:
        return re.sub(r"Sub-Container(\s+\d+)?", "", text)
    if "Container" in text:
        return re.sub(r"Container(\s+\d+)?", "", text)
    return text
