# Grapplecore - Cave Adventure

A turn-based grid platformer where you explore a cave using movement and grappling hook mechanics.

## Controls

### Movement (A/W/D keys):
- **A** - Move left
- **W** - Jump
- **D** - Move right

### Grappling Hook (Arrow keys):
- **Left Arrow** - Grapple left
- **Up Arrow** - Grapple up  
- **Right Arrow** - Grapple right

## Game Features

- **Turn-based gameplay**: The world pauses while you decide your next action, but not if you're free-falling
- **Grid-based platformer**: Precise movement on a grid system
- **Grappling hook mechanics**: Swing and pull yourself around the cave
- **Amber collection**: Collect amber as you explore (displayed in top-left)

## Installation

1. Install Python 3.7 or higher
2. Install pygame:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

```bash
python game.py
```

## Notes
### Discrepancies
Note that there are several differences between the "vibe coded" game and the game proposed.
1. There is no actual grapple rope planned, this is just added to visualize it.
2. The level structure is significantly different from the planned game. Think of this as a debug room showing off each of the mechanics. Typically, the next level would be traversed to by "falling" to a certain block.
3. The bat is not supposed to go through the blocks but due to time constraints, this was just left in.
4. The grapple "count" is not added since this is just a debug room, assume it will be added in the actual game.

### Closing
Thank you for reviewing this submission. Used Cursor for this exercise.