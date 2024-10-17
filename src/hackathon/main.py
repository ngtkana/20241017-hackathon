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


@click.command()
@click.option(
    "--input",
    type=click.Path(path_type=Path, exists=True),
    default="input/011dd18a-c571-4826-be22-f8be5e07cf1e/DrawingNumber/DR-34S8UQLQLTNF.png", # '67-1'30-D'
    required=True,
)
def main(
    input: Path,
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

    with open(input, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')


    parser = JsonOutputParser()
    system_prompt = dedent(
        f"""
        Please read the text in the image.

        
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


    target_messages = [
        {
            "type": "text",
            "text": "[Target] Image is shown below",
        },
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{encoded_image}"},
        },
    ]
    human_message = [HumanMessage(content=target_messages)]
    response = chain.invoke({"messages": human_message})

    print(response)


if __name__ == "__main__":
    print("Start") 
    main()
    print("Done")