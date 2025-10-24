from mcp.server.fastmcp import FastMCP
from todo import TodoList

mcp = FastMCP("todo_server")

todo_list = TodoList()

@mcp.tool()
async def add_todo_item(description: str) -> dict:
    """Add a new todo item.

    Args:
        description: The description of the todo item
    """
    todo_list.add_item(description)
    return {"message": "Item added successfully."}  

@mcp.tool()
async def mark_todo_completed(item_id: int) -> dict:
    """Mark a todo item as completed.

    Args:
        item_id: The ID of the todo item
    """
    try:
        item = todo_list.mark_completed(item_id)
        return {"message": f"Item {item.id} marked as completed."}
    except ValueError as e:
        return {"error": str(e)}
    

@mcp.tool()
async def get_pending_todo_items() -> list[dict]:
    """Get all pending todo items."""
    pending_items = todo_list.get_pending_items()
    return [item.dict() for item in pending_items]  


@mcp.tool()
async def get_completed_todo_items() -> list[dict]:
    """Get all completed todo items."""
    completed_items = todo_list.get_completed_items()
    return [item.dict() for item in completed_items]

@mcp.tool()
async def remove_todo_item(item_id: int) -> dict:
    """Remove a todo item.

    Args:
        item_id: The ID of the todo item
    """
    todo_list.remove_item(item_id)
    return {"message": f"Item {item_id} removed successfully."}


@mcp.resource("todo://todo_server/items")
async def read_todo_items_resource() -> list[dict]:
    """Read all todo items as a resource."""
    return [item.dict() for item in todo_list.items]

if __name__ == "__main__":
    mcp.run(transport='stdio')