from webquest_mcp.app import mcp


def main() -> None:
    mcp.run(transport="streamable-http")
