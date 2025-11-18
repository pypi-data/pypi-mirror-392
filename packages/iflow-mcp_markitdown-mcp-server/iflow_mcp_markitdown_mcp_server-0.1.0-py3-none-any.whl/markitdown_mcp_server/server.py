from os import listdir
from typing import Tuple

import mcp.types as types
from markitdown import MarkItDown
from mcp.server import NotificationOptions, Server, models, stdio

def convert_to_markdown(file_path: str) -> Tuple[str | None, str]:
    try:
        md = MarkItDown()
        result = md.convert(file_path)
        return result.title, result.text_content

    except Exception as e:
        return None, f"Error converting document: {str(e)}"

# Initialize server
app = Server("markitdown-mcp-server")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="md",
            description="Convert document to markdown format using MarkItDown",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "A URI to any document or file"
                    }
                },
                "required": ["file_path"]
            }
        ),
        types.Tool(
            name="ls",
            description="List files in a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to list files"
                    }
                },
                "required": ["directory"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "md":
        file_path = arguments.get("file_path")
        if not file_path:
            raise ValueError("file_path is required")

        try:
            markdown_title, markdown_content = convert_to_markdown(file_path)
            result_text = f"Here is the converted document in markdown format:\n"
            if markdown_title:
                result_text += f"Title: {markdown_title}\n\n"
            result_text += markdown_content

            return [types.TextContent(type="text", text=result_text)]

        except Exception as e:
            raise ValueError(f"Error processing document: {str(e)}")

    elif name == "ls":
        directory = arguments.get("directory")
        if not directory:
            raise ValueError("directory is required")

        try:
            files = listdir(directory)

            # Format the output in a structured, informative way
            file_count = len(files)
            formatted_output = f"Directory listing for: {directory}\n"
            formatted_output += f"Total files: {file_count}\n\n"

            # Group files by type if possible
            extensions = {}
            no_extension = []

            for file in files:
                if "." in file:
                    ext = file.split(".")[-1].lower()
                    if ext not in extensions:
                        extensions[ext] = []
                    extensions[ext].append(file)
                else:
                    no_extension.append(file)

            # Add file groupings to output
            if extensions:
                formatted_output += "Files by type:\n"
                for ext, files_of_type in extensions.items():
                    formatted_output += f"- {ext.upper()} files ({len(files_of_type)}): {', '.join(files_of_type)}\n"

            if no_extension:
                formatted_output += f"\nFiles without extension ({len(no_extension)}): {', '.join(no_extension)}\n"

            # Add complete listing
            formatted_output += "\nComplete file listing:\n"
            for idx, file in enumerate(sorted(files), 1):
                formatted_output += f"{idx}. {file}\n"

            return [types.TextContent(type="text", text=formatted_output)]

        except Exception as e:
            raise ValueError(f"Error listing directory: {str(e)}")

    else:
        raise ValueError(f"Unknown tool: {name}")

async def run():
    async with stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            models.InitializationOptions(
                server_name="markitdown-mcp-server",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
