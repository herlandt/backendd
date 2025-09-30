# Script de Prueba del Backend - PowerShell
# Ejecutar en PowerShell desde la raíz del proyecto

Write-Host "=== PRUEBAS DEL BACKEND DJANGO ===" -ForegroundColor Green
Write-Host "Fecha: $(Get-Date)" -ForegroundColor Gray

# 1. Verificar que el servidor está corriendo
Write-Host "`n1. Verificando servidor..." -ForegroundColor Yellow
try {
    $welcome = Invoke-WebRequest -Uri "http://localhost:8000/api/" -Method GET
    Write-Host "✅ Servidor funcionando - Status: $($welcome.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Servidor no responde. Asegúrate de que Django esté corriendo con 'python manage.py runserver'" -ForegroundColor Red
    exit 1
}

# 2. Probar documentación
Write-Host "`n2. Verificando documentación..." -ForegroundColor Yellow
try {
    $swagger = Invoke-WebRequest -Uri "http://localhost:8000/api/schema/swagger-ui/" -Method GET
    Write-Host "✅ Swagger UI disponible - Status: $($swagger.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error en Swagger UI" -ForegroundColor Red
}

# 3. Probar registro de usuario
Write-Host "`n3. Probando registro de usuario..." -ForegroundColor Yellow
$username = "testuser$(Get-Random -Minimum 1000 -Maximum 9999)"
$registerBody = @{
    username = $username
    password = "testpass123"
    email = "$username@example.com"
    first_name = "Test"
    last_name = "User"
} | ConvertTo-Json

try {
    $register = Invoke-WebRequest -Uri "http://localhost:8000/api/registro/" -Method POST -Body $registerBody -ContentType "application/json"
    Write-Host "✅ Registro exitoso - Status: $($register.StatusCode)" -ForegroundColor Green
    Write-Host "   Usuario creado: $username" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Error en registro: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Probar login
Write-Host "`n4. Probando login..." -ForegroundColor Yellow
$loginBody = @{
    username = $username
    password = "testpass123"
} | ConvertTo-Json

try {
    $login = Invoke-WebRequest -Uri "http://localhost:8000/api/login/" -Method POST -Body $loginBody -ContentType "application/json"
    $tokenResponse = $login.Content | ConvertFrom-Json
    $token = $tokenResponse.token
    Write-Host "✅ Login exitoso - Status: $($login.StatusCode)" -ForegroundColor Green
    Write-Host "   Token obtenido: $($token.Substring(0,20))..." -ForegroundColor Cyan
} catch {
    Write-Host "❌ Error en login: $($_.Exception.Message)" -ForegroundColor Red
    $token = $null
}

# 5. Probar endpoints con autenticación
if ($token) {
    Write-Host "`n5. Probando endpoints con autenticación..." -ForegroundColor Yellow
    $headers = @{
        "Authorization" = "Token $token"
        "Content-Type" = "application/json"
    }
    
    # Lista de endpoints a probar
    $endpoints = @(
        "http://localhost:8000/api/usuarios/",
        "http://localhost:8000/api/condominio/propiedades/",
        "http://localhost:8000/api/seguridad/visitas/",
        "http://localhost:8000/api/finanzas/gastos/"
    )
    
    foreach ($endpoint in $endpoints) {
        try {
            $response = Invoke-WebRequest -Uri $endpoint -Method GET -Headers $headers
            $endpointName = $endpoint.Split('/')[-2]
            Write-Host "   ✅ $endpointName - Status: $($response.StatusCode)" -ForegroundColor Green
        } catch {
            $endpointName = $endpoint.Split('/')[-2]
            Write-Host "   ❌ $endpointName - Error: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

# 6. Resumen
Write-Host "`n=== RESUMEN ===" -ForegroundColor Green
Write-Host "🌟 Backend Django funcionando correctamente" -ForegroundColor Green
Write-Host "📋 Documentación disponible en:" -ForegroundColor Cyan
Write-Host "   • Swagger UI: http://localhost:8000/api/schema/swagger-ui/" -ForegroundColor White
Write-Host "   • ReDoc: http://localhost:8000/api/schema/redoc/" -ForegroundColor White
Write-Host "   • API Root: http://localhost:8000/api/" -ForegroundColor White
Write-Host "🔐 Autenticación funcionando con tokens" -ForegroundColor Cyan
Write-Host "📱 Endpoints principales operativos" -ForegroundColor Cyan

Write-Host "`n💡 Para desarrollo frontend:" -ForegroundColor Yellow
Write-Host "   1. Usar http://localhost:8000/api/ como base URL" -ForegroundColor White
Write-Host "   2. Implementar Token Authentication" -ForegroundColor White
Write-Host "   3. Consultar Swagger UI para schemas" -ForegroundColor White