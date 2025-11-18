# Colory PPrint

**Colory PPrint** is your new best friend when it comes to logging in Python—especially if you like your logs colorful, stylish, and super readable! Say goodbye to bland, hard-to-read logs and hello to clean, color-coded JSON logs with all the bells and whistles. Plus, it’s got your back when logging things that Python doesn't like to serialize.

## Features:

- 🎨 **Color-coded JSON logs**: Pick your foreground and background colors for that perfect contrast.
- ✨ **Text styles**: Bold, underline, reverse, and even concealed—make your logs pop!
- 🔧 **Customizable**: Tweak the logging to your heart’s content, perfect for debugging and visualizing data.
- 🧩 **Handles non-serializable objects**: Logs things like custom classes by showing their type and memory address. Nothing gets left behind.

## Installation

Getting Colory PPrint up and running is a breeze! Choose one of these two methods:

1. From the GitHub repo directly:

   ```bash
   pip install git+https://github.com/ruhiddin/colory-pprint.git
   ```

2. Alternatively, from PyPI (because we’re all about simplicity):
   ```bash
   pip install colory_pprint
   ```

## Usage

### Basic Usage:

Start logging with a simple import and one-liner. Like magic.

```python
from colory_pprint import ColoryPPrint

log = ColoryPPrint(debug=True)

log({"message": "Hello, World!"})
```

### Logging with Colors and Styles:

Why stick to plain text when you can have colorful, styled logs?

```python
log.red.bold({"status": "error", "message": "Oops! Something went wrong."})
log.green.on_black.underline({"status": "success", "message": "All systems go!"})
```

### Handling Non-Serializable Objects:

Got an object that Python doesn’t know how to handle? No worries. Colory PPrint logs it with style anyway, using the `repr()` function.

```python
class CustomObject:
    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value

custom_obj = CustomObject(name="Test", value=100)

log.red.bold({
    "status": "error",
    "message": "Something failed!",
    "object": custom_obj
})
```

The output will look something like this:

```json
{
  "status": "error",
  "message": "Something failed!",
  "object": "<CustomObject object at 0x7f8a3f8b93d0>"
}
```

### Available Colors:

**Foreground**: black, red, green, yellow, blue, magenta, cyan, white, grey, light_red, light_green, light_yellow, light_blue, light_magenta, light_cyan, light_white.  
**Background**: on_black, on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan, on_white, on_grey, on_light_red, on_light_green, on_light_yellow, on_light_blue, on_light_magenta, on_light_cyan, on_light_white.

### Available Text Styles:

- bold
- underline
- reverse
- concealed

### Debug Mode:

Got some tricky bugs? Turn on debug mode to see all the inner workings of your logging.

```python
log = ColoryPPrint(debug=True)
log({"message": "Debug mode: ON! See everything in style."})
```

_(Just remember to switch it off in production, unless you want your logs to throw a party.)_

Now go on, add some color to those logs, and make debugging feel like a breeze!
