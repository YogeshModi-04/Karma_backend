from google.adk.agents import LlmAgent

from agents.base import get_ollama_model

# Extracted as a module-level constant so service.py can use it directly
# in LiteLLM calls without going through the ADK runner.
# IMAGE_AGENT_INSTRUCTION = (
#     "Describe this image completely and accurately. Cover:\n\n"
#     "1. WHAT IS SHOWN — Identify every visible subject, object, person, "
#     "animal, or scene. State what is happening or being depicted.\n\n"
#     "2. VISUAL DETAILS — Colors, shapes, textures, lighting, composition, "
#     "and any text or symbols visible.\n\n"
#     "3. SETTING & CONTEXT — Where does this take place? What is the "
#     "environment, background, or location?\n\n"
#     "4. MOOD & TONE — What feeling or atmosphere does the image convey?\n\n"
#     "5. ORIGINAL PURPOSE — What is this image likely for? "
#     "(e.g. advertisement, news photo, artwork, screenshot, meme, "
#     "product shot, personal photo)\n\n"
#     "6. ANY TEXT OR LABELS — Transcribe all readable text exactly as it appears.\n\n"
#     "7. NOTABLE DETAILS — Anything unusual, specific, or important that "
#     "a viewer should not miss.\n\n"
#     "Be factual. Do not guess what is not visible. "
#     "If something is unclear, say so."
# )
IMAGE_AGENT_INSTRUCTION = (
    """Analyze this image and describe: 
    The main action or subject in one sentence., 
    Everything visible — people, objects, colors, clothing, expressions., 
    The visual style — photo, illustration, AI art, meme, diagram, lighting, composition., 
    The setting and mood — location, time, era, and emotional atmosphere., 
    Purpose and text — why this image likely exists, and transcribe any visible text exactly.
    Only describe what you can actually see. Say \"unclear\" if unsure — never guess or assume."""
)


def create_image_agent() -> LlmAgent:
    """
    Build an LlmAgent specialised in describing images.
    Kept for ADK-native agentic workflows; vision API calls use LiteLLM directly.
    """
    return LlmAgent(
        model=get_ollama_model(),
        name="image_description_agent",
        instruction=IMAGE_AGENT_INSTRUCTION,
    )
