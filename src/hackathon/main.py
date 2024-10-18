from langchain_google_vertexai import ChatVertexAI, HarmCategory, HarmBlockThreshold
import base64
import pandas as pd
import json
from langchain_core.messages.human import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from textwrap import dedent
from langchain_core.messages import SystemMessage
from langchain.output_parsers import PydanticOutputParser
from langchain_core.output_parsers.pydantic import _PYDANTIC_FORMAT_INSTRUCTIONS
from pathlib import Path
from pydantic import Field, create_model
from typing import Optional
import os

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

def process(tenant_id: str, field_name: str, drawing_id: str):
    input = Path('input') / tenant_id / f'{field_name}.csv'
    
    # Safety settings
    safety_settings = {
        HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    }

    # VertexAI model setup
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

    # Schema and parser
    schema = create_default_response_model()
    parser = JapanizePydanticOutputParser(pydantic_object=schema)

    system_prompt = dedent(
        f"""
        You are a manufacturing expert.
        You will be given an image of a cell in the title block of a drawing and the OCR result.
        If the OCR result is incorrect, please output the correction result.
        If it is correct, please output it as is without making any changes.

        Note that images often contain not only text but also surrounding borders. Be careful not to mistake the border for "1" or similar.

        For example, the following mistakes are often made:
        - Due to the nature of the drawing, there are lots of commas and lines
        - The numbers have been removed, so there are lots of △ and A's
        
        ## Schema
        {parser.get_format_instructions()}
        """
    )

    # Chat prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    chain = prompt | model | parser

    # Read input CSV
    df = pd.read_csv(input)
    row = next(df[df["image_name"] == drawing_id].itertuples())

    # Open image file and encode it to base64
    image_file_path = input.parent / input.stem / f"{row.image_name}.png"
    with open(image_file_path, "rb") as image_file:
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
    
    # save to `output/tenant_id/field_name/drawing_id.json`
    output = Path('output') / tenant_id / field_name
    if os.path.exists(output) is False:
        os.makedirs(output)
    with open(output / f"{drawing_id}.json", "w") as f:
        json.dump(result.dict(), f, ensure_ascii=False, indent=2)


def main():
    tasks = [
        {
            "tenant_id": "fc81fcd7-b4b9-4c75-beda-215b8dcef4e0",
            "attribute": "DrawingNumber",
            "comment": "図面の性質上、カンマや罫線が入りまくってる",
            "ocr_miss": [
                "DR-33IWPYQ3WBJ8", "DR-33SE4ABFHVAW", "DR-39HEFFOQJG3S",
                "DR-3N6MMZMF3M3Q", "DR-3R67OQGM4IZP"
            ],
            "ocr_correct": [
                "DR-3BSACKHDU3HT", "DR-7PXQ6NPPNUQD", "DR-638WRPMGVZHZ"
            ]
        },
        {
            "tenant_id": "56dde43c-54d4-4775-99e1-d4db86b5a1de",
            "attribute": "DrawingNumber",
            "comment": "改番を取ってしまっていて、△やAが入りまくってる",
            "ocr_miss": [
                "DR-33MYOREOEPAJ", "DR-36OFOWVKDGQB", "DR-39KSJRJD94M4",
                "DR-3AVZMC7OIEXG", "DR-3BBHAOTZDYXP"
            ],
            "ocr_correct": [
                "DR-364QDST4HZP7", "DR-3E8SPKYD8VPS", "DR-3EZWBU7JZ6VS",
                "DR-3SXE3KMFHEUP"
            ]
        },
        # {
        #     "tenant_id": "345c1b16-14fe-42fa-8be0-7208caca6ab5",
        #     "attribute": "Name",
        #     "comment": "日本語の読み取りミス",
        #     "ocr_miss": [
        #         "DR-3SH7MJCJOZ9D", "DR-3YYBVVZJTWD4", "DR-4J6WWH4QVFYP", "DR-6EMSIHL3JHN8"
        #     ],
        #     "ocr_correct": [
        #         "DR-34OMWSTXBJJD", "DR-38OC8WYCHJCL", "DR-3YR8XS7DNAP4"
        #     ]
        # },
        # {
        #     "tenant_id": "b70b9dcc-4bc8-45b7-936e-c7f983ce7a01",
        #     "attribute": "Material",
        #     "comment": "アルファベットの読み取りミス",
        #     "ocr_miss": [
        #         "DR-36E8D6RDBF3V", "DR-36RP9TR6IGE3", "DR-3ASNUZQBTVLL",
        #         "DR-3S3BUFJVQ4WV", "DR-4ESMDJAFVCII"
        #     ],
        #     "ocr_correct": [
        #         "DR-36LBHXTPZTWI", "DR-3TWQFM9EOK6D", "DR-3VKA8TECQ3KF"
        #     ]
        # }
    ]

    # 各タスクを順に処理
    for task in tasks:
        tenant_id = task["tenant_id"]
        attribute = task["attribute"]
        comment = task["comment"]
        ocr_miss_list = task["ocr_miss"]
        ocr_correct_list = task["ocr_correct"]

        print(f"Processing tenant_id: {tenant_id}, Attribute: {attribute}")
        print(f"Comment: {comment}")

        # OCRが間違っているdrawing_idを処理
        for drawing_id in ocr_miss_list:
            print(f"  OCR miss: {drawing_id}")
            process(tenant_id=tenant_id, field_name=attribute, drawing_id=drawing_id)

        # OCRが合っているdrawing_idを処理
        for drawing_id in ocr_correct_list:
            print(f"  OCR correct: {drawing_id}")
            process(tenant_id=tenant_id, field_name=attribute, drawing_id=drawing_id)


if __name__ == "__main__":
    print("Start")
    main()
    print("Done")
