<!-- vocomateAgent/
│
├── data/                     # (likely for datasets or processed data)
├── logs/
├── modules/                  # (custom modules, e.g., melotts)
├── OpenVoice/                # OpenVoice code and checkpoints
│   └── openvoice/
│       └── checkpoints_v2/
├── scripts/                  # Standalone scripts (e.g., clone_voice.py)
├── vocomate_app/
|     vocomate_app/
    ├── asr/
    │   ├── __pycache__/
    │   ├── whisper_asr.py
    │   └── __init__.py                # Speech recognition (Whisper, etc.)
│   ├── assets/               # Audio inputs/outputs
│   ├── context/              # Contextual data (e.g., weather)
│   ├── llm/
    │   ├── __pycache__/
    │   ├── ollama_client.py
    │   └── __init__.py                 # LLM integration
│   ├── tts/                  # TTS modules
│   ├── ui/                   # Frontend/UI code
    |   |__ web_interface_streamlit/py
│   ├── utils/                # Utilities
│   ├── voice_cloning/        # Voice cloning logic
│   └── __init__.py
├── requirements.txt
└── README.md -->
