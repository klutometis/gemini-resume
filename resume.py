# Given a PDF resume, searches for jobs on LinkedIn and finds relevant
# problems on LeetCode; run with e.g.:
#
#   bazel run -c opt :resume
import json

import vertexai
from vertexai.preview.generative_models import (
    GenerativeModel,
    Part,
    Content,
    FunctionDeclaration,
    Tool,
)


def get_secret(key: str) -> str:
    with open("secrets.json", "r") as file:
        return json.load(file)[key]


def generate_python(tool_call):
    arguments = ", ".join(f'{key}="{value}"' for key, value in tool_call.args.items())
    return f"{tool_call.name}({arguments})"


def print_markdown(string: str) -> None:
    print(string)


def run_python(code):
    from io import StringIO
    from contextlib import redirect_stdout

    f = StringIO()
    with redirect_stdout(f):
        exec(code)
    return f.getvalue()


def search_google(engine, query):
    from googleapiclient.discovery import build

    service = build("customsearch", "v1", developerKey=get_secret("developer_key"))

    res = (
        service.cse()
        .list(
            q=query,
            cx=engine,
            num=10,
        )
        .execute()
    )

    links = ""

    for item in res["items"]:
        links += f"- [{item['title']}]({item['link']})\n"

    print(links)


def summarize_resume(model, uri) -> str:
    return model.generate_content(
        [
            "Can you summarize this resume, paying particular attention to: where the candidate lives; skills; work experience? If you don't know something, omit it.",
            Part.from_uri(uri, mime_type="image/jpeg"),
        ]
    ).text


def search_jobs(city, job_title):
    search_google("823489c44ec984355", f"{city} {job_title}")


def call_search_jobs(model, resume):
    search_jobs_api = FunctionDeclaration(
        name="search_jobs",
        description="Searches for jobs in a given area and matching a certain description and title.",
        parameters={
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "job_title": {"type": "string"},
            },
        },
    )

    return (
        model.generate_content(
            [
                "Given the following resume, please search for appropriate jobs where they live.",
                resume,
            ],
            tools=[Tool(function_declarations=[search_jobs_api])],
        )
        .candidates[0]
        .content.parts[0]
        .function_call
    )


def search_leetcode(job_title, **kwargs):
    search_google("753d852d92b9949c0", job_title)


def call_search_leetcode(model, resume):
    search_leetcode_api = FunctionDeclaration(
        name="search_leetcode",
        description="Searches for LeetCode problems for a given job.",
        parameters={
            "type": "object",
            "properties": {
                "job_title": {"type": "string"},
            },
        },
    )

    return (
        model.generate_content(
            [
                "Given the following resume, please search for LeetCode problems appropriate for their job.",
                resume,
            ],
            tools=[Tool(function_declarations=[search_leetcode_api])],
        )
        .candidates[0]
        .content.parts[0]
        .function_call
    )


def main():
    vertexai.init(project=get_secret("project"), location=None)
    gemini = GenerativeModel("gemini-pro")
    multimodal_gemini = GenerativeModel("gemini-pro-vision")
    resume = summarize_resume(multimodal_gemini, "gs://bard.dog/peter-danenberg.png")
    print(resume)
    search_job_call = call_search_jobs(gemini, resume)
    print(search_job_call)
    search_job_python = generate_python(search_job_call)
    print(search_job_python)
    print_markdown(run_python(search_job_python))
    search_leetcode_call = call_search_leetcode(gemini, resume)
    print(search_leetcode_call)
    search_leetcode_python = generate_python(search_leetcode_call)
    print_markdown(run_python(search_leetcode_python))


if __name__ == "__main__":
    main()
