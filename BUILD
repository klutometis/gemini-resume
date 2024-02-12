load("@pip//:requirements.bzl", "requirement")
load("@rules_python//python:pip.bzl", "compile_pip_requirements")
load("@rules_python//python:py_binary.bzl", "py_binary")

compile_pip_requirements(
    name = "requirements",
    src = "requirements.in",
    requirements_txt = "requirements.txt",
)

py_binary(
    name = "resume",
    srcs = ["resume.py"],
    deps = [
        # requirement("google-api-python-client"),
        requirement("google-cloud-aiplatform"),
        # requirement("requests"),
    ],
)
