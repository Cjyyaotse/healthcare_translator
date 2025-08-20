import base64
import threading
from reactpy import component, html, use_state, run, use_effect
from services.speech_to_text import start_recording, stop_recording
from services.translate import generate_translations
from services.text_to_speech import text_to_speech, play_audio_bytes

def create_audio_url(audio_bytes):
    base64_audio = base64.b64encode(audio_bytes).decode('utf-8')
    return f"data:audio/mp3;base64,{base64_audio}"

@component
def App():
    source_lang, set_source_lang = use_state("English")
    target_lang, set_target_lang = use_state("Spanish")
    transcript, set_transcript = use_state("")
    translation, set_translation = use_state("")
    audio_url, set_audio_url = use_state(None)
    recording, set_recording = use_state(False)

    def start_recording_handler(event):
        set_recording(True)
        start_recording()

    def stop_recording_handler(event):
        # Immediately update button text
           set_recording(False)

           # Run stop_recording (blocking) in a separate thread
           def process_transcription():
               new_transcript = stop_recording()
               set_transcript(new_transcript)

           threading.Thread(target=process_transcription).start()
    def translate(event):
        if transcript:
            new_translation = generate_translations(transcript, source_lang, target_lang)
            set_translation(new_translation)

    def play_audio(event):
        if translation:
            audio_bytes = text_to_speech(translation)
            url = create_audio_url(audio_bytes)
            set_audio_url(url)

    @use_effect
    def handle_keydown():
        def on_keydown(event):
            if recording and event["key"] == "Enter":
                stop_recording_handler(event)

        window = js_globals["window"]
        window.addEventListener("keydown", on_keydown)

        def cleanup():
            window.removeEventListener("keydown", on_keydown)

        return cleanup

    languages = ["English", "Spanish", "French", "German", "Chinese"]

    return html.div(
        {
            "style": {
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",
                "padding": "16px",
                "margin": "auto",
                "fontFamily": "Inter, sans-serif",
                "backgroundColor": "#f9fbfd",
                "minHeight": "100vh",
                "boxSizing": "border-box"
            }
        },
        # Header
        html.header(
            {
                "style": {
                    "width": "100%",
                    "maxWidth": "600px",
                    "textAlign": "center",
                    "marginBottom": "20px",
                }
            },
            html.h1(
                {"style": {
                    "fontSize": "1.8rem",
                    "color": "#334155",
                    "marginBottom": "8px"
                }},
                "🌐 Voice Translation App"
            ),
            html.p(
                {"style": {"fontSize": "0.9rem", "color": "#64748b"}},
                "Record speech → Get transcript → Translate → Play"
            )
        ),

        # Language selectors
        html.div(
            {
                "style": {
                    "display": "flex",
                    "gap": "12px",
                    "width": "100%",
                    "maxWidth": "600px",
                    "marginBottom": "16px",
                }
            },
            html.div(
                {"style": {"flex": 1}},
                html.label({"style": {"fontSize": "0.85rem", "color": "#475569"}}, "Input"),
                html.select(
                    {"value": source_lang, "on_change": lambda e: set_source_lang(e["target"]["value"]),
                     "style": {
                         "width": "100%",
                         "padding": "8px",
                         "borderRadius": "8px",
                         "border": "1px solid #cbd5e1",
                         "backgroundColor": "white"
                     }},
                    *[html.option({"value": lang, "key": lang}, lang) for lang in languages]
                )
            ),
            html.div(
                {"style": {"flex": 1}},
                html.label({"style": {"fontSize": "0.85rem", "color": "#475569"}}, "Output"),
                html.select(
                    {"value": target_lang, "on_change": lambda e: set_target_lang(e["target"]["value"]),
                     "style": {
                         "width": "100%",
                         "padding": "8px",
                         "borderRadius": "8px",
                         "border": "1px solid #cbd5e1",
                         "backgroundColor": "white"
                     }},
                    *[html.option({"value": lang, "key": lang}, lang) for lang in languages]
                )
            ),
        ),

        # Recording button
        html.div(
            {"style": {"marginBottom": "20px"}},
            html.button(
                {
                    "on_click": start_recording_handler if not recording else stop_recording_handler,
                    "disabled": False,
                    "style": {
                        "padding": "12px 24px",
                        "borderRadius": "9999px",
                        "border": "none",
                        "backgroundColor": "#3b82f6" if not recording else "#ef4444",
                        "color": "white",
                        "fontSize": "1rem",
                        "cursor": "pointer",
                        "boxShadow": "0 4px 6px rgba(0,0,0,0.1)"
                    }
                },
                "🎤 Start Recording" if not recording else "🛑 Stop Recording (Enter)"
            )if not recording else html.button(
                {
                    "on_click": stop_recording_handler,
                    "style": {
                        "padding": "12px 24px",
                        "borderRadius": "9999px",
                        "border": "none",
                        "backgroundColor": "#ef4444",
                        "color": "white",
                        "fontSize": "1rem",
                        "cursor": "pointer",
                        "boxShadow": "0 4px 6px rgba(0,0,0,0.1)"
                    }
                },
                "🛑 Stop Recording (Enter)"
            )
        ),

        # Transcript card
        html.div(
            {
                "style": {
                    "width": "100%",
                    "maxWidth": "600px",
                    "backgroundColor": "white",
                    "borderRadius": "12px",
                    "padding": "16px",
                    "marginBottom": "16px",
                    "boxShadow": "0 2px 8px rgba(0,0,0,0.05)"
                }
            },
            html.h3({"style": {"marginBottom": "8px", "color": "#1e293b"}}, "Transcript"),
            html.pre({"style": {"whiteSpace": "pre-wrap", "color": "#334155"}}, transcript)
        ),

        # Translate button
        html.button(
            {
                "on_click": translate,
                "disabled": not transcript,
                "style": {
                    "padding": "10px 20px",
                    "borderRadius": "8px",
                    "border": "none",
                    "backgroundColor": "#6366f1" if transcript else "#cbd5e1",
                    "color": "white",
                    "fontSize": "1rem",
                    "cursor": "pointer" if transcript else "not-allowed",
                    "marginBottom": "16px"
                }
            },
            "🔄 Translate"
        ),

        # Translation card
        html.div(
            {
                "style": {
                    "width": "100%",
                    "maxWidth": "600px",
                    "backgroundColor": "white",
                    "borderRadius": "12px",
                    "padding": "16px",
                    "marginBottom": "16px",
                    "boxShadow": "0 2px 8px rgba(0,0,0,0.05)"
                }
            },
            html.h3({"style": {"marginBottom": "8px", "color": "#1e293b"}}, "Translation"),
            html.pre({"style": {"whiteSpace": "pre-wrap", "color": "#334155"}}, translation)
        ),

        # Play audio button
        html.button(
            {
                "on_click": play_audio,
                "disabled": not translation,
                "style": {
                    "padding": "10px 20px",
                    "borderRadius": "8px",
                    "border": "none",
                    "backgroundColor": "#10b981" if translation else "#cbd5e1",
                    "color": "white",
                    "fontSize": "1rem",
                    "cursor": "pointer" if translation else "not-allowed",
                    "marginBottom": "12px"
                }
            },
            "▶️ Play Translated Audio"
        ),

        # Audio player
        html.audio(
            {"src": audio_url, "controls": True, "style": {"width": "100%", "maxWidth": "600px"}}
        ) if audio_url else None
    )


if __name__ == "__main__":
    run(App)
