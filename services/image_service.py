
import base64
import json
import re
from io import BytesIO

from PIL import Image
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from config import VISION_MODEL
from services.llm_service import get_api_key


def _extract_json(response):
    """Extract JSON from the model response."""

    content = response.content

    if isinstance(content, list):
        content = "\n".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict)
        )

    content = str(content).strip()

    # Remove Markdown code fences if the model includes them.
    content = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        content,
        flags=re.IGNORECASE
    ).strip()

    # Extract the JSON object if additional text is present.
    start = content.find("{")
    end = content.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "The AI did not return a valid JSON object."
        )

    return json.loads(content[start:end + 1])


def analyse_image(uploaded_file):
    """Analyse an uploaded image and generate a social media brief."""

    # Open and optimize the image.
    image = Image.open(uploaded_file).convert("RGB")

    image.thumbnail((1600, 1600))

    buffer = BytesIO()

    image.save(
        buffer,
        format="JPEG",
        quality=88
    )

    image_bytes = buffer.getvalue()

    encoded_image = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    image_url = (
        f"data:image/jpeg;base64,{encoded_image}"
    )

    # Initialize the vision model without structured tool calling.
    model = ChatGroq(
        model=VISION_MODEL,
        temperature=0.3,
        api_key=get_api_key()
    )

    system_prompt = """
You are an expert social media content strategist.

Your task is to analyse an uploaded image and prepare
a useful social media content brief.

IMPORTANT RULES:

1. Do not simply narrate what is visible in the image.
2. Write a natural, engaging, publish-ready social media description.
3. Understand the likely occasion, emotion, subject and context.
4. Do not invent names, events, achievements or personal facts.
5. If the context is uncertain, use neutral wording.
6. Suggest a catchy and relevant title.
7. Provide 6 to 10 relevant keywords.
8. Keep visual_analysis factual and separate from the publish-ready copy.

Return ONLY a valid JSON object with exactly these four keys:

{
    "suggested_title": "A catchy title",
    "suggested_description": "A publish-ready social media description",
    "keywords": ["keyword 1", "keyword 2"],
    "visual_analysis": "A factual explanation of what is visible"
}

Do not use Markdown code fences.
Do not add any text before or after the JSON.
"""

    user_message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": (
                    "Analyse this image and generate the "
                    "social media content brief using the "
                    "required JSON structure."
                )
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
            }
        ]
    )

    response = model.invoke([
        SystemMessage(content=system_prompt),
        user_message
    ])

    data = _extract_json(response)

    # Validate all required fields.
    required_fields = [
        "suggested_title",
        "suggested_description",
        "keywords",
        "visual_analysis"
    ]

    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(
                f"AI response is missing the required field: {field}"
            )

    if not isinstance(data["keywords"], list):
        raise ValueError(
            "AI returned keywords in an invalid format."
        )

    return ImageBrief(
        suggested_title=data["suggested_title"],
        suggested_description=data["suggested_description"],
        keywords=data["keywords"],
        visual_analysis=data["visual_analysis"]
    )


# Keep the same output structure used by the rest of the app.
from pydantic import BaseModel, Field


class ImageBrief(BaseModel):

    suggested_title: str = Field(
        description="A catchy social media post title"
    )

    suggested_description: str = Field(
        description="A publish-ready social media description"
    )

    keywords: list[str] = Field(
        description="Relevant social media keywords"
    )

    visual_analysis: str = Field(
        description="A factual analysis of the uploaded image"
    )
