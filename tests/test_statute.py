import pytest

from corpus_x import Statute


@pytest.fixture
def ra_11716_obj(shared_datadir):
    if obj := Statute.from_page(
        shared_datadir / "statutes" / "ra" / "11716" / "details.yaml"
    ):
        return obj.dict(exclude_none=True)


def test_ra_11716_obj_keys(ra_11716_obj):
    assert set(ra_11716_obj.keys()) == {
        "id",
        "emails",
        "meta",
        "titles",
        "tree",
        "unit_fts",
        "material_paths",
        "statutes_found",
    }


def test_ra_11716_unit_fts(ra_11716_obj):
    assert ra_11716_obj["unit_fts"] == [
        {
            "material_path": "1.",
            "statute_id": "ra-11716-april-29-2022",
            "unit_text": (  # noqa: E501
                "ra 11716, Republic Act No. 11716, An Act Increasing The Bed"
                " Capacity Of The Northern Mindanao Medical Center In Cagayan"
                " De Oro City, Amending For The Purpose Republic Act No. 7938,"
                " As Amended By Republic Act No. 10677, And Appropriating"
                " Funds Therefor"
            ),
        },
        {
            "material_path": "1.1.",
            "statute_id": "ra-11716-april-29-2022",
            "unit_text": (  # noqa: E501
                "Section 2 of Republic Act No. 7938, as amended by Republic"
                " Act No. 10677, is hereby amended to read as follows:"
            ),
        },
        {
            "material_path": "1.1.1.1.",
            "statute_id": "ra-11716-april-29-2022",
            "unit_text": (  # noqa: E501
                "The health care services and facilities of the Northern"
                " Mindanao Medical Center (NMMC) shall be upgraded to conform"
                " with and be commensurate to the bed capacity increase from"
                " six hundred (600) to one thousand two hundred (1,200) beds."
            ),
        },
        {
            "material_path": "1.1.1.2.",
            "statute_id": "ra-11716-april-29-2022",
            "unit_text": (  # noqa: E501
                "Any future increase in bed capacity shall be consistent with"
                " the hospital development plan which shall be prepared by the"
                " Department of Health (DOH)."
            ),
        },
        {
            "material_path": "1.2.",
            "statute_id": "ra-11716-april-29-2022",
            "unit_text": (  # noqa: E501
                "Section 3 of the same Act is hereby amended to read as"
                " follows:"
            ),
        },
        {
            "material_path": "1.2.1.",
            "statute_id": "ra-11716-april-29-2022",
            "unit_text": (  # noqa: E501
                "The number of medical personnel, the budget for personnel"
                " services and maintenance\nand other operating expenses of"
                " the NMMC shall correspondingly be increased. The\nSecretary"
                " of the DOH shall, in coordination with the Secretary of the"
                " Department\nof Budget and Management and the Chairperson of"
                " the Civil Service Commission,\nand after consultation with"
                " the Chief of NMMC, determine the additional"
                " plantilla\npositions to be created pursuant to this Act."
            ),
        },
        {
            "material_path": "1.3.",
            "statute_id": "ra-11716-april-29-2022",
            "unit_text": (  # noqa: E501
                "Section 4 of the same Act is hereby amended to read as"
                " follows:"
            ),
        },
        {
            "material_path": "1.3.1.",
            "statute_id": "ra-11716-april-29-2022",
            "unit_text": (  # noqa: E501
                "The increase in bed capacity of the NMMC fro six hundred"
                " (600) to one thousand\ntwo hundred (1,200) beds shall be"
                " implemented immediately upon approval of this\nAct."
            ),
        },
        {
            "material_path": "1.4.",
            "statute_id": "ra-11716-april-29-2022",
            "unit_text": (  # noqa: E501
                "This Act shall take effect fifteen (15) days after its"
                " publication in the *Official Gazette* or in a newspaper of"
                " general circulation."
            ),
        },
    ]


