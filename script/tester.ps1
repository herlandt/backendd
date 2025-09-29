# scripts/tester.ps1
$ErrorActionPreference = "Stop"

# ==== PARAMS ====
$ENV:DJANGO_SETTINGS_MODULE = "config.settings"
$ENV:AWS_DEFAULT_REGION    = "us-east-1"
$ENV:AWS_REGION            = "us-east-1"
$ENV:INTERNAL_API_KEY      = "test-key"
$ENV:REKOG_COLLECTION      = "condominio-rostros"

# Ruta a un MP4 corto de prueba
$video = "C:\Users\asus\Videos\demo.mp4"

# ==== 1) Levantar MediaMTX (RTSP/HLS/WebRTC) ====
docker rm -f mediamtx 2>$null | Out-Null
docker run -d --name mediamtx `
  -p 8554:8554 -p 8888:8888 -p 8889:8889 `
  bluenviron/mediamtx:latest

Write-Host "Esperando MediaMTX 3s..."
Start-Sleep -Seconds 3

# ==== 2) Publicar el video a rtsp://127.0.0.1:8554/cam1 con FFmpeg ====
if (-Not (Test-Path $video)) {
  Write-Error "No existe el video en $video"
  exit 1
}

docker rm -f cam1 2>$null | Out-Null
docker run -d --name cam1 --add-host=host.docker.internal:host-gateway `
  -v "$video:/media/video.mp4" jrottenberg/ffmpeg:latest `
  -re -stream_loop -1 -i /media/video.mp4 `
  -c:v libx264 -preset veryfast -tune zerolatency -c:a aac `
  -rtsp_transport tcp -f rtsp rtsp://host.docker.internal:8554/cam1

Write-Host "Publicando a RTSP… Esperando 3s"
Start-Sleep -Seconds 3

# ==== 3) Preparar DB y seed mínimos ====
python manage.py migrate

# Crea colección de Rekognition y registra la cámara 'cam1' si no existe
$seed = @"
from seguridad.services.rekog import ensure_collection
from seguridad.models import Camera
ensure_collection()
Camera.objects.get_or_create(name="cam1", defaults={"rtsp_url":"rtsp://127.0.0.1:8554/cam1"})
print("Seed OK")
"@
python manage.py shell -c $seed

# ==== 4) Correr tests de TODO el proyecto ====
python manage.py test
$exitCode = $LASTEXITCODE

# ==== 5) (Opcional) monitoreo: correr detector 10s en modo demo ====
$demo = @"
from seguridad.models import Camera
from seguridad.services.detector import run_detector
cam = Camera.objects.get(name="cam1")
print("Iniciando detector 10s…")
run_detector(cam, fps=1, min_similarity=90.0, store_frames=False, run_seconds=10)
print("Detector finalizado")
"@
python manage.py shell -c $demo

exit $exitCode
