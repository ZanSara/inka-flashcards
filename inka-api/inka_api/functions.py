import base64


FUNCTIONS = {
    "b64encode": lambda string: base64.b64encode(string.encode()).decode(),
    "b64decode": lambda string: base64.b64decode(string).decode(),
    "audio_player": lambda url, elem_id="audio": f"""
        <audio id='{elem_id}' src='{url}'></audio>
        <i onclick="document.getElementById('{elem_id}').play()" class="fas fa-volume-up" style='margin-left:1rem;'></i>
    """,
    "pt_audio": lambda word, elem_id="pt_audio": f"""
        <audio id='{elem_id}' src='https://voice.reverso.net/RestPronunciation.svc/v1/output=json/GetVoiceStream/voiceName=Celia22k?inputText={base64.b64encode(word.encode()).decode()}'></audio>
        <i onclick="document.getElementById('{elem_id}').play()" class="fas fa-volume-up" style='margin-left:1rem;'></i>
    """,
}