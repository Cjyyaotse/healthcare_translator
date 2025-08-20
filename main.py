from reactpy import component, html, hooks, run
from services.speech_to_text import start_streaming, stop_streaming
from services.translate import generate_translations
from services.text_to_speech import text_to_speech, play_audio


@component
def App():
    # State variables
    input_lang, set_input_lang = hooks.use_state("english")
    target_lang, set_target_lang = hooks.use_state("french")
    transcript, set_transcript = hooks.use_state("")
    translation, set_translation = hooks.use_state("")
    audio_file, set_audio_file = hooks.use_state(None)
    is_recording, set_is_recording = hooks.use_state(False)

    async def handle_start(event):
        set_is_recording(True)
        set_transcript("")
        set_translation("")
        set_audio_file(None)

        text = start_streaming()  # blocking stream
        set_transcript(text)

        # After recording ends, translate & generate audio
        translated = generate_translations(text, input_lang, target_lang)
        set_translation(translated)

        audio_path = text_to_speech(translated)
        set_audio_file(audio_path)

        set_is_recording(False)

    async def handle_stop(event):
        stop_streaming()
        set_is_recording(False)

    async def handle_play(event):
        if audio_file:
            play_audio(audio_file)

    return html.div(
        {
            "style": {
                "maxWidth": "600px",
                "margin": "auto",
                "padding": "1rem",
                "fontFamily": "Arial, sans-serif",
                "display": "flex",
                "flexDirection": "column",
                "gap": "1rem",
            }
        },
        html.h1({"style": {"textAlign": "center"}}, "🌍 Health Translator App"),

        # Input language selector
        html.div(
            {"style": {"display": "flex", "flexDirection": "column"}},
            html.label("Input Language"),
            html.input({
                "type": "text",
                "value": input_lang,
                "onChange": lambda e: set_input_lang(e["target"]["value"]),
                "placeholder": "e.g., english",
                "style": {"padding": "0.5rem", "fontSize": "1rem"},
            }),
        ),

        # Target language selector
        html.div(
            {"style": {"display": "flex", "flexDirection": "column"}},
            html.label("Target Language"),
            html.input({
                "type": "text",
                "value": target_lang,
                "onChange": lambda e: set_target_lang(e["target"]["value"]),
                "placeholder": "e.g., french",
                "style": {"padding": "0.5rem", "fontSize": "1rem"},
            }),
        ),

        # Start/Stop buttons
        html.div(
            {"style": {"display": "flex", "gap": "1rem"}},
            html.button(
                {
                    "onClick": handle_start,
                    "disabled": is_recording,  # disable while recording
                    "style": {
                        "padding": "0.75rem",
                        "fontSize": "1rem",
                        "background": "#007BFF" if not is_recording else "#ccc",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "8px",
                    },
                },
                "🎤 Start Recording",
            ),
            html.button(
                {
                    "onClick": handle_stop,
                    "disabled": not is_recording,  # disable if not recording
                    "style": {
                        "padding": "0.75rem",
                        "fontSize": "1rem",
                        "background": "#dc3545" if is_recording else "#ccc",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "8px",
                    },
                },
                "⏹ Stop Recording",
            ),
        ),

        # Transcript
        html.div(
            {"style": {"background": "#f1f1f1", "padding": "0.75rem", "borderRadius": "8px"}},
            html.h3("Transcript (Input):"),
            html.p(transcript or "No input yet."),
        ),

        # Translation
        html.div(
            {"style": {"background": "#f9f9f9", "padding": "0.75rem", "borderRadius": "8px"}},
            html.h3("Translation (Output):"),
            html.p(translation or "No translation yet."),
        ),

        # Speak button
        html.button(
            {
                "onClick": handle_play,
                "disabled": not audio_file,
                "style": {
                    "padding": "0.75rem",
                    "fontSize": "1rem",
                    "background": "#28a745" if audio_file else "#ccc",
                    "color": "white",
                    "border": "none",
                    "borderRadius": "8px",
                },
            },
            "🔊 Speak",
        ),
    )


if __name__ == "__main__":
    run(App)