def test_ra_11716_titles(ra_11716_obj):
    assert ra_11716_obj["titles"] == [
        {
            "statute_id": "ra-11716-april-29-2022",
            "category": "serial",
            "text": "Republic Act No. 11716",
        },
        {
            "statute_id": "ra-11716-april-29-2022",
            "category": "official",
            "text": (  # noqa: E501
                "An Act Increasing The Bed Capacity Of The Northern Mindanao"
                " Medical Center In Cagayan De Oro City, Amending For The"
                " Purpose Republic Act No. 7938, As Amended By Republic Act"
                " No. 10677, And Appropriating Funds Therefor"
            ),
        },
    ]


def test_ra_11716_statutes_found(ra_11716_obj):
    assert ra_11716_obj["statutes_found"] == [
        {
            "statute_category": "ra",
            "statute_serial_id": "7938",
            "material_path": "1.1.",
            "statute_id": "ra-11716-april-29-2022",
        },
        {
            "statute_category": "ra",
            "statute_serial_id": "10677",
            "material_path": "1.1.",
            "statute_id": "ra-11716-april-29-2022",
        },
    ]


def test_ra_11716_material_paths(ra_11716_obj):
    assert ra_11716_obj["material_paths"] == [
        {
            "item": "Republic Act No. 11716",
            "material_path": "1.",
            "statute_id": "ra-11716-april-29-2022",
        },
        {
            "item": "Section 1",
            "content": (  # noqa: E501
                "Section 2 of Republic Act No. 7938, as amended by Republic"
                " Act No. 10677, is hereby amended to read as follows:"
            ),
            "material_path": "1.1.",
            "statute_id": "ra-11716-april-29-2022",
        },
        {
            "item": "Section 2",
            "material_path": "1.1.1.",
            "statute_id": "ra-11716-april-29-2022",
        },
        {
            "item": "Paragraph 1",
            "content": (  # noqa: E501
                "The health care services and facilities of the Northern"
                " Mindanao Medical Center (NMMC) shall be upgraded to conform"
                " with and be commensurate to the bed capacity increase from"
                " six hundred (600) to one thousand two hundred (1,200) beds."
            ),
            "material_path": "1.1.1.1.",
            "statute_id": "ra-11716-april-29-2022",
        },
        {
            "item": "Paragraph 2",
            "content": (  # noqa: E501
                "Any future increase in bed capacity shall be consistent with"
                " the hospital development plan which shall be prepared by the"
                " Department of Health (DOH)."
            ),
            "material_path": "1.1.1.2.",
            "statute_id": "ra-11716-april-29-2022",
        },
        {
            "item": "Section 2",
            "content": (  # noqa: E501
                "Section 3 of the same Act is hereby amended to read as"
                " follows:"
            ),
            "material_path": "1.2.",
            "statute_id": "ra-11716-april-29-2022",
        },
        {
            "item": "Section 3",
            "content": (  # noqa: E501
                "The number of medical personnel, the budget for personnel"
                " services and maintenance\nand other operating expenses of"
                " the NMMC shall correspondingly be increased. The\nSecretary"
                " of the DOH shall, in coordination with the Secretary of the"
                " Department\nof Budget and Management and the Chairperson of"
                " the Civil Service Commission,\nand after consultation with"
                " the Chief of NMMC, determine the additional"
                " plantilla\npositions to be created pursuant to this Act."
            ),
            "material_path": "1.2.1.",
            "statute_id": "ra-11716-april-29-2022",
        },
        {
            "item": "Section 3",
            "content": (  # noqa: E501
                "Section 4 of the same Act is hereby amended to read as"
                " follows:"
            ),
            "material_path": "1.3.",
            "statute_id": "ra-11716-april-29-2022",
        },
        {
            "item": "Section 4",
            "content": (  # noqa: E501
                "The increase in bed capacity of the NMMC fro six hundred"
                " (600) to one thousand\ntwo hundred (1,200) beds shall be"
                " implemented immediately upon approval of this\nAct."
            ),
            "material_path": "1.3.1.",
            "statute_id": "ra-11716-april-29-2022",
        },
        {
            "item": "Section 4",
            "content": (  # noqa: E501
                "This Act shall take effect fifteen (15) days after its"
                " publication in the *Official Gazette* or in a newspaper of"
                " general circulation."
            ),
            "material_path": "1.4.",
            "statute_id": "ra-11716-april-29-2022",
        },
    ]
