
import streamlit as st
import hashlib
import html
import textwrap
from pathlib import Path

from config import (
    PAGE_TITLE,
    MAX_IMAGE_MB,
    PLATFORMS,
    TONES,
    LENGTHS,
    TEXT_MODEL
)

from services.llm_service import get_chat_model
from services.image_service import analyse_image
from services.generation_service import (
    generate_post,
    transform_post
)

from utils.validators import validate_image
from utils.helpers import post_to_markdown


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =====================================================
# LOAD CSS
# =====================================================

css_path = Path("assets/styles.css")

if css_path.exists():
    st.markdown(
        f"<style>{css_path.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True
    )


# =====================================================
# HTML HELPER
# =====================================================

def render_html(markup):
    """Render HTML directly using Streamlit's HTML component."""
    st.html(textwrap.dedent(markup).strip())


# =====================================================
# SESSION STATE
# =====================================================

defaults = {
    "image_brief": None,
    "results": {},
    "approved_title": "",
    "edited_description": "",
    "audience": "",
    "tone": "Friendly",
    "length": "Medium",
    "selected_platforms": ["Instagram", "LinkedIn"],
    "generation_inputs": {},
    "uploaded_image_hash": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def reset_content():

    st.session_state.image_brief = None
    st.session_state.results = {}
    st.session_state.approved_title = ""
    st.session_state.edited_description = ""
    st.session_state.generation_inputs = {}


def get_model():

    return get_chat_model(
        TEXT_MODEL,
        temperature=0.7
    )


# =====================================================
# GENERATED POST DISPLAY
# =====================================================

def render_post(platform, post):

    safe_platform = html.escape(str(platform))

    safe_title = html.escape(
        str(post.post_title or "")
    )

    safe_hook = html.escape(
        str(post.opening_hook or "")
    )

    safe_caption = html.escape(
        str(post.main_caption or "")
    )

    safe_hashtags = html.escape(
        " ".join(post.hashtags or [])
    )

    render_html(f"""
        <div class="post-platform">
            {safe_platform.upper()} POST
        </div>
    """)

    render_html(f"""
        <div class="post-title">
            {safe_title}
        </div>
    """)

    render_html(f"""
        <div class="post-hook">
            {safe_hook}
        </div>
    """)

    st.markdown("#### Your caption")

    render_html(f"""
        <div class="caption-box">
            {safe_caption}
        </div>
    """)

    st.markdown("#### Hashtags")

    render_html(f"""
        <div class="hashtag-box">
            {safe_hashtags}
        </div>
    """)

    st.markdown("#### Call to action")

    st.write(post.call_to_action or "")

    # Additional content

    with st.expander("Alternative hooks, short caption and strategy"):

        st.markdown("**Alternative hooks**")

        for hook in post.alternative_hooks or []:
            st.write(f"• {hook}")

        st.markdown("**Short caption**")

        st.write(post.short_version or "")

        st.markdown("**Content strategy**")

        st.write(post.content_strategy or "")

    # Downloads

    full_caption = (
        f"{post.main_caption or ''}\n\n"
        f"{' '.join(post.hashtags or [])}"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            "↓ Download post",
            data=post_to_markdown(platform, post),
            file_name=f"{platform.lower().replace(' ', '-')}-post.md",
            mime="text/markdown",
            key=f"download_{platform}",
            use_container_width=True
        )

    with col2:

        st.download_button(
            "↓ Download caption",
            data=full_caption,
            file_name=f"{platform.lower().replace(' ', '-')}-caption.txt",
            mime="text/plain",
            key=f"caption_{platform}",
            use_container_width=True
        )

    # Customize post

    with st.expander("Customize this post"):

        custom_instruction = st.text_input(
            "What would you like to change?",
            placeholder="e.g. Make it more emotional and engaging",
            key=f"instruction_{platform}"
        )

        if st.button(
            "Apply changes",
            key=f"apply_{platform}",
            use_container_width=True,
            disabled=not custom_instruction.strip()
        ):

            try:

                with st.spinner("Improving your post..."):

                    updated = transform_post(
                        get_model(),
                        post,
                        custom_instruction,
                        platform
                    )

                    st.session_state.results[platform] = updated

                st.success("Your post has been updated.")
                st.rerun()

            except Exception as error:

                st.error(f"Could not update post: {error}")

    # Regenerate and shorten

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "↻ Regenerate",
            key=f"regenerate_{platform}",
            use_container_width=True
        ):

            try:

                with st.spinner("Creating another version..."):

                    updated = generate_post(
                        get_model(),
                        platform,
                        st.session_state.generation_inputs
                    )

                    st.session_state.results[platform] = updated

                st.rerun()

            except Exception as error:

                st.error(f"Regeneration failed: {error}")

    with col2:

        if st.button(
            "Shorten caption",
            key=f"shorten_{platform}",
            use_container_width=True
        ):

            try:

                with st.spinner("Shortening your caption..."):

                    updated = transform_post(
                        get_model(),
                        post,
                        (
                            "Make the caption shorter, clearer "
                            "and more concise. Preserve the key message."
                        ),
                        platform
                    )

                    st.session_state.results[platform] = updated

                st.rerun()

            except Exception as error:

                st.error(f"Could not shorten caption: {error}")


# =====================================================
# MAIN HEADER
# =====================================================

render_html("""
<div style="
    padding: 20px 0 30px 0;
    border-bottom: 1px solid rgba(255,255,255,0.09);
    margin-bottom: 30px;
">
    <div style="
        color: #A78BFA;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 2px;
        margin-bottom: 12px;
    ">
        ✦ SOCIAL STUDIO AI
    </div>

    <h1 style="
        font-size: 38px;
        font-weight: 800;
        letter-spacing: -1.5px;
        margin: 0;
        color: #F5F4FC;
    ">
        Create content that connects.
    </h1>

    <p style="
        color: #A0A6BA;
        font-size: 16px;
        margin-top: 10px;
        margin-bottom: 0;
    ">
        Turn your images into engaging, platform-ready
        social media content with AI.
    </p>
</div>
""")


# =====================================================
# IMAGE UPLOAD
# =====================================================

st.markdown(
    '<div class="section-heading">01 / Upload your image</div>',
    unsafe_allow_html=True
)

st.caption(
    "Upload a photograph to automatically generate your social media content."
)

uploaded_file = st.file_uploader(
    "Choose an image",
    type=["jpg", "jpeg", "png", "webp"],
    help=f"Maximum file size: {MAX_IMAGE_MB} MB",
    label_visibility="collapsed"
)


if uploaded_file:

    current_hash = hashlib.md5(
        uploaded_file.getvalue()
    ).hexdigest()

    if current_hash != st.session_state.uploaded_image_hash:

        reset_content()

        st.session_state.uploaded_image_hash = current_hash

    valid, message = validate_image(
        uploaded_file,
        MAX_IMAGE_MB
    )

    if not valid:

        st.error(message)

    else:

        image_col, info_col = st.columns(
            [1.1, 1],
            gap="large"
        )

        with image_col:

            st.image(
                uploaded_file,
                use_container_width=True
            )

        with info_col:

            st.markdown("### Your creative starting point")

            st.write(
                """
                Your image contains the raw material for a great
                social media post.

                Let AI understand its context and create a
                publish-ready content brief.
                """
            )

            render_html("""
                <div>
                    <span class="feature-chip">
                        ✦ Image understanding
                    </span>

                    <span class="feature-chip">
                        ✦ AI-written captions
                    </span>

                    <span class="feature-chip">
                        ✦ Relevant keywords
                    </span>
                </div>
            """)

            if st.button(
                "✦ Analyse image",
                type="primary",
                use_container_width=True
            ):

                try:

                    with st.spinner(
                        "Understanding your image and creating your content brief..."
                    ):

                        uploaded_file.seek(0)

                        brief = analyse_image(uploaded_file)

                        st.session_state.image_brief = brief

                        st.session_state.approved_title = (
                            brief.suggested_title
                        )

                        st.session_state.edited_description = (
                            brief.suggested_description
                        )

                        st.session_state.results = {}

                    st.success("Your content brief is ready!")
                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Image analysis failed: {error}"
                    )


# =====================================================
# AI-GENERATED CONTENT BRIEF
# =====================================================

if st.session_state.image_brief:

    brief = st.session_state.image_brief

    st.markdown("---")

    st.markdown(
        '<div class="section-heading">02 / Your creative brief</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Review and edit the content suggested by AI."
    )

    with st.container(border=True):

        st.markdown("#### Suggested title")

        st.text_input(
            "Post title",
            key="approved_title",
            label_visibility="collapsed"
        )

        st.markdown("#### Social media description")

        st.text_area(
            "Edit description",
            key="edited_description",
            height=170,
            label_visibility="collapsed"
        )

        st.markdown("#### Suggested keywords")

        keyword_html = "".join(
            (
                '<span class="keyword-chip">'
                f'{html.escape(str(keyword))}'
                '</span>'
            )
            for keyword in brief.keywords
        )

        render_html(
            f'<div class="keyword-wrap">{keyword_html}</div>'
        )

        with st.expander("View image analysis"):

            st.write(brief.visual_analysis)


# =====================================================
# CONTENT CUSTOMIZATION
# =====================================================

if st.session_state.image_brief:

    st.markdown("---")

    st.markdown(
        '<div class="section-heading">03 / Customize your content</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Choose your target audience and preferred writing style."
    )

    with st.container(border=True):

        col1, col2 = st.columns(2, gap="large")

        with col1:

            st.markdown("**Target audience**")

            st.text_input(
                "Who are you creating content for?",
                key="audience",
                placeholder="e.g. Young professionals, car lovers, students",
                label_visibility="collapsed"
            )

        with col2:

            st.markdown("**Tone of voice**")

            st.selectbox(
                "Choose your tone",
                TONES,
                key="tone",
                label_visibility="collapsed"
            )

        st.markdown("**Caption length**")

        st.select_slider(
            "Choose caption length",
            options=LENGTHS,
            key="length",
            label_visibility="collapsed"
        )

        st.markdown("**Select social media platforms**")

        st.multiselect(
            "Choose where you want to publish",
            options=PLATFORMS,
            key="selected_platforms",
            label_visibility="collapsed",
            placeholder="Select one or more platforms"
        )

        selected = st.session_state.selected_platforms

        if selected:

            st.caption(
                "Selected: " + " · ".join(selected)
            )

        can_generate = (
            bool(selected)
            and bool(st.session_state.approved_title.strip())
            and bool(st.session_state.edited_description.strip())
        )

        if st.button(
            "✦ Generate my social media posts",
            type="primary",
            use_container_width=True,
            disabled=not can_generate
        ):

            inputs = {

                "title": st.session_state.approved_title.strip(),

                "description": (
                    st.session_state.edited_description.strip()
                ),

                "keywords": brief.keywords,

                "visual_analysis": brief.visual_analysis,

                "audience": (
                    st.session_state.audience.strip()
                    or "General audience"
                ),

                "tone": st.session_state.tone,

                "length": st.session_state.length,

                "language": "English",

                "objective": "Engagement",

                "cta": (
                    "Create a natural and relevant call to action"
                )
            }

            st.session_state.generation_inputs = inputs

            try:

                generated = {}

                progress = st.progress(0)

                status = st.empty()

                model = get_model()

                total = len(selected)

                for index, platform in enumerate(selected):

                    status.info(
                        f"Creating your {platform} content..."
                    )

                    generated[platform] = generate_post(
                        model,
                        platform,
                        inputs
                    )

                    progress.progress(
                        (index + 1) / total
                    )

                st.session_state.results = generated

                status.success("Your content is ready!")

                st.rerun()

            except Exception as error:

                st.error(
                    f"Post generation failed: {error}"
                )


# =====================================================
# GENERATED POSTS
# =====================================================

if st.session_state.results:

    st.markdown("---")

    st.markdown(
        '<div class="section-heading">04 / Your generated content</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Review, edit and download your AI-generated posts."
    )

    platforms = list(st.session_state.results.keys())

    tabs = st.tabs(platforms)

    for tab, platform in zip(tabs, platforms):

        with tab:

            with st.container(border=True):

                render_post(
                    platform,
                    st.session_state.results[platform]
                )

    st.markdown("")

    all_posts = "\n\n---\n\n".join(
        post_to_markdown(platform, post)
        for platform, post in st.session_state.results.items()
    )

    st.download_button(
        "↓ Download all generated posts",
        data=all_posts,
        file_name="social-studio-all-posts.md",
        mime="text/markdown",
        use_container_width=True
    )


# =====================================================
# FOOTER
# =====================================================

render_html("""
<div class="main-footer">

    <div class="footer-brand">
        ✦ SOCIAL STUDIO AI
    </div>

    <p>
        Create better content. Tell better stories.
    </p>

    <span>
        Powered by AI · Built for creators
    </span>

</div>
""")
