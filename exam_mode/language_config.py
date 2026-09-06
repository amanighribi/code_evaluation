# Maps a language identifier to its Docker image, filename, and
# compile/run commands. Adding a new language means adding an entry here,
# not writing new executor code.

LANGUAGE_CONFIG = {
    "c": {
        "image": "gcc:latest",
        "filename": "main.c",
        "compile_cmd": "gcc main.c -o main_exec 2> compile_errors.txt",
        "run_cmd": "./main_exec",
    },
    "cpp": {
        "image": "gcc:latest",
        "filename": "main.cpp",
        "compile_cmd": "g++ main.cpp -o main_exec 2> compile_errors.txt",
        "run_cmd": "./main_exec",
    },
    "javascript": {
        "image": "node:20-slim",
        "filename": "main.js",
        "compile_cmd": None,
        "run_cmd": "node main.js",
    },
    "ruby": {
        "image": "ruby:3-slim",
        "filename": "main.rb",
        "compile_cmd": None,
        "run_cmd": "ruby main.rb",
    },
    "go": {
        "image": "golang:1.22",
        "filename": "main.go",
        "compile_cmd": None,
        "run_cmd": "go run main.go",
    },
    "php": {
        "image": "php:8-cli",
        "filename": "main.php",
        "compile_cmd": None,
        "run_cmd": "php main.php",
    },
}


def is_language_supported_for_execution(language: str) -> bool:
    return language in ("python", "java") or language in LANGUAGE_CONFIG


def get_language_config(language: str) -> dict:
    return LANGUAGE_CONFIG.get(language)