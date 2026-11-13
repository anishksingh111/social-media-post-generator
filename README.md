# Social Studio AI

An image-first, non-technical social media content generator built with Streamlit, LangChain and Groq.

## What the user does
1. Uploads an image.
2. Clicks **Analyse image**.
3. Reviews the AI-suggested title, image description and keywords. The title is editable; description and keywords are generated automatically from the image.
4. Enters a target audience and chooses a tone and caption length.
5. Selects social platforms and clicks **Create my posts**.

The app creates platform-specific post titles, hooks, captions, hashtags, CTAs, alternative hooks, short versions and content strategy notes.

## Owner setup

Python 3.10+ and a Groq API key are required.

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and set:

```env
GROQ_API_KEY=your_actual_groq_api_key
MAX_IMAGE_MB=8
```

The API key is configured by the app owner, not entered by end users. Never commit `.env` to GitHub. The default vision model is configured in `config.py`; model availability can change, so update `VISION_MODEL` there if needed.

Run locally:

```powershell
streamlit run app.py
```

## Deployment

Push the project to GitHub (excluding `.env`) and deploy `app.py` on Streamlit Community Cloud. Add this to the app's Secrets settings:

```toml
GROQ_API_KEY = "your_actual_groq_api_key"
```

The app reads the key from the environment/Streamlit runtime. Do not expose the key in the UI or source control.

## Architecture

- `app.py`: user-friendly image-first Streamlit interface.
- `services/image_service.py`: vision analysis and structured image brief.
- `services/generation_service.py`: platform-specific generation and rewrite operations.
- `services/llm_service.py`: central Groq text model initialization.
- `prompts/platform_prompts.py`: platform-specific writing guidance.
- `utils/validators.py`: upload validation.
- `assets/styles.css`: dark visual theme.
- `.streamlit/config.toml`: Streamlit dark theme.

Image-derived title, description and keywords are suggestions, not verified product facts. Review generated content before publishing. The app generates drafts; it does not publish directly to social platforms.
