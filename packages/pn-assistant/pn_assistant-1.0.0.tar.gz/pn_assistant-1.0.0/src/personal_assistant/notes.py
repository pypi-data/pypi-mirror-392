from .fields import Title, Content, Tags
from .colorize import Colorize

class Note:
    """Class representing a single note with title, content, and tags."""

    def __init__(self, title, content=None, tags=None):
        """Initializes a note with a title, content, and tags."""
        self.title = Title(title)
        self.content = Content(content)
        self.tags = Tags(tags) if tags else ""
    
    def __str__(self) -> str:
        """Returns a string representation of the note."""
        title_str = f"Title: {self.title.value}"
        content_str = f"Content: {self.content}" if self.content else ""
        tag_str = f"Tags: {self.tags}" if self.tags else ""
        return "\n".join(filter(None, [title_str, content_str, tag_str]))
    

class Notes:
    """Class managing a collection of notes."""
    
    def __init__(self):
        """Initializes an empty collection of notes."""
        self.notes = []

    def _get_tags_text(self, note) -> str:
        # Helper method (Private) to get the text of a note's tags
        if hasattr(note, 'tags'):
            t = note.tags
            if hasattr(t, 'value'):
                return str(t.value)
            return str(t)
        return ""

    def add_note(self, title, text=None, tags=None) -> str:
        """Adds a new note to the collection."""
        if self.find_note_by_title(title):
            raise ValueError(Colorize.error(f"Note with title '{title}' already exists"))
        note = Note(title, text, tags)
        self.notes.append(note)
        return Colorize.success(f"Note with title '{title}' added successfully.")
    
    def find_note_by_title(self, title):
        """Finds a note by its title."""
        if not title:
            raise ValueError(Colorize.warning("Title is required"))
        for note in self.notes:
            if note.title.value == title:
                return note
        return None
    
    def delete_note(self, title) -> str:
        """Deletes a note by its title."""
        note = self.find_note_by_title(title)
        if note:
            self.notes.remove(note)
            return Colorize.success(f"Note with title '{title}' deleted successfully.")
        else:
            return Colorize.error(f"Note with title '{title}' not found")
        
    def change_note(self, title, new_content, new_tags) -> str:
        """Changes the content and/or tags of a note by its title."""
        note = self.find_note_by_title(title)
        if note:
            note.content = Content(new_content) if new_content else note.content
            note.tags = Tags(new_tags) if new_tags else note.tags
            return Colorize.success(f"Note with title '{title}' updated successfully.")
        else:
            return Colorize.error(f"Note with title '{title}' not found")
        
    def find_note_by_tag(self, tag: str) -> list:
        """Finds notes by a specific tag."""
        if not tag:
            raise ValueError(Colorize.warning("Tag is required"))
        matched_notes = []
        tag = tag.strip().lower()
        for note in self.notes:
            tags_text = self._get_tags_text(note).lower()

            actual_tags = [t.strip() for t in tags_text.split(',')]
            if tag in actual_tags:
                matched_notes.append(note)
        # Sort notes by title in alphabetical order
        matched_notes.sort(key=lambda x: str(x.title).lower())  
        return matched_notes
    
    def show_all_notes(self) -> str:
        """Shows all notes in the collection."""
        if not self.notes:
            return Colorize.error("No notes available.")
        divider = "-" * 40
        notes_str = "\n".join(f"{divider}\n{str(note)}\n{divider}" for note in self.notes)
        return notes_str
    