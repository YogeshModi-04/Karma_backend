from pydantic import BaseModel, Field


class LocationInput(BaseModel):
    area: str = Field(..., description="Neighbourhood or locality name.", examples=["Satellite"])
    city: str = Field(..., description="City name.", examples=["Ahmedabad"])


class VerifyRequest(BaseModel):
    """
    Input for the karma verification endpoint.

    Combine the output of the image-description agent with the user's
    claimed action and location to receive a verdict.
    """

    image_description: str = Field(
        ...,
        description="AI-generated description of the submitted photo (from the vision agent).",
    )
    action_id: str = Field(
        ...,
        description="Karma action ID from karma_categories.json, e.g. 'ENV-P01' or 'BLD-N02'.",
        examples=["ENV-P01"],
    )
    title: str = Field(
        ...,
        description="Short title the user gave to their submission.",
        examples=["Planted neem sapling at community park"],
    )
    description: str = Field(
        ...,
        description="User-written description of what they did.",
    )
    location: LocationInput


class VerifyResponse(BaseModel):
    """Verdict returned by the Chitragupt verification agent."""

    action_id: str = Field(description="The action ID that was evaluated.")
    action_name: str = Field(description="Human-readable name of the action.")
    category_id: str = Field(description="Parent category ID.")
    category_name: str = Field(description="Parent category display name.")
    points: int | float | str = Field(
        description="Points associated with this action (from the rule book)."
    )
    verdict: str = Field(
        description="One of: 'Approved', 'Rejected', 'Human Review'."
    )
    comment: str = Field(
        description="Concise explanation of why the verdict was reached."
    )
