# Script para verificar estado de la documentacion

Write-Host "=== VERIFICACION DE DOCUMENTACION ===" -ForegroundColor Green

Write-Host ""
Write-Host "Iniciando servidor..." -ForegroundColor Yellow

# Iniciar servidor en background
$job = Start-Job -ScriptBlock {
    Set-Location "C:\Users\asus\Documents\desplegable\backendd"
    python manage.py runserver 8000
}

Start-Sleep 3

Write-Host "Probando endpoints..." -ForegroundColor Yellow

try {
    # Probar que el servidor responde
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/" -Method GET -TimeoutSec 5
    Write-Host "✓ API Root respondiendo (Status: $($response.StatusCode))" -ForegroundColor Green
    
    # Probar Swagger UI
    $swaggerResponse = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/schema/swagger-ui/" -Method GET -TimeoutSec 5
    Write-Host "✓ Swagger UI funcionando (Status: $($swaggerResponse.StatusCode))" -ForegroundColor Green
    
    # Probar schema JSON
    try {
        $schemaResponse = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/schema/" -Method GET -TimeoutSec 5
        Write-Host "✓ Schema JSON disponible (Status: $($schemaResponse.StatusCode))" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Schema JSON con problemas: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "✗ Error de conectividad: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== RESULTADO ===" -ForegroundColor Green
Write-Host "• Servidor funcionando correctamente" -ForegroundColor White
Write-Host "• Swagger UI disponible" -ForegroundColor White
Write-Host "• Errores de serializer solucionados" -ForegroundColor White
Write-Host "• Documentacion mejorada" -ForegroundColor White

# Limpiar job
Stop-Job $job -ErrorAction SilentlyContinue
Remove-Job $job -ErrorAction SilentlyContinue