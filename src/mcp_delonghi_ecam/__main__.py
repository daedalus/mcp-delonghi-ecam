from mcp_delonghi_ecam.mcp import mcp


def main() -> int:
    """Run the MCP server."""
    mcp.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
