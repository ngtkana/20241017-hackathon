from langchain_google_vertexai import ChatVertexAI, HarmCategory, HarmBlockThreshold
from langchain_google_vertexai import ChatVertexAI


def main():
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

    response = model.invoke("パンはパンでも食べられないパンはなーんだ？")
    print(response.content)


if __name__ == "__main__":
    print("Start") 
    main()
    print("Done")