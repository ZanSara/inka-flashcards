
{
    "audio_player": lambda url, elem_id="audio": f"""
            <audio id='{elem_id}' src='{url}'></audio>
            <i onclick="document.getElementById('{elem_id}').play()" class="fas fa-volume-up" style='margin-left:1rem;'></i>
        """,
    "pt_audio": lambda word, elem_id="audio": f"""
            <audio id='{elem_id}' src='https://voice.reverso.net/RestPronunciation.svc/v1/output=json/GetVoiceStream/voiceName=Celia22k?inputText={b64encode(word)}'></audio>
            <i onclick="document.getElementById('{elem_id}').play()" class="fas fa-volume-up" style='margin-left:1rem;'></i>
        """,
}