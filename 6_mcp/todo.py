from pydantic import BaseModel

class TodoItem(BaseModel):
    id: int
    description: str
    completed: bool = False

class TodoList(BaseModel):
    items: list[TodoItem] = [TodoItem(id=1, description="Sample Task"), TodoItem(id=2, description="Another Task", completed=True), TodoItem(id=3, description="Third Task"), TodoItem(id=4, description="Fourth Task", completed=True)]

    def add_item(self, description: str):
        new_id = len(self.items) + 1
        item = TodoItem(id=new_id, description=description)
        self.items.append(item)

    def mark_completed(self, item_id: int):
        for item in self.items:
            if item.id == item_id:
                item.completed = True
                return item
        raise ValueError(f"Item with id {item_id} not found.")

    def get_pending_items(self) -> list[TodoItem]:
        return [item for item in self.items if not item.completed]
    
    def get_completed_items(self) -> list[TodoItem]:
        return [item for item in self.items if item.completed]
    
    def remove_item(self, item_id: int):
        self.items = [item for item in self.items if item.id != item_id]