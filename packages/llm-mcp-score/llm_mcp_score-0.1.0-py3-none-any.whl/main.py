from mcp.server.fastmcp import FastMCP

mcp = FastMCP("llm_mcp_score")

# 1. Echo
@mcp.tool()
def echo(text: str) -> str:
    """Return the input text"""
    return text

# 2. Add two numbers
@mcp.tool()
def add(a: int, b: int) -> int:
    """Return sum of two integers"""
    return a + b

# 3. Multiply two numbers
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Return product of two integers"""
    return a * b

# 4. Reverse string
@mcp.tool()
def reverse(text: str) -> str:
    """Return reversed string"""
    return text[::-1]

# 5. Uppercase
@mcp.tool()
def to_upper(text: str) -> str:
    """Convert text to uppercase"""
    return text.upper()

# 6. Lowercase
@mcp.tool()
def to_lower(text: str) -> str:
    """Convert text to lowercase"""
    return text.lower()

# 7. Concatenate strings
@mcp.tool()
def concat(text1: str, text2: str) -> str:
    """Concatenate two strings"""
    return text1 + text2

# 8. Boolean AND
@mcp.tool()
def logical_and(a: bool, b: bool) -> bool:
    """Return logical AND of two booleans"""
    return a and b

# 9. Boolean OR
@mcp.tool()
def logical_or(a: bool, b: bool) -> bool:
    """Return logical OR of two booleans"""
    return a or b

# 10. Length of string
@mcp.tool()
def length(text: str) -> int:
    """Return length of the input string"""
    return len(text)

def main():
    print("Starting llm_mcp_score MCP server...")
    mcp.run()

if __name__ == "__main__":
    main()
