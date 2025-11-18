# PowerPoint MCP Server

A Python-based MCP (Model Context Protocol) server for creating and managing PowerPoint presentations using [python-pptx](https://python-pptx.readthedocs.io/).

## Features

- **Create presentations** with title slides
- **Add various slide types**: title slides, text slides with bullets, image slides, blank slides
- **Add content elements**: textboxes, shapes (rectangle, oval, etc.), tables
- **Query presentations**: get slide count, presentation info
- **Full programmatic control** over PowerPoint files without requiring Microsoft Office

## Installation

### From PyPI (Recommended)

```bash
pip install mcp-pptx-tools
```

### From Source

```bash
git clone https://github.com/Prathush21/powerpoint-mcp.git
cd powerpoint-mcp
pip install -e .
```

### Prerequisites

- Python 3.10 or higher
- pip

## Usage

### Running the server

```bash
python -m powerpoint_mcp.server
```

Or if installed:

```bash
powerpoint-mcp
```

### MCP Client Configuration

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "powerpoint": {
      "command": "python",
      "args": ["-m", "powerpoint_mcp.server"]
    }
  }
}
```

Or with full path:

```json
{
  "mcpServers": {
    "powerpoint": {
      "command": "/path/to/python",
      "args": ["/path/to/powerpoint-mcp/powerpoint_mcp/server.py"]
    }
  }
}
```

## Available Tools

### 1. create_presentation

Create a new PowerPoint presentation.

**Parameters:**
- `filepath` (required): Path where the presentation will be saved
- `title` (optional): Title for the title slide
- `subtitle` (optional): Subtitle for the title slide

**Example:**
```json
{
  "filepath": "my_presentation.pptx",
  "title": "My Awesome Presentation",
  "subtitle": "Created with MCP"
}
```

### 2. add_title_slide

Add a title slide to an existing presentation.

**Parameters:**
- `filepath` (required): Path to the PowerPoint file
- `title` (required): Title text
- `subtitle` (optional): Subtitle text

**Example:**
```json
{
  "filepath": "presentation.pptx",
  "title": "Welcome",
  "subtitle": "Introduction to MCP"
}
```

### 3. add_text_slide

Add a slide with title and bullet points.

**Parameters:**
- `filepath` (required): Path to the PowerPoint file
- `title` (required): Slide title
- `content` (required): Array of strings for bullet points

**Example:**
```json
{
  "filepath": "presentation.pptx",
  "title": "Key Features",
  "content": [
    "Easy to use",
    "Powerful automation",
    "Cross-platform compatibility",
    "No Microsoft Office required"
  ]
}
```

### 4. add_image_slide

Add a slide with a title and an image.

**Parameters:**
- `filepath` (required): Path to the PowerPoint file
- `title` (required): Slide title
- `image_path` (required): Path to the image file
- `left` (optional): Left position in inches (default: 1.5)
- `top` (optional): Top position in inches (default: 2.5)
- `width` (optional): Image width in inches (default: 6)

**Example:**
```json
{
  "filepath": "presentation.pptx",
  "title": "Our Product",
  "image_path": "/path/to/image.png",
  "left": 2,
  "top": 2,
  "width": 5
}
```

### 5. add_blank_slide

Add a blank slide to the presentation.

**Parameters:**
- `filepath` (required): Path to the PowerPoint file

**Example:**
```json
{
  "filepath": "presentation.pptx"
}
```

### 6. add_textbox

Add a textbox to the last slide with custom positioning.

**Parameters:**
- `filepath` (required): Path to the PowerPoint file
- `text` (required): Text content
- `left` (required): Left position in inches
- `top` (required): Top position in inches
- `width` (required): Width in inches
- `height` (required): Height in inches
- `font_size` (optional): Font size in points (default: 18)
- `bold` (optional): Make text bold (default: false)

**Example:**
```json
{
  "filepath": "presentation.pptx",
  "text": "Important Note!",
  "left": 1,
  "top": 5,
  "width": 4,
  "height": 1,
  "font_size": 24,
  "bold": true
}
```

### 7. add_shape

Add a shape to the last slide.

**Parameters:**
- `filepath` (required): Path to the PowerPoint file
- `shape_type` (required): Type of shape - 'rectangle', 'oval', 'rounded_rectangle', 'triangle'
- `left` (required): Left position in inches
- `top` (required): Top position in inches
- `width` (required): Width in inches
- `height` (required): Height in inches
- `fill_color` (optional): Fill color in hex format (e.g., '#FF0000')

**Example:**
```json
{
  "filepath": "presentation.pptx",
  "shape_type": "rectangle",
  "left": 2,
  "top": 3,
  "width": 4,
  "height": 2,
  "fill_color": "#4472C4"
}
```

### 8. add_table

Add a table to the last slide.

**Parameters:**
- `filepath` (required): Path to the PowerPoint file
- `rows` (required): Number of rows
- `cols` (required): Number of columns
- `data` (required): 2D array of table data (rows x cols)
- `left` (optional): Left position in inches (default: 1)
- `top` (optional): Top position in inches (default: 2)
- `width` (optional): Table width in inches (default: 8)
- `height` (optional): Table height in inches (default: 4)

**Example:**
```json
{
  "filepath": "presentation.pptx",
  "rows": 3,
  "cols": 3,
  "data": [
    ["Header 1", "Header 2", "Header 3"],
    ["Data 1", "Data 2", "Data 3"],
    ["Data 4", "Data 5", "Data 6"]
  ]
}
```

### 9. get_slide_count

Get the number of slides in a presentation.

**Parameters:**
- `filepath` (required): Path to the PowerPoint file

**Example:**
```json
{
  "filepath": "presentation.pptx"
}
```

### 10. get_presentation_info

Get detailed information about a presentation.

**Parameters:**
- `filepath` (required): Path to the PowerPoint file

**Example:**
```json
{
  "filepath": "presentation.pptx"
}
```

## Testing

Run the test suite:

```bash
python test_server.py
```

This will:
1. Start the MCP server
2. Run comprehensive tests of all tools
3. Create a test presentation (`test_presentation.pptx`)
4. Display test results
5. Clean up and shut down

## Example Workflow

```python
# 1. Create a new presentation
create_presentation(filepath="demo.pptx", title="Sales Report", subtitle="Q4 2024")

# 2. Add content slides
add_text_slide(
    filepath="demo.pptx",
    title="Overview",
    content=["Revenue increased 25%", "New customers: 1,200", "Market expansion successful"]
)

# 3. Add a table with data
add_blank_slide(filepath="demo.pptx")
add_table(
    filepath="demo.pptx",
    rows=4,
    cols=3,
    data=[
        ["Quarter", "Revenue", "Growth"],
        ["Q1", "$1.2M", "15%"],
        ["Q2", "$1.5M", "20%"],
        ["Q3", "$1.8M", "25%"]
    ]
)

# 4. Add visual elements
add_blank_slide(filepath="demo.pptx")
add_shape(
    filepath="demo.pptx",
    shape_type="rectangle",
    left=1, top=2, width=3, height=2,
    fill_color="#00B050"
)
add_textbox(
    filepath="demo.pptx",
    text="Revenue Growth",
    left=1.5, top=2.5, width=2, height=0.5,
    font_size=20, bold=True
)

# 5. Get info
get_presentation_info(filepath="demo.pptx")
```

## Architecture

The server is built using:
- **MCP SDK**: For Model Context Protocol implementation
- **python-pptx**: For PowerPoint file manipulation
- **asyncio**: For asynchronous operation handling

## Limitations

- Some advanced PowerPoint features are not supported by python-pptx
- Charts and complex animations require additional implementation
- The server operates on files (not in-memory editing with auto-save)

## Contributing

Contributions are welcome! Areas for enhancement:
- Add chart support (bar, line, pie charts)
- Add more shape types
- Support for themes and templates
- Slide master customization
- Animation support

## License

MIT

## Resources

- [python-pptx Documentation](https://python-pptx.readthedocs.io/)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
