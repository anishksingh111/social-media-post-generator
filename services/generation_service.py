
from typing import List

from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from prompts.platform_prompts import PLATFORM_GUIDANCE


# ==========================================
# 1. SOCIAL MEDIA POST OUTPUT STRUCTURE
# ==========================================

class SocialPost(BaseModel):

    post_title: str = Field(
        default="Social Media Post",
        description="An engaging title for the post"
    )

    opening_hook: str = Field(
        default="",
        description="An attention-grabbing opening line"
    )

    main_caption: str = Field(
        default="",
        description="The complete publish-ready social media caption"
    )

    hashtags: List[str] = Field(
        default_factory=list,
        description="Relevant hashtags for the selected platform"
    )

    call_to_action: str = Field(
        default="",
        description="A natural and relevant call to action"
    )

    alternative_hooks: List[str] = Field(
        default_factory=list,
        description="Three alternative opening hooks"
    )

    short_version: str = Field(
        default="",
        description="A shorter version of the main caption"
    )

    content_strategy: str = Field(
        default="Focus on engaging the target audience with relevant content.",
        description="A brief explanation of the content strategy"
    )


# ==========================================
# 2. STRUCTURED OUTPUT HELPER
# ==========================================

def _generate_structured_response(
    model,
    system_prompt: str,
    user_prompt: str
) -> SocialPost:

    parser = PydanticOutputParser(
        pydantic_object=SocialPost
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "{system_prompt}\n\n"
                "Follow this output format exactly:\n"
                "{format_instructions}"
            ),
            (
                "human",
                "{user_prompt}"
            )
        ]
    )

    chain = prompt | model | parser

    result = chain.invoke(
        {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "format_instructions": parser.get_format_instructions()
        }
    )

    return result


# ==========================================
# 3. GENERATE PLATFORM-SPECIFIC POST
# ==========================================

def generate_post(
    model,
    platform: str,
    inputs: dict
) -> SocialPost:

    platform_instructions = PLATFORM_GUIDANCE.get(
        platform,
        "Create engaging, natural and platform-appropriate content."
    )

    system_prompt = f"""
You are an expert social media strategist,
copywriter and digital marketing specialist.

Your task is to create a high-quality,
publish-ready social media post.

TARGET PLATFORM:
{platform}

PLATFORM-SPECIFIC GUIDANCE:
{platform_instructions}

CONTENT REQUIREMENTS:

1. Create content specifically for the selected platform.
2. Do not simply describe the uploaded photograph.
3. Write natural, engaging and human-sounding copy.
4. Use the suggested title as inspiration.
5. Respect the selected target audience.
6. Follow the requested tone of voice.
7. Follow the requested caption length.
8. Use keywords naturally without keyword stuffing.
9. Do not invent facts, statistics, achievements,
   names or product features.
10. Avoid repetitive or generic marketing language.
11. Make the opening hook attention-grabbing.
12. Include a suitable call to action.
13. Use relevant hashtags appropriate to the platform.
14. Make the final caption ready to publish.

PLATFORM-SPECIFIC EXPECTATIONS:

- Instagram: Engaging, visually relevant and shareable.
- LinkedIn: Professional, insightful and credible.
- Facebook: Conversational and community-oriented.
- X (Twitter): Concise, impactful and direct.
- YouTube Community: Conversational and discussion-driven.
- Pinterest: Search-friendly, descriptive and inspirational.

IMPORTANT:

The main_caption must be a complete caption that the
user can publish directly.

Do not include explanations, internal notes or labels
inside the main_caption.

The content_strategy field should briefly explain
the creative approach used.
"""

    user_prompt = f"""
Create a social media post using the following information.

SUGGESTED TITLE:
{inputs.get("title", "")}

AI-GENERATED DESCRIPTION:
{inputs.get("description", "")}

RELEVANT KEYWORDS:
{", ".join(inputs.get("keywords", []))}

IMAGE CONTEXT:
{inputs.get("visual_analysis", "")}

TARGET AUDIENCE:
{inputs.get("audience", "General audience")}

TONE OF VOICE:
{inputs.get("tone", "Friendly")}

CAPTION LENGTH:
{inputs.get("length", "Medium")}

LANGUAGE:
{inputs.get("language", "English")}

CONTENT OBJECTIVE:
{inputs.get("objective", "Engagement")}

CALL TO ACTION PREFERENCE:
{inputs.get("cta", "Create a natural and relevant call to action")}

Generate all the required fields in the output structure.
"""

    return _generate_structured_response(
        model,
        system_prompt,
        user_prompt
    )


# ==========================================
# 4. IMPROVE / SHORTEN EXISTING POST
# ==========================================

def transform_post(
    model,
    post: SocialPost,
    instruction: str,
    platform: str
) -> SocialPost:

    platform_instructions = PLATFORM_GUIDANCE.get(
        platform,
        "Maintain natural and platform-appropriate content."
    )

    system_prompt = f"""
You are an expert social media editor and copywriter.

Your task is to revise an existing social media post.

TARGET PLATFORM:
{platform}

PLATFORM GUIDANCE:
{platform_instructions}

RULES:

1. Follow the user's editing instruction carefully.
2. Preserve the original meaning and factual information.
3. Maintain the selected platform's writing style.
4. Improve clarity, readability and engagement.
5. Do not invent information.
6. Keep the result natural and publish-ready.
7. Return all fields in the required output structure.
"""

    # Support both Pydantic v2 and v1.
    if hasattr(post, "model_dump_json"):
        existing_post = post.model_dump_json(indent=2)
    else:
        existing_post = post.json(indent=2)

    user_prompt = f"""
EXISTING SOCIAL MEDIA POST:

{existing_post}

USER'S EDITING INSTRUCTION:

{instruction}

Revise the post while preserving its important information.

Return the complete revised post, including:
- Post title
- Opening hook
- Main caption
- Hashtags
- Call to action
- Alternative hooks
- Short version
- Content strategy
"""

    return _generate_structured_response(
        model,
        system_prompt,
        user_prompt
    )
