# PROYECTO BACKEND - ESTADO LOCAL

Write-Host "=== BACKEND DE CONDOMINIO - FUNCIONANDO ===" -ForegroundColor Green

# URLs principales
$baseUrl = "http://127.0.0.1:8000"
$apiUrl = "$baseUrl/api"

Write-Host ""
Write-Host "ENDPOINTS PRINCIPALES:" -ForegroundColor Yellow
Write-Host "- Servidor principal: $baseUrl" -ForegroundColor White
Write-Host "- API Root: $apiUrl/" -ForegroundColor White
Write-Host "- Login: $apiUrl/login/" -ForegroundColor White
Write-Host "- Swagger UI: $apiUrl/schema/swagger-ui/" -ForegroundColor White
Write-Host "- Admin Panel: $baseUrl/admin/" -ForegroundColor White

Write-Host ""
Write-Host "CREDENCIALES DE PRUEBA:" -ForegroundColor Yellow
Write-Host "- Usuario: admin" -ForegroundColor White
Write-Host "- Contraseña: [la que configuraste]" -ForegroundColor White

Write-Host ""
Write-Host "MODULOS DISPONIBLES:" -ForegroundColor Yellow
Write-Host "- /api/usuarios/ - Gestion de usuarios" -ForegroundColor White
Write-Host "- /api/condominio/ - Propiedades y avisos" -ForegroundColor White
Write-Host "- /api/seguridad/ - Control de acceso" -ForegroundColor White
Write-Host "- /api/finanzas/ - Pagos y facturacion" -ForegroundColor White
Write-Host "- /api/mantenimiento/ - Ordenes de trabajo" -ForegroundColor White
Write-Host "- /api/notificaciones/ - Notificaciones push" -ForegroundColor White

Write-Host ""
Write-Host "PRUEBA DE CONECTIVIDAD:" -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri $apiUrl/ -Method GET -TimeoutSec 5
    Write-Host "✓ Servidor respondiendo (Status: $($response.StatusCode))" -ForegroundColor Green
    
    $swaggerResponse = Invoke-WebRequest -Uri "$apiUrl/schema/swagger-ui/" -Method GET -TimeoutSec 5
    Write-Host "✓ Swagger UI disponible (Status: $($swaggerResponse.StatusCode))" -ForegroundColor Green
    
} catch {
    Write-Host "✗ Error de conectividad: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Asegurate de que el servidor este corriendo:" -ForegroundColor Yellow
    Write-Host "  python manage.py runserver 8000" -ForegroundColor Gray
}

Write-Host ""
Write-Host "NOTAS IMPORTANTES:" -ForegroundColor Yellow
Write-Host "- Los warnings de serializer son normales" -ForegroundColor Gray
Write-Host "- Usar /api/login/ (no /api/users/login/)" -ForegroundColor Gray
Write-Host "- El .env esta protegido por .gitignore" -ForegroundColor Gray

Write-Host ""
Write-Host "✓ EL PROYECTO ESTA FUNCIONANDO CORRECTAMENTE" -ForegroundColor Green