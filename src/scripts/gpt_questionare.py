import openai
import json
import regex as re

# Initialize OpenAI API client
client = openai.OpenAI(api_key='sk-proj-PxRpylslPas4pRZUSALzT3BlbkFJwJRGg5P63EFGH9Q0FHYa')


def create_questionnaire(location):
    prompt = f"""
    Create a questionnaire with 8 multiple-choice questions about the movie set location '{location}'.
    Each question should have 4 answer options, only one of which is correct.

    Format the output in JSON as follows:
    [
        {{
            "question": "Question text",
            "options": {{
                "a": "Option 1",
                "b": "Option 2",
                "c": "Option 3",
                "d": "Option 4"
            }},
            "correct_answer": "a"
        }},
        ...
        {{
            "question": "Question text",
            "options": {{
                "a": "Option 1",
                "b": "Option 2",
                "c": "Option 3",
                "d": "Option 4"
            }},
            "correct_answer": "a"
        }}
    ]
    """

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.7
    )

    response = json.loads(completion.choices[0].message.content)

    return response


def get_questionnaire_for(location="Garching"):
    # location = "Eiffel Tower"
    questionnaire = create_questionnaire(location)

    if questionnaire:
        # Print the extracted JSON data
        print("Here is your questionnaire in JSON format:")
        return questionnaire
        print(type(questionnaire))
    else:
        print("Failed to create questionnaire")


