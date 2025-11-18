# c400g-ptz

ipTIME C400G ONVIF PTZ control wrapper

## Installation

```bash
pip install c400g-ptz
```

## Usage

```python
from c400g_ptz import C400GPTZ

# Connect to camera
cam = C400GPTZ("192.168.1.100", 5000, "admin", "password")

# Step movements (with duration)
cam.left(0.3)
cam.right(0.3)
cam.up(0.5)
cam.down(0.5)

# Continuous movement
cam.start_move("left")
# ... do something ...
cam.stop()

# Generic step with custom duration
cam.step("up", duration=0.4)
```

## API

### `C400GPTZ(ip, port, user, password, *, profile_index=0, default_step_time=0.3, log=None)`

Main PTZ control class.

**Parameters:**
- `ip`: Camera IP address
- `port`: ONVIF port (usually 5000)
- `user`: Username
- `password`: Password
- `profile_index`: ONVIF media profile index (default: 0)
- `default_step_time`: Default duration for step movements in seconds (default: 0.3)
- `log`: Optional logger instance

**Methods:**
- `step(direction, *, duration=None)`: Move in direction for specified duration
- `left(duration=None)`: Move left
- `right(duration=None)`: Move right
- `up(duration=None)`: Move up
- `down(duration=None)`: Move down
- `start_move(direction)`: Start continuous movement
- `stop()`: Stop movement

**Directions:** `"left"`, `"right"`, `"up"`, `"down"`

## Logging

Enable logging to see what's happening:

```python
import logging
logging.basicConfig(level=logging.INFO)

from c400g_ptz import C400GPTZ
cam = C400GPTZ("192.168.1.100", 5000, "admin", "password")
```

## License

MIT
