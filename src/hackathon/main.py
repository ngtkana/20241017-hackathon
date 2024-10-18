from langchain_google_vertexai import ChatVertexAI, HarmCategory, HarmBlockThreshold
from langchain_google_vertexai import ChatVertexAI
import base64
from langchain_core.messages.human import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from textwrap import dedent
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from pathlib import Path
from pydantic import BaseModel, Field, create_model
from typing import Optional
from langchain.output_parsers import PydanticOutputParser
from langchain_core.output_parsers.pydantic import _PYDANTIC_FORMAT_INSTRUCTIONS
import click
import pandas as pd
import json

def create_default_response_model():
    attributes = {
        "original": (Optional[str], Field(description="given ocr text", required=False)),
        "corrected": (Optional[str], Field(description="llm-corrected text", required=False)),
    }
    return create_model("Response", **attributes)


class JapanizePydanticOutputParser(PydanticOutputParser):
    """Parser with ensure_ascii=False for PydanticOutputParser"""

    def get_format_instructions(self) -> str:
        """Return the format instructions for the JSON output.

        Returns:
            The format instructions for the JSON output.
        """
        # Copy＾ schema to avoid altering original Pydantic schema.
        schema = {k: v for k, v in self.pydantic_object.schema().items()}

        # Remove extraneous fields.
        reduced_schema = schema
        if "title" in reduced_schema:
            del reduced_schema["title"]
        if "type" in reduced_schema:
            del reduced_schema["type"]
        # Ensure json in context is well-formed with double quotes.
        schema_str = json.dumps(reduced_schema, ensure_ascii=False)

        return _PYDANTIC_FORMAT_INSTRUCTIONS.format(schema=schema_str)


@click.command()
@click.argument(
    'field_name',
    type=str,
    default="DueDate",
)
@click.argument(
    'tenant-id',
    type=str,
    default="011dd18a-c571-4826-be22-f8be5e07cf1e",
)
def main(
    field_name: str,
    tenant_id: str,
):
    input = Path('input') / tenant_id / f'{field_name}.csv'
    output = Path('output') / tenant_id / f'{field_name}.csv'
    safety_settings = {
        HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    }
    model = ChatVertexAI(
        model="gemini-1.5-pro-002",
        location="asia-northeast1",
        temperature=0.0,
        generation_config={"response_mime_type": "application/json"},
        safety_settings=safety_settings,
        project="ai-lab-drawer-ml-dev",
        top_p=0.75,
        seed=42,
    )


    schema = create_default_response_model()
    parser = JapanizePydanticOutputParser(pydantic_object=schema)
    system_prompt = dedent(
        f"""
        You are a manufacturing expert.
        You will be given an image of a cell in the title block of a drawing and the OCR result.
        If the OCR result is incorrect, please output the correction result.
        If it is correct, please output it as is without making any changes.

        Note that images often contain not only text but also surrounding borders. Be careful not to mistake the border for "1" or similar.        ## Schema

        ## Schema
        {parser.get_format_instructions()}
        """
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    chain = prompt | model | parser


    input_df = pd.read_csv(input)
    column_image_name = []
    column_original = []
    column_corrected = []
    for index, row in enumerate(input_df.itertuples()):
        print(f"[{index}/{input_df.shape[0]}] Processing {row.image_name}...")
        with open(input.parent / input.stem / f"{row.image_name}.png", "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        target_messages = [
            {
                "type": "text",
                "text": "[Target] Image is shown below",
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{encoded_image}"},
            },
            {
                "type": "text",
                "text": "[Target] OCR results are shown below",
            },
            {
                "type": "text",
                "text": row.values
            }
        ]
        human_message = [HumanMessage(content=target_messages)]
        result = chain.invoke({"messages": human_message})
        column_image_name.append(row.image_name)
        column_original.append(result.original)
        column_corrected.append(result.corrected)

    output_df = pd.DataFrame({
        "image_name": column_image_name,
        "original": column_original,
        "corrected": column_corrected
    })
    print(output_df)
    output_df.to_csv(output, index=False)

if __name__ == "__main__":
    print("Start") 
    main()
    print("Done")
