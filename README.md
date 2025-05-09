# TOEFL Exam Trainer

A Streamlit-based TOEFL Reading & Writing Exam Simulator powered by Google Gemini (Gemini 2.0 Flash). This app generates realistic TOEFL-style reading passages, questions, and writing prompts, enforces time limits, and provides automated feedback on essays.

![](https://www.filepicker.io/api/file/BaHwQ3SvTKKoTHb1DVG6)
---
## App
https://aitoefttrainer.streamlit.app/

## Features

* **Reading Practice**

  * Dynamically generates academic passages (400–600 words) on diverse topics.
  * Creates multiple-choice questions across all TOEFL question types (factual, inference, vocabulary, etc.).
  * Enforces a 35-minute timer for reading sessions.

* **Writing Practice**

  * Supports both Integrated (20-minute) and Independent (30-minute) writing tasks.
  * Generates reading passages and lecture summaries for Integrated tasks.
  * Enforces time limits and captures essays.

* **Automated Feedback**

  * Uses Gemini to analyze submitted essays.
  * Scores essays on development, organization, language use, and relevance.
  * Provides overall scoring and detailed recommendations.

* **Session Management**

  * Tracks user answers, timers, used topics, and used writing themes in Streamlit session state.
  * Allows navigation between Home, Reading, and Writing via sidebar.

---

## Prerequisites

* Python 3.7 or higher
* A valid Google Gemini API key (Gemini 2.0 Flash)

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/toefl-exam-trainer.git
   cd toefl-exam-trainer
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   .\\venv\\Scripts\\activate # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** in the project root and add your API key:

   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

---

## Configuration

* **Environment Variables**

  * `GEMINI_API_KEY`: Your Google Gemini API key.

* **Model Settings**

  * The default model is `gemini-2.0-flash`. To change it, update the `MODEL` constant in `app.py`.

---

## Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

**Navigate** using the sidebar:

* **Home**: Overview and links to practice modules.
* **Reading Practice**: Configure question types and number, then start.
* **Writing Practice**: Choose Integrated or Independent, generate prompt, and write.

---

## Project Structure

```
├── app.py                # Main Streamlit application
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not checked into VCS)
└── README.md             # This documentation
```

---

## Helper Functions Overview

* **call\_gemini()**: Handles API calls and extracts text safely.
* **get\_reading\_topic()**: Rotates among academic topics for reading passages.
* **get\_writing\_theme()**: Rotates among writing themes for Integrated/Independent tasks.
* **Timer utilities**: `start_timer()`, `format_time()`, and `is_timer_expired()` manage session timers.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with enhancements or bug fixes.

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.
