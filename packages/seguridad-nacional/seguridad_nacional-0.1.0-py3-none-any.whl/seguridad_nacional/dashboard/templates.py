"""Plantillas HTML del dashboard"""


def get_dashboard_html() -> str:
    """Obtener HTML del dashboard"""
    return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Seguridad Nacional - Dashboard</title>
    
    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #0f0f23;
            color: #e0e0e0;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        
        header h1 {
            color: white;
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .kpis {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .kpi-card {
            background: #1a1a2e;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .kpi-card h3 {
            font-size: 14px;
            color: #aaa;
            margin-bottom: 10px;
        }
        
        .kpi-card .value {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }
        
        .kpi-card.status-normal {
            border-left-color: #10b981;
        }
        
        .kpi-card.status-alert {
            border-left-color: #f59e0b;
        }
        
        .kpi-card.status-critical {
            border-left-color: #ef4444;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: #1a1a2e;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .card h2 {
            font-size: 20px;
            margin-bottom: 15px;
            color: #667eea;
        }
        
        #map {
            height: 400px;
            width: 100%;
            border-radius: 8px;
            position: relative;
            z-index: 1;
            overflow: hidden;
            background: #1a1a2e;
        }
        
        /* Evitar glitches visuales en el mapa */
        #map .leaflet-container {
            background: #1a1a2e;
            outline: none;
        }
        
        /* Mejorar rendimiento del mapa durante interacciones */
        #map .leaflet-tile-container {
            image-rendering: -webkit-optimize-contrast;
        }
        
        /* Prevenir selección de texto durante el drag */
        #map .leaflet-container {
            -webkit-user-select: none;
            -moz-user-select: none;
            user-select: none;
        }
        
        /* Mejorar rendimiento durante zoom */
        #map .leaflet-tile-pane {
            opacity: 1;
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .table th,
        .table td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #333;
        }
        
        .table th {
            background: #2a2a3e;
            color: #667eea;
        }
        
        .table tr:hover {
            background: #2a2a3e;
        }
        
        .recent-attacks {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .attack-item {
            padding: 10px;
            margin-bottom: 10px;
            background: #2a2a3e;
            border-radius: 5px;
            border-left: 4px solid #ef4444;
        }
        
        .attack-item.blocked {
            border-left-color: #10b981;
        }
        
        .attack-item .time {
            font-size: 12px;
            color: #aaa;
        }
        
        .attack-item .details {
            margin-top: 5px;
            font-size: 14px;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #aaa;
        }
        
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 20px;
        }
        
        .refresh-btn:hover {
            background: #5568d3;
        }
        
        .last-update {
            color: #aaa;
            font-size: 12px;
            margin-top: 10px;
            text-align: center;
        }
        
        .error-message {
            background: #ef4444;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔒 Seguridad Nacional - Dashboard</h1>
            <p>Monitoreo en tiempo real de ciberataques</p>
        </header>
        
        <div style="display: flex; gap: 10px; margin-bottom: 20px;">
            <button class="refresh-btn" onclick="loadDashboard()">🔄 Actualizar</button>
            <button class="refresh-btn" onclick="exportReport('csv')" style="background: #10b981;">📥 Exportar CSV</button>
            <button class="refresh-btn" onclick="exportReport('json')" style="background: #3b82f6;">📥 Exportar JSON</button>
        </div>
        <div class="last-update" id="lastUpdate">Última actualización: --</div>
        
        <div id="errorMessage" style="display: none;"></div>
        
        <div class="kpis" id="kpis">
            <div class="loading">Cargando estadísticas...</div>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <h2>📍 Mapa Mundial de Ataques</h2>
                <div id="map"></div>
            </div>
            
            <div class="card">
                <h2>⚠️ Tipos de Ataques</h2>
                <canvas id="attackTypesChart"></canvas>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <h2>🎯 Endpoints Más Vulnerables</h2>
                <table class="table" id="endpointsTable">
                    <thead>
                        <tr>
                            <th>Endpoint</th>
                            <th>Ataques</th>
                            <th>Último Ataque</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td colspan="3" class="loading">Cargando...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="card">
                <h2>🔴 Actividad en Tiempo Real</h2>
                <div class="recent-attacks" id="recentAttacks">
                    <div class="loading">Cargando ataques recientes...</div>
                </div>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <h2>📈 Tendencias de Ataques (Últimas 24h)</h2>
                <canvas id="trendsChart"></canvas>
            </div>
            
            <div class="card">
                <h2>🚫 IPs Bloqueadas</h2>
                <div id="blockedIPs">
                    <div class="loading">Cargando IPs bloqueadas...</div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Leaflet JS -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    
    <script>
        const DASHBOARD_PATH = '/seguridad';
        let map;
        let attackTypesChart;
        let trendsChart;
        
        // Variables para controlar las actualizaciones del mapa
        let currentMarkers = [];
        let isMapInteracting = false;  // Flag para saber si el usuario está interactuando con el mapa
        let pendingMapUpdate = null;   // Datos pendientes de actualización
        let mapUpdateTimeout = null;   // Timeout para actualizar el mapa después de la interacción
        
        // Función para aplicar actualización pendiente del mapa
        function applyPendingMapUpdate() {
            if (pendingMapUpdate !== null && !isMapInteracting) {
                updateMap(pendingMapUpdate);
                pendingMapUpdate = null;
            }
        }
        
        // Inicializar mapa
        function initMap() {
            map = L.map('map', {
                zoomControl: true,
                doubleClickZoom: true,
                boxZoom: true,
                keyboard: true,
                scrollWheelZoom: true,
                tap: true,
                touchZoom: true,
                dragging: true
            }).setView([13.7942, -88.8965], 6);  // Centrar en El Salvador
            
            // Agregar capa de tiles con opciones para mejorar rendimiento
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19,
                minZoom: 2,
                updateWhenZooming: false,  // No actualizar tiles durante el zoom
                updateWhenIdle: true,      // Actualizar tiles cuando está inactivo
                keepBuffer: 2              // Mantener buffer de tiles
            }).addTo(map);
            
            // Detectar cuando el usuario comienza a interactuar con el mapa
            map.on('zoomstart', function() {
                isMapInteracting = true;
                if (mapUpdateTimeout) {
                    clearTimeout(mapUpdateTimeout);
                    mapUpdateTimeout = null;
                }
            });
            
            map.on('movestart', function() {
                isMapInteracting = true;
                if (mapUpdateTimeout) {
                    clearTimeout(mapUpdateTimeout);
                    mapUpdateTimeout = null;
                }
            });
            
            map.on('dragstart', function() {
                isMapInteracting = true;
                if (mapUpdateTimeout) {
                    clearTimeout(mapUpdateTimeout);
                    mapUpdateTimeout = null;
                }
            });
            
            // Detectar cuando el usuario termina de interactuar con el mapa
            map.on('zoomend', function() {
                isMapInteracting = false;
                // Esperar un poco antes de aplicar actualización pendiente
                if (mapUpdateTimeout) {
                    clearTimeout(mapUpdateTimeout);
                }
                mapUpdateTimeout = setTimeout(function() {
                    applyPendingMapUpdate();
                }, 800);  // Esperar 800ms después de terminar el zoom
            });
            
            map.on('moveend', function() {
                isMapInteracting = false;
                // Esperar un poco antes de aplicar actualización pendiente
                if (mapUpdateTimeout) {
                    clearTimeout(mapUpdateTimeout);
                }
                mapUpdateTimeout = setTimeout(function() {
                    applyPendingMapUpdate();
                }, 800);  // Esperar 800ms después de terminar el movimiento
            });
            
            map.on('dragend', function() {
                isMapInteracting = false;
                // Esperar un poco antes de aplicar actualización pendiente
                if (mapUpdateTimeout) {
                    clearTimeout(mapUpdateTimeout);
                }
                mapUpdateTimeout = setTimeout(function() {
                    applyPendingMapUpdate();
                }, 800);  // Esperar 800ms después de terminar el drag
            });
        }
        
        // Cargar datos del dashboard
        async function loadDashboard() {
            try {
                // Crear URL con credenciales (el navegador las maneja automáticamente)
                // O usar fetch con credentials
                const username = 'admin';
                const password = 'admin123';
                const credentials = btoa(username + ':' + password);
                
                const response = await fetch(`${DASHBOARD_PATH}/api/dashboard`, {
                    method: 'GET',
                    headers: {
                        'Authorization': 'Basic ' + credentials,
                        'Content-Type': 'application/json'
                    },
                    credentials: 'same-origin'
                });
                
                if (!response.ok) {
                    if (response.status === 401) {
                        console.error('Error de autenticacion (401)');
                        console.error('Verifica las credenciales: admin/admin123');
                        // Mostrar error
                        const errorMsg = document.getElementById('errorMessage');
                        if (errorMsg) {
                            errorMsg.innerHTML = 'Error de autenticacion. Verifica las credenciales.';
                            errorMsg.style.display = 'block';
                        }
                    } else {
                        console.error('Error en respuesta:', response.status, response.statusText);
                    }
                    return;
                }
                
                const data = await response.json();
                
                if (!data) {
                    console.error('No se recibieron datos del dashboard');
                    return;
                }
                
                console.log('Datos recibidos:', data);
                
                // Actualizar componentes del dashboard
                if (data.general) {
                    updateKPIs(data.general);
                }
                if (data.top_countries) {
                    updateMap(data.top_countries);
                }
                if (data.top_attack_types) {
                    updateAttackTypes(data.top_attack_types);
                }
                if (data.top_endpoints) {
                    updateEndpoints(data.top_endpoints);
                }
                if (data.recent_attacks) {
                    updateRecentAttacks(data.recent_attacks);
                }
                if (data.blocked_ips) {
                    updateBlockedIPs(data.blocked_ips);
                }
                if (data.trends) {
                    updateTrends(data.trends);
                }
                
                // Mostrar última actualización
                const now = new Date();
                const lastUpdateEl = document.getElementById('lastUpdate');
                if (lastUpdateEl) {
                    lastUpdateEl.textContent = 'Ultima actualizacion: ' + now.toLocaleTimeString() + ' (Total: ' + (data.general ? data.general.total_attacks : 0) + ' ataques)';
                }
                console.log('Dashboard actualizado a las:', now.toLocaleTimeString(), '- Total de ataques:', data.general ? data.general.total_attacks : 0);
                
                // Ocultar mensaje de error si existe
                const errorMsg = document.getElementById('errorMessage');
                if (errorMsg) {
                    errorMsg.style.display = 'none';
                }
                
            } catch (error) {
                console.error('Error cargando dashboard:', error);
                console.error('Stack trace:', error.stack);
                
                // Mostrar error en el dashboard
                const errorMsg = document.getElementById('errorMessage');
                if (errorMsg) {
                    errorMsg.innerHTML = 'Error cargando datos: ' + error.message + '<br>Verifica la consola del navegador (F12) para mas detalles.';
                    errorMsg.style.display = 'block';
                }
                
                const kpis = document.getElementById('kpis');
                if (kpis && kpis.innerHTML.includes('Cargando')) {
                    kpis.innerHTML = '<div class="loading" style="color: #ef4444;">Error cargando datos. Verifica la consola del navegador (F12).</div>';
                }
            }
        }
        
        // Actualizar KPIs
        function updateKPIs(stats) {
            const statusClass = `status-${stats.status || 'normal'}`;
            const statusEmoji = {
                'normal': '🟢',
                'alert': '🟡',
                'critical': '🔴'
            }[stats.status || 'normal'] || '🟢';
            
            document.getElementById('kpis').innerHTML = `
                <div class="kpi-card ${statusClass}">
                    <h3>Estado del Sistema</h3>
                    <div class="value">${statusEmoji} ${stats.status || 'Normal'}</div>
                </div>
                <div class="kpi-card">
                    <h3>Ataques Hoy</h3>
                    <div class="value">${stats.attacks_today || 0}</div>
                </div>
                <div class="kpi-card">
                    <h3>Ataques (24h)</h3>
                    <div class="value">${stats.attacks_24h || 0}</div>
                </div>
                <div class="kpi-card">
                    <h3>Total de Ataques</h3>
                    <div class="value">${stats.total_attacks || 0}</div>
                </div>
                <div class="kpi-card">
                    <h3>Bloqueados</h3>
                    <div class="value">${stats.blocked_attacks || 0}</div>
                </div>
                <div class="kpi-card">
                    <h3>Tasa de Bloqueo</h3>
                    <div class="value">${stats.block_rate || 0}%</div>
                </div>
                <div class="kpi-card">
                    <h3>Endpoints Protegidos</h3>
                    <div class="value">${stats.endpoints_protected || 0}</div>
                </div>
            `;
        }
        
        // Actualizar mapa
        function updateMap(countries) {
            // Si el usuario está interactuando con el mapa, guardar los datos para actualizar después
            if (isMapInteracting) {
                pendingMapUpdate = countries;
                // No hacer log para evitar spam en la consola
                return;
            }
            
            // Si no hay países y no hay marcadores, no hacer nada
            if (!countries || countries.length === 0) {
                // Si hay marcadores actuales, limpiarlos
                if (currentMarkers.length > 0) {
                    currentMarkers.forEach(marker => map.removeLayer(marker));
                    currentMarkers = [];
                }
                return;
            }
            
            // Verificar si los países han cambiado (comparar solo los datos, no los marcadores)
            const countriesStr = JSON.stringify(countries.map(c => `${c.country || 'Unknown'}:${c.count || 0}`).sort());
            const lastCountriesStr = currentMarkers.length > 0 
                ? JSON.stringify(currentMarkers.map(m => {
                    if (m._popup && m._popup._content) {
                        // Extraer país y count del popup
                        const content = m._popup._content;
                        const match = content.match(/<strong>(.*?)<\/strong>.*?Ataques: (\d+)/);
                        if (match) {
                            return `${match[1]}:${match[2]}`;
                        }
                    }
                    return '';
                }).filter(s => s).sort())
                : '';
            
            // Si no hay cambios, no actualizar (evitar bucle infinito)
            if (countriesStr === lastCountriesStr && currentMarkers.length === countries.length) {
                return;  // No hacer log para evitar spam
            }
            
            // Limpiar marcadores anteriores
            currentMarkers.forEach(marker => map.removeLayer(marker));
            currentMarkers = [];
            
            // Coordenadas aproximadas por país
            const countryCoords = {
                // Localhost
                'Local': [13.7942, -88.8965],  // El Salvador
                'El Salvador': [13.7942, -88.8965],
                // Países más comunes
                'United States': [39.5, -98.35], 'USA': [39.5, -98.35], 'US': [39.5, -98.35],
                'China': [35.86, 104.19],
                'Russia': [61.52, 105.32], 'Russian Federation': [61.52, 105.32],
                // LATAM
                'Mexico': [23.63, -102.55], 'Brazil': [-14.24, -51.93], 'Argentina': [-38.42, -63.62],
                'Colombia': [4.57, -74.30], 'Chile': [-35.68, -71.54], 'Peru': [-9.19, -75.02],
                'Venezuela': [6.42, -66.59], 'Ecuador': [-1.83, -78.18], 'Guatemala': [15.78, -90.23],
                'Honduras': [15.20, -86.24], 'Nicaragua': [12.27, -85.21], 'Costa Rica': [9.75, -83.75],
                'Panama': [8.54, -80.78], 'Dominican Republic': [18.74, -70.16], 'Cuba': [21.52, -77.78],
                // Europa
                'United Kingdom': [55.38, -3.44], 'UK': [55.38, -3.44],
                'France': [46.23, 2.21], 'Germany': [51.17, 10.45], 'Italy': [41.87, 12.57],
                'Spain': [40.46, -3.75], 'Netherlands': [52.13, 5.29], 'Belgium': [50.50, 4.47],
                'Poland': [51.92, 19.15], 'Portugal': [39.40, -8.22], 'Sweden': [60.13, 18.64],
                'Norway': [60.47, 8.47], 'Denmark': [56.26, 9.50], 'Finland': [61.92, 25.75],
                // Asia
                'Japan': [36.20, 138.25], 'South Korea': [35.91, 127.77], 'India': [20.59, 78.96],
                'Indonesia': [-0.79, 113.92], 'Thailand': [15.87, 100.99], 'Vietnam': [14.06, 108.28],
                'Philippines': [12.88, 121.77], 'Malaysia': [4.21, 101.98], 'Singapore': [1.35, 103.82],
                // Otros
                'Australia': [-25.27, 133.78], 'New Zealand': [-40.90, 174.89],
                'South Africa': [-30.56, 22.94], 'Egypt': [26.82, 30.80], 'Nigeria': [9.08, 8.68],
                'Turkey': [38.96, 35.24], 'Saudi Arabia': [23.89, 45.08], 'Israel': [31.05, 34.85],
                'Pakistan': [30.38, 69.35], 'Bangladesh': [23.68, 90.36], 'Ukraine': [48.38, 31.17],
            };
            
            countries.forEach(country => {
                if (!country || !country.country) {
                    return;
                }
                
                // Buscar coordenadas (probar diferentes nombres)
                let coords = countryCoords[country.country] || 
                           countryCoords[country.country_code] ||
                           null;
                
                // Si no se encuentra, usar coordenadas por defecto
                if (!coords) {
                    // Para países desconocidos, usar coordenadas aproximadas
                    coords = [20.0, -89.0];  // Centro de América
                }
                
                // Crear marcador simple (sin icono personalizado para evitar problemas de carga)
                const marker = L.marker(coords, {
                    title: `${country.country || 'Unknown'}: ${country.count || 0} ataques`
                }).addTo(map);
                
                // Popup con información del país
                const popupContent = `
                    <div style="text-align: center;">
                        <strong>${country.country || 'Unknown'}</strong><br>
                        <span style="color: #ef4444; font-weight: bold;">${country.count || 0} ataques</span>
                    </div>
                `;
                marker.bindPopup(popupContent, {
                    closeOnClick: true,
                    autoClose: true,
                    autoPan: false  // No mover el mapa cuando se abre el popup
                });
                
                // Agregar a la lista de marcadores actuales
                currentMarkers.push(marker);
            });
            
            // NO ajustar la vista del mapa automáticamente
            // Esto evita el glitch cuando el usuario está haciendo zoom o moviendo el mapa
            // El mapa mantiene la vista que el usuario ha establecido
        }
        
        // Actualizar gráfico de tipos de ataques
        function updateAttackTypes(attackTypes) {
            const ctx = document.getElementById('attackTypesChart').getContext('2d');
            
            if (attackTypesChart) {
                attackTypesChart.destroy();
            }
            
            attackTypesChart = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: attackTypes.map(a => a.type),
                    datasets: [{
                        data: attackTypes.map(a => a.count),
                        backgroundColor: [
                            '#667eea',
                            '#764ba2',
                            '#f093fb',
                            '#4facfe',
                            '#00f2fe'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#e0e0e0'
                            }
                        }
                    }
                }
            });
        }
        
        // Actualizar tabla de endpoints
        function updateEndpoints(endpoints) {
            const tbody = document.querySelector('#endpointsTable tbody');
            if (endpoints.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3">No hay endpoints vulnerables</td></tr>';
                return;
            }
            
            tbody.innerHTML = endpoints.map(endpoint => `
                <tr>
                    <td>${endpoint.endpoint}</td>
                    <td>${endpoint.attack_count}</td>
                    <td>${endpoint.last_attack || 'N/A'}</td>
                </tr>
            `).join('');
        }
        
        // Actualizar ataques recientes
        function updateRecentAttacks(attacks) {
            const container = document.getElementById('recentAttacks');
            if (attacks.length === 0) {
                container.innerHTML = '<div class="loading">No hay ataques recientes</div>';
                return;
            }
            
            container.innerHTML = attacks.map(attack => `
                <div class="attack-item ${attack.blocked ? 'blocked' : ''}">
                    <div class="time">${attack.timestamp}</div>
                    <div class="details">
                        <strong>${attack.threat_type}</strong> desde ${attack.ip || 'Unknown'} (${attack.country || 'Unknown'})
                        <br>
                        Endpoint: ${attack.endpoint}
                        ${attack.blocked ? ' <span style="color: #10b981;">✓ Bloqueado</span>' : ''}
                    </div>
                </div>
            `).join('');
        }
        
        // Actualizar IPs bloqueadas
        function updateBlockedIPs(blockedIPs) {
            const container = document.getElementById('blockedIPs');
            if (!container) {
                return;
            }
            
            if (!blockedIPs || blockedIPs.length === 0) {
                container.innerHTML = '<div class="loading">No hay IPs bloqueadas</div>';
                return;
            }
            
            container.innerHTML = blockedIPs.map(ip => `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #333;">
                    <div>
                        <strong>${ip.ip}</strong>
                        <br>
                        <small style="color: #888;">Bloqueado: ${ip.blocked_at || 'N/A'}</small>
                        <br>
                        <small style="color: #888;">Severidad: ${ip.severity || 'N/A'}</small>
                        <br>
                        <small style="color: #888;">Ataques: ${ip.attack_count || 0}</small>
                    </div>
                    <button onclick="unblockIP('${ip.ip}')" style="background: #10b981; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;">
                        Desbloquear
                    </button>
                </div>
            `).join('');
        }
        
        // Actualizar gráfico de tendencias
        function updateTrends(trends) {
            const ctx = document.getElementById('trendsChart');
            if (!ctx) {
                return;
            }
            
            if (!trends || trends.length === 0) {
                return;
            }
            
            if (trendsChart) {
                trendsChart.destroy();
            }
            
            const labels = trends.map(t => {
                const date = new Date(t.hour);
                return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
            });
            
            trendsChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Total Ataques',
                            data: trends.map(t => t.total),
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'Bloqueados',
                            data: trends.map(t => t.blocked),
                            borderColor: '#ef4444',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'Permitidos',
                            data: trends.map(t => t.allowed),
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#e0e0e0'
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                color: '#e0e0e0'
                            },
                            grid: {
                                color: '#333'
                            }
                        },
                        x: {
                            ticks: {
                                color: '#e0e0e0'
                            },
                            grid: {
                                color: '#333'
                            }
                        }
                    }
                }
            });
        }
        
        // Exportar reporte
        async function exportReport(format) {
            try {
                const username = 'admin';
                const password = 'admin123';
                const credentials = btoa(username + ':' + password);
                
                const response = await fetch(`${DASHBOARD_PATH}/api/export?format=${format}`, {
                    method: 'GET',
                    headers: {
                        'Authorization': 'Basic ' + credentials,
                    },
                });
                
                if (!response.ok) {
                    throw new Error('Error exportando reporte');
                }
                
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `reporte_ataques_${new Date().toISOString().split('T')[0]}.${format}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            } catch (error) {
                console.error('Error exportando reporte:', error);
                alert('Error exportando reporte: ' + error.message);
            }
        }
        
        // Desbloquear IP
        async function unblockIP(ip) {
            if (!confirm(`¿Estás seguro de que quieres desbloquear la IP ${ip}?`)) {
                return;
            }
            
            try {
                const username = 'admin';
                const password = 'admin123';
                const credentials = btoa(username + ':' + password);
                
                const response = await fetch(`${DASHBOARD_PATH}/api/unblock/${ip}`, {
                    method: 'POST',
                    headers: {
                        'Authorization': 'Basic ' + credentials,
                        'Content-Type': 'application/json'
                    },
                });
                
                if (!response.ok) {
                    throw new Error('Error desbloqueando IP');
                }
                
                const data = await response.json();
                alert(data.message || 'IP desbloqueada correctamente');
                loadDashboard(); // Recargar dashboard
            } catch (error) {
                console.error('Error desbloqueando IP:', error);
                alert('Error desbloqueando IP: ' + error.message);
            }
        }
        
        // Inicializar
        initMap();
        
        // Cargar dashboard inmediatamente
        loadDashboard();
        
        // Auto-refresh cada 5 segundos (menos frecuente para evitar conflictos con el mapa)
        // El mapa se actualiza solo si el usuario no está interactuando
        setInterval(function() {
            // No actualizar si el usuario está interactuando con el mapa
            if (!isMapInteracting) {
                loadDashboard();
            }
            // Si el usuario está interactuando, las actualizaciones se aplicarán después
        }, 5000);  // 5 segundos para reducir conflictos con el mapa
        
        // También refrescar cuando la ventana obtiene el foco (solo si no está interactuando)
        window.addEventListener('focus', function() {
            if (!isMapInteracting) {
                loadDashboard();
            }
        });
    </script>
</body>
</html>
    """


