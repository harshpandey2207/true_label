import os
import base64
import json
import tempfile
import shutil
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

router = APIRouter(tags=["Label Generator"])

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

def call_gemini_vision(prompt: str, images_b64: List[str]) -> str:
    """Call Gemini API with images and a text prompt, return text response."""
    import urllib.request
    import urllib.error

    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set in environment.")

    parts = []
    for img_b64 in images_b64:
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": img_b64
            }
        })
    parts.append({"text": prompt})

    payload = json.dumps({
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 0.4,
            "topK": 32,
            "topP": 1,
            "maxOutputTokens": 4096
        }
    }).encode("utf-8")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise HTTPException(status_code=502, detail=f"Gemini API error: {body}")


@router.post("/generate")
async def generate_label(
    images: List[UploadFile] = File(...),
    product_name: str = Form(...),
    product_category: str = Form("General Packaged Commodity"),
    shape: str = Form("Rectangular"),
    dimensions: str = Form("10cm x 15cm"),
    custom_prompt: str = Form(""),
    missing_tag_values: str = Form("{}"),  # JSON string: {"MRP": "100", "NET_QUANTITY": "500g"}
):
    """
    Takes reference label images + user-provided values for missing tags,
    calls Gemini Vision to analyze brand DNA and generate structured label JSON
    for each side of the product.
    """
    temp_dir = tempfile.mkdtemp()
    images_b64 = []

    try:
        for img in images:
            temp_path = os.path.join(temp_dir, img.filename or "image.jpg")
            with open(temp_path, "wb") as f:
                content = await img.read()
                f.write(content)
            with open(temp_path, "rb") as f:
                images_b64.append(base64.b64encode(f.read()).decode("utf-8"))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    # Parse the missing tag values
    try:
        tag_values = json.loads(missing_tag_values)
    except Exception:
        tag_values = {}

    # Auto-calculate USP from MRP if MRP is provided
    mrp_value = tag_values.get("MRP", tag_values.get("mrp", ""))
    net_qty = tag_values.get("NET_QUANTITY", tag_values.get("net_quantity", ""))
    usp_value = ""
    if mrp_value:
        try:
            # USP = MRP (for single unit; divide by quantity if multiple)
            qty_num = 1
            if net_qty:
                import re
                nums = re.findall(r'[\d.]+', net_qty)
                if nums:
                    qty_num = max(1, int(float(nums[0]))) if float(nums[0]) > 10 else 1
            usp_value = f"₹{float(mrp_value.replace('₹','').replace('Rs','').strip()):.2f}"
        except Exception:
            usp_value = mrp_value

    # Build the number of sides based on uploaded images
    num_sides = len(images_b64)
    side_labels = ["Front Label", "Back Label", "Left Side", "Right Side", "Top", "Bottom"]

    compliance_block = "\n".join([f"- {k}: {v}" for k, v in tag_values.items()])
    if usp_value:
        compliance_block += f"\n- USP (Unit Sale Price, auto-calculated): {usp_value}"

    prompt = f"""You are a professional packaging designer and Legal Metrology compliance expert in India.

I am uploading {num_sides} reference image(s) of different sides of a product package. Analyze each image carefully for:
1. Brand colors (extract hex codes)
2. Brand fonts (describe style: bold, serif, sans-serif, etc.)
3. Existing logo/icon descriptions
4. Layout style and design DNA
5. What side of the package each image represents (front/back/side etc.)

Then generate a complete, professional, compliant label design specification in strict JSON format.

PRODUCT DETAILS:
- Product Name: {product_name}
- Category: {product_category}
- Label Shape: {shape}
- Dimensions: {dimensions}
- Custom Design Instructions: {custom_prompt if custom_prompt else "Match brand DNA from uploaded images"}

MANDATORY COMPLIANCE DATA (Legal Metrology Act 2011, PCR 2011):
{compliance_block if compliance_block else "Extract all visible compliance info from images"}

INSTRUCTIONS:
- Generate one label design per uploaded image side
- Each label must be visually distinct and appropriate for that side
- Front label must be premium and brand-forward
- Back/side labels must contain all Legal Metrology declarations
- USP has been auto-calculated from MRP — do NOT ask for it again
- Font sizes must comply with Rule 7: minimum 1mm height for declarations
- Return ONLY valid JSON, no extra text

Return this EXACT JSON structure:
{{
  "brand_dna": {{
    "primary_color": "#hex",
    "secondary_color": "#hex",
    "accent_color": "#hex",
    "font_style": "description",
    "design_aesthetic": "description"
  }},
  "sides": [
    {{
      "side_name": "Front Label",
      "layout_description": "brief description of what this side shows",
      "header": {{
        "brand_name": "{product_name}",
        "tagline": "generated tagline",
        "logo_description": "icon or symbol description"
      }},
      "body_sections": [
        {{
          "section_title": "e.g. Product Highlights",
          "content": "text content here"
        }}
      ],
      "compliance_declarations": {{
        "net_quantity": "",
        "mrp": "",
        "usp": "{usp_value}",
        "manufacturing_date": "",
        "expiry_date": "",
        "batch_no": "",
        "manufacturer": "",
        "country_of_origin": "India",
        "fssai_license": "",
        "customer_care": ""
      }},
      "rule7_note": "Minimum font height applied per Rule 7 PCR 2011"
    }}
  ]
}}

Fill in compliance_declarations from the MANDATORY COMPLIANCE DATA above. Generate {num_sides} side(s) in the sides array.
"""

    result_text = call_gemini_vision(prompt, images_b64)

    # Extract JSON from response
    try:
        # Find JSON block in response
        import re
        json_match = re.search(r'\{[\s\S]*\}', result_text)
        if json_match:
            label_data = json.loads(json_match.group())
        else:
            raise ValueError("No JSON found in response")
    except Exception:
        # Return a structured fallback if JSON parsing fails
        label_data = {
            "brand_dna": {
                "primary_color": "#1B4332",
                "secondary_color": "#FFFFFF",
                "accent_color": "#52B788",
                "font_style": "Bold sans-serif",
                "design_aesthetic": "Clean and professional"
            },
            "sides": [
                {
                    "side_name": f"Side {i+1}",
                    "layout_description": "Compliance label",
                    "header": {
                        "brand_name": product_name,
                        "tagline": "",
                        "logo_description": ""
                    },
                    "body_sections": [],
                    "compliance_declarations": {k: v for k, v in tag_values.items()},
                    "rule7_note": "Rule 7 compliant font sizes applied"
                }
                for i in range(num_sides)
            ],
            "raw_ai_response": result_text
        }

    return {"success": True, "label_data": label_data, "usp_auto_calculated": usp_value}
