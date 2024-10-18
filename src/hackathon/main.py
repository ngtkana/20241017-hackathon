from langchain_google_vertexai import ChatVertexAI, HarmCategory, HarmBlockThreshold
from langchain_google_vertexai import ChatVertexAI
import base64
from langchain_core.messages.human import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from textwrap import dedent
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from pathlib import Path
import click
import pandas as pd

@click.command()
@click.argument(
    'input',
    type=click.Path(path_type=Path, exists=True),
    default="input/011dd18a-c571-4826-be22-f8be5e07cf1e/DueDate.csv",
)
@click.argument(
    'output',
    type=click.Path(path_type=Path, exists=False),
    default="output/011dd18a-c571-4826-be22-f8be5e07cf1e/DueDate.csv",
)
def main(
    input: Path,
    output: Path,
):
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


    parser = JsonOutputParser()
    system_prompt = dedent(
        f"""
        You are a manufacturing expert.
        You will be given an image of a cell in the title block of a drawing and the OCR result.
        If the OCR result is incorrect, please output the correction result.
        If it is correct, please output it as is without making any changes.

        Please output in JSON format as shown in the following example.
        {{
            "original": "'67-!-30-D",
            "corrected": "'67-1-30-D",
        }}

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
        column_original.append(result["original"])
        column_corrected.append(result["corrected"])

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