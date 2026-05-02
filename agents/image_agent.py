from google.adk.agents import LlmAgent

from agents.base import get_ollama_model


def create_image_agent() -> LlmAgent:
    """
    Build an LlmAgent specialised in describing images.

    The agent receives a multimodal message (inline image + text prompt)
    and returns a structured, detailed description.
    """
    return LlmAgent(
        model=get_ollama_model(),
        name="image_description_agent",
        instruction=(
            "You are an expert image analyst. When given an image, provide a "
            "comprehensive description covering:\n"
            "- Main subjects or focal points\n"
            "- Colors, lighting, and visual style\n"
            "- Composition and spatial layout\n"
            "- Setting, background, and context\n"
            "- Actions or emotions depicted\n"
            "- Any notable text, objects, or details\n\n"
            "Be specific, objective, and thorough. "
            "Respond only with the description — no preamble or sign-off."
        ),
    )
