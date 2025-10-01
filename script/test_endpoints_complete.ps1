# =========================================
# SCRIPT COMPLETO DE PRUEBAS DE ENDPOINTS
# =========================================

$baseUrl = "http://localhost:8080/api"

# Tokens de prueba proporcionados
$tokenResidente = "c337be3b9197718d9ecaced05cd67a9f0525b347"
$tokenAdmin = "589db8d96d1dfbd4eeac58d784ad7b3989a0bb21"

Write-Host "🚀 INICIANDO PRUEBAS COMPLETAS DE ENDPOINTS" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Yellow

# Función para hacer peticiones HTTP
function Test-Endpoint {
    param(
        [string]$Method = "GET",
        [string]$Url,
        [string]$Token = "",
        [string]$Description,
        [hashtable]$Body = @{}
    )
    
    try {
        $headers = @{
            "Content-Type" = "application/json"
        }
        
        if ($Token) {
            $headers["Authorization"] = "Token $Token"
        }
        
        $params = @{
            Uri = $Url
            Method = $Method
            Headers = $headers
            UseBasicParsing = $true
        }
        
        if ($Body.Count -gt 0 -and $Method -ne "GET") {
            $params.Body = ($Body | ConvertTo-Json)
        }
        
        $response = Invoke-WebRequest @params
        $statusColor = if ($response.StatusCode -lt 300) { "Green" } elseif ($response.StatusCode -lt 400) { "Yellow" } else { "Red" }
        Write-Host "✅ [$($response.StatusCode)] $Description" -ForegroundColor $statusColor
        
        return $response
    }
    catch {
        $statusCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode.value__ } else { "ERR" }
        $color = if ($statusCode -eq 401 -or $statusCode -eq 403) { "Yellow" } else { "Red" }
        Write-Host "⚠️  [$statusCode] $Description - $($_.Exception.Message)" -ForegroundColor $color
        
        return $null
    }
}

Write-Host "`n📋 1. ENDPOINTS PÚBLICOS (Sin autenticación)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor DarkCyan

Test-Endpoint -Url "$baseUrl/" -Description "Vista de bienvenida API"
Test-Endpoint -Url "$baseUrl/schema/swagger-ui/" -Description "Swagger UI"
Test-Endpoint -Url "$baseUrl/schema/redoc/" -Description "ReDoc"
Test-Endpoint -Url "$baseUrl/schema/" -Description "OpenAPI Schema"

Write-Host "`n🔐 2. AUTENTICACIÓN" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor DarkCyan

# Test login
$loginBody = @{
    username = "residente1"
    password = "isaelOrtiz2"
}
Test-Endpoint -Method "POST" -Url "$baseUrl/login/" -Body $loginBody -Description "Login residente1"

$adminLoginBody = @{
    username = "admin"
    password = "password"
}
Test-Endpoint -Method "POST" -Url "$baseUrl/login/" -Body $adminLoginBody -Description "Login admin"

Write-Host "`n👥 3. MÓDULO USUARIOS" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor DarkCyan

Test-Endpoint -Url "$baseUrl/usuarios/residentes/" -Token $tokenAdmin -Description "Lista residentes (Admin)"
Test-Endpoint -Url "$baseUrl/usuarios/perfil/" -Token $tokenResidente -Description "Perfil usuario (Residente)"
Test-Endpoint -Url "$baseUrl/usuarios/perfil/" -Token $tokenAdmin -Description "Perfil usuario (Admin)"

Write-Host "`n🏠 4. MÓDULO CONDOMINIO" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor DarkCyan

Test-Endpoint -Url "$baseUrl/condominio/propiedades/" -Token $tokenAdmin -Description "Lista propiedades (Admin)"
Test-Endpoint -Url "$baseUrl/condominio/propiedades/" -Token $tokenResidente -Description "Lista propiedades (Residente)"
Test-Endpoint -Url "$baseUrl/condominio/areas-comunes/" -Token $tokenResidente -Description "Áreas comunes"
Test-Endpoint -Url "$baseUrl/condominio/avisos/" -Token $tokenResidente -Description "Avisos del condominio"
Test-Endpoint -Url "$baseUrl/condominio/reglas/" -Token $tokenResidente -Description "Reglas del condominio"

Write-Host "`n💰 5. MÓDULO FINANZAS" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor DarkCyan

Test-Endpoint -Url "$baseUrl/finanzas/gastos/" -Token $tokenResidente -Description "Gastos/Expensas (Residente)"
Test-Endpoint -Url "$baseUrl/finanzas/gastos/" -Token $tokenAdmin -Description "Gastos/Expensas (Admin)"
Test-Endpoint -Url "$baseUrl/finanzas/multas/" -Token $tokenResidente -Description "Multas (Residente)"
Test-Endpoint -Url "$baseUrl/finanzas/pagos/" -Token $tokenResidente -Description "Pagos realizados"
Test-Endpoint -Url "$baseUrl/finanzas/reservas/" -Token $tokenResidente -Description "Reservas de áreas"
Test-Endpoint -Url "$baseUrl/finanzas/estado-cuenta/" -Token $tokenResidente -Description "Estado de cuenta"

# Endpoints administrativos
Test-Endpoint -Url "$baseUrl/finanzas/reportes/resumen/" -Token $tokenAdmin -Description "Reporte resumen (Admin)"
Test-Endpoint -Url "$baseUrl/finanzas/reportes/estado-morosidad/" -Token $tokenAdmin -Description "Estado morosidad (Admin)"

Write-Host "`n🛡️ 6. MÓDULO SEGURIDAD" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor DarkCyan

Test-Endpoint -Url "$baseUrl/seguridad/visitantes/" -Token $tokenResidente -Description "Lista visitantes"
Test-Endpoint -Url "$baseUrl/seguridad/vehiculos/" -Token $tokenResidente -Description "Lista vehículos"
Test-Endpoint -Url "$baseUrl/seguridad/visitas/" -Token $tokenResidente -Description "Lista visitas"
Test-Endpoint -Url "$baseUrl/seguridad/eventos/" -Token $tokenAdmin -Description "Eventos de seguridad"

# Endpoints de control de acceso
$placaTest = @{ placa = "ABC123" }
Test-Endpoint -Method "POST" -Url "$baseUrl/seguridad/control-acceso-vehicular/" -Token $tokenAdmin -Body $placaTest -Description "Control acceso vehicular"

# Dashboards
Test-Endpoint -Url "$baseUrl/seguridad/dashboard/resumen/" -Token $tokenAdmin -Description "Dashboard resumen"
Test-Endpoint -Url "$baseUrl/seguridad/visitas-abiertas/" -Token $tokenAdmin -Description "Visitas abiertas"

Write-Host "`n🔧 7. MÓDULO MANTENIMIENTO" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor DarkCyan

Test-Endpoint -Url "$baseUrl/mantenimiento/personal/" -Token $tokenAdmin -Description "Personal de mantenimiento"
Test-Endpoint -Url "$baseUrl/mantenimiento/solicitudes/" -Token $tokenResidente -Description "Solicitudes (Residente)"
Test-Endpoint -Url "$baseUrl/mantenimiento/solicitudes/" -Token $tokenAdmin -Description "Solicitudes (Admin)"

Write-Host "`n📱 8. MÓDULO NOTIFICACIONES" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor DarkCyan

$tokenBody = @{
    token = "test_fcm_token_12345"
    platform = "android"
}
Test-Endpoint -Method "POST" -Url "$baseUrl/notificaciones/token/" -Token $tokenResidente -Body $tokenBody -Description "Registrar token FCM"

$deviceBody = @{
    token_dispositivo = "test_device_token_67890"
    plataforma = "ios"
}
Test-Endpoint -Method "POST" -Url "$baseUrl/notificaciones/registrar-dispositivo/" -Token $tokenResidente -Body $deviceBody -Description "Registrar dispositivo"

Write-Host "`n🧪 9. CREAR DATOS DE PRUEBA" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor DarkCyan

# Crear visitante de prueba
$visitanteBody = @{
    nombre_completo = "Juan Pérez Test"
    documento = "12345678"
    telefono = "555-0123"
    email = "juan.test@example.com"
}
Test-Endpoint -Method "POST" -Url "$baseUrl/seguridad/visitantes/" -Token $tokenResidente -Body $visitanteBody -Description "Crear visitante de prueba"

# Crear solicitud de mantenimiento
$solicitudBody = @{
    titulo = "Reparación prueba"
    descripcion = "Solicitud de prueba del sistema"
    prioridad = "MEDIA"
}
Test-Endpoint -Method "POST" -Url "$baseUrl/mantenimiento/solicitudes/" -Token $tokenResidente -Body $solicitudBody -Description "Crear solicitud mantenimiento"

Write-Host "`n📊 10. PRUEBAS DE FILTROS" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor DarkCyan

Test-Endpoint -Url "$baseUrl/finanzas/gastos/?pagado=false" -Token $tokenResidente -Description "Gastos no pagados"
Test-Endpoint -Url "$baseUrl/seguridad/visitas/?estado=PROGRAMADA" -Token $tokenResidente -Description "Visitas programadas"
Test-Endpoint -Url "$baseUrl/mantenimiento/solicitudes/?prioridad=ALTA" -Token $tokenAdmin -Description "Solicitudes alta prioridad"

Write-Host "`n🎯 RESUMEN FINAL" -ForegroundColor Green
Write-Host "================" -ForegroundColor Yellow
Write-Host "✅ Pruebas completadas. Revise los resultados arriba." -ForegroundColor Green
Write-Host "⚠️  Los códigos 401/403 son normales (requieren autenticación específica)" -ForegroundColor Yellow
Write-Host "🚨 Los códigos 500+ indican errores del servidor que necesitan corrección" -ForegroundColor Red
Write-Host "`n🔗 Documentación: $baseUrl/schema/swagger-ui/" -ForegroundColor Cyan