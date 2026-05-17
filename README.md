# Live2D Motion Recorder

A desktop application for recording, editing, and exporting Live2D motion parameters from VTube Studio. Built with Python and PyQt6.

## Features

- Real-time parameter recording from VTube Studio via WebSocket API
- Playback preview with timeline and interpolation
- Motion optimization (smoothing, duplicate removal, keyframe reduction)
- Export to JSON or compressed format
- Send motion back to VTube Studio for live preview
- Clean, minimal dark UI

## Requirements

- Python 3.11 or higher
- VTube Studio (with WebSocket API enabled)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Connect to VTube Studio

1. Open VTube Studio
2. Go to **Settings > Connect to app**
3. Enable **Activate WebSocket API** (default port: 8002)
4. Click **Connect** in Motion Recorder
5. Accept the authentication prompt in VTube Studio

### Record Motion

1. Select recording FPS (30 or 60)
2. Click **Record**
3. Perform your motion in VTube Studio
4. Click **Stop** when finished

### Playback & Export

- Click **Play** to preview the recorded motion
- Use the timeline to seek through frames
- **Save as JSON** for standard motion files
- **Save as Compressed** for smaller file size
- **Send to VTS** to replay motion on your model live

## Motion File Format

```json
{
  "meta": {
    "fps": 60,
    "duration": 12.5,
    "frame_count": 750,
    "created_at": "2026-05-16T00:00:00+00:00",
    "parameters": ["ParamAngleX", "ParamAngleY", "..."]
  },
  "frames": [
    {
      "time": 0.0,
      "params": {
        "ParamAngleX": 12.3,
        "ParamEyeLOpen": 0.1
      }
    }
  ]
}
```

## Project Structure

```
MotionRecorder/
├── app/
│   ├── core/           Configuration, events, timing
│   ├── vtubestudio/    WebSocket client and authentication
│   ├── recorder/       Recording engine and optimizer
│   ├── playback/       Playback engine and interpolator
│   ├── exporter/       File export and project management
│   ├── ui/             PyQt6 interface components
│   └── main.py         Application entry point
├── data/
│   ├── motions/        Saved motion files
│   └── projects/       Project files
├── requirements.txt
├── run.py
└── README.md
```

## Architecture

```
VTube Studio (WebSocket)
    ↓
Tracking Client
    ↓
Recorder Engine → Frame Buffer → Optimizer
    ↓
Motion Asset (JSON)
    ↓
Playback Engine → Interpolator
    ↓
GUI (Timeline, Parameters, Stats)
```

## Troubleshooting

**Connection Failed**
- Ensure VTube Studio is running
- Verify WebSocket API is enabled in Settings
- Check the port matches (default: 8002)

**No Parameters Showing**
- Make sure a model is loaded in VTube Studio
- Reconnect after loading a model

**Recording Empty**
- Confirm connection status shows "Authenticated"
- Ensure the model is moving during recording

## License

MIT License

Copyright (c) 2026 Fainshe

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
