# Generates the spoken meme lines into assets/sounds/meme/ using the default
# installed Windows TTS voice (System.Speech). Output: 16-bit PCM mono 44100 Hz WAV.
# Requires Windows with System.Speech (PowerShell 5 or 7). Installs nothing.

$ErrorActionPreference = 'Stop'

$outDir = Join-Path $PSScriptRoot 'meme'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

try {
    Add-Type -AssemblyName System.Speech
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
} catch {
    Write-Warning "System.Speech is unavailable: $($_.Exception.Message). No TTS files were written."
    exit 1
}

$format = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(
    44100,
    [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen,
    [System.Speech.AudioFormat.AudioChannel]::Mono)

$lines = [ordered]@{
    'jeff.wav'      = 'My name is Jeff.'
    'shut_up.wav'   = 'Everything should shut the fuck up. Everything should shut up.'
    'oh_no.wav'     = 'Oh no. Oh no no no no no.'
    'bruh.wav'      = 'Bruh.'
    'sheesh.wav'    = 'Sheeeesh.'
    'wow.wav'       = 'Wow. That is crazy.'
    'sixseven.wav'  = 'Six seven. Six seven. Six seven.'
    'skibidi.wav'   = 'Skibidi toilet.'
}

foreach ($name in $lines.Keys) {
    $path = Join-Path $outDir $name
    try {
        $synth.SetOutputToWaveFile($path, $format)
        $synth.Speak($lines[$name])
        $synth.SetOutputToNull()
        Write-Host "wrote $name"
    } catch {
        Write-Warning "failed $name : $($_.Exception.Message)"
        try { $synth.SetOutputToNull() } catch { }
    }
}

$synth.Dispose()
