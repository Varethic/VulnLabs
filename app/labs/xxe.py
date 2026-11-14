import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/labs/xxe", tags=["XML External Entity"])
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

XXE_FLAG = "FLAG{xxe_external_entity_disclosure_7261}"

VULN_CODE = """@router.post("/parse")
def parse_xml_order(xml_data: str = Form(...)):
    parser = ET.XMLParser()
    parser.entity["xxe"] = read_external_entity()
    root = ET.fromstring(xml_data, parser=parser)
    return {"order_status": "received", "data": root.find("item").text}
"""

FIX_CODE = """import defusedxml.ElementTree as ET

@router.post("/parse")
def parse_xml_order(xml_data: str = Form(...)):
    root = ET.fromstring(xml_data, forbid_dtd=True, forbid_entities=True)
    return {"order_status": "received", "data": root.find("item").text}
"""


def parse_vulnerable_xml(raw_xml: str):
    entity_regex = r'<!ENTITY\s+(\w+)\s+SYSTEM\s+["\']([^"\']+)["\']'
    match = re.search(entity_regex, raw_xml, re.IGNORECASE)
    resolved_xml = raw_xml
    if match:
        ent_name, ent_target = match.groups()
        if "flag" in ent_target.lower() or "secret" in ent_target.lower():
            content = XXE_FLAG
        else:
            clean_path = ent_target.replace("file://", "").strip()
            if os.path.exists(clean_path):
                with open(clean_path, "r", errors="ignore") as f:
                    content = f.read()
            else:
                content = XXE_FLAG
        resolved_xml = re.sub(rf'&{ent_name};', content, raw_xml)
    root = ET.fromstring(resolved_xml)
    return root


@router.get("", response_class=HTMLResponse)
def xxe_view(request: Request):
    default_xml = """<?xml version="1.0" encoding="UTF-8"?>
<order>
    <customer>Academic Department</customer>
    <item>Lab Workstation 01</item>
    <quantity>5</quantity>
</order>"""
    return templates.TemplateResponse(
        request=request,
        name="xxe.html",
        context={
            "xml_input": default_xml,
            "parsed_output": None,
            "error": None,
            "vuln_code": VULN_CODE,
            "fix_code": FIX_CODE,
            "active_tab": "xxe",
        },
    )


@router.post("/parse", response_class=HTMLResponse)
def parse_order(request: Request, xml_content: str = Form("")):
    parsed_output = None
    error = None
    try:
        root = parse_vulnerable_xml(xml_content.strip())
        items = {}
        for child in root:
            items[child.tag] = child.text or ""
        parsed_output = items
    except Exception as e:
        error = str(e)

    return templates.TemplateResponse(
        request=request,
        name="xxe.html",
        context={
            "xml_input": xml_content,
            "parsed_output": parsed_output,
            "error": error,
            "vuln_code": VULN_CODE,
            "fix_code": FIX_CODE,
            "active_tab": "xxe",
        },
    )
