# Prueba de login con la API
Write-Host "=== PRUEBA DE LOGIN API ===" -ForegroundColor Green

# URL correcta del login
$loginUrl = "http://127.0.0.1:8000/api/login/"

# Datos de login
$loginData = @{
    username = "admin"
    password = "admin"  # o la contraseña que hayas configurado
} | ConvertTo-Json

Write-Host "URL: $loginUrl" -ForegroundColor Yellow
Write-Host "Datos: $loginData" -ForegroundColor Yellow

try {
    # Hacer petición POST
    $response = Invoke-RestMethod -Uri $loginUrl -Method POST -Body $loginData -ContentType "application/json"
    
    Write-Host "✅ LOGIN EXITOSO" -ForegroundColor Green
    Write-Host "Token recibido: $($response.token)" -ForegroundColor Cyan
    
    # Guardar token para uso posterior
    $token = $response.token
    Write-Host "Token guardado en variable `$token" -ForegroundColor Yellow
    
} catch {
    Write-Host "❌ ERROR EN LOGIN" -ForegroundColor Red
    Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    Write-Host "Detalle: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== PRUEBA DE ENDPOINT PROTEGIDO ===" -ForegroundColor Green

if ($token) {
    try {
        # Probar un endpoint que requiere autenticación
        $headers = @{
            "Authorization" = "Token $token"
        }
        
        $testUrl = "http://127.0.0.1:8000/api/usuarios/"
        $usersResponse = Invoke-RestMethod -Uri $testUrl -Method GET -Headers $headers
        
        Write-Host "✅ ACCESO A USUARIOS EXITOSO" -ForegroundColor Green
        Write-Host "Usuarios encontrados: $($usersResponse.count)" -ForegroundColor Cyan
        
    } catch {
        Write-Host "❌ ERROR EN ENDPOINT PROTEGIDO" -ForegroundColor Red
        Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

Write-Host "`n=== RESUMEN ===" -ForegroundColor Green
Write-Host "- Servidor corriendo en: http://127.0.0.1:8000/" -ForegroundColor White
Write-Host "- Login endpoint: /api/login/" -ForegroundColor White
Write-Host "- Swagger UI: http://127.0.0.1:8000/api/schema/swagger-ui/" -ForegroundColor White
Write-Host "- Schema JSON: http://127.0.0.1:8000/api/schema/" -ForegroundColor White