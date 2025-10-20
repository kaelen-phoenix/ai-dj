$env:SPOTIFY_CLIENT_ID = "b568dcea222848aab3697ec6ca4195b7"
$env:SPOTIFY_CLIENT_SECRET = "c1abfc0990574c68a4f8e9d4846190c1"
& .\.venv\Scripts\Activate.ps1
cdk synth
