import os
import panel as pn

# 1. Inicjalizacja Panelu
pn.extension(sizing_mode="stretch_width")

# 2. Definicja TOKENU (upewnij się, że ustawiasz zmienną środowiskową)
# W terminalu: export CESIUM_ION_TOKEN="Twój_Token"
token = os.getenv("CESIUM_ION_TOKEN")
token_value = token if token else "" # Używamy pustego stringa, jeśli token nie jest ustawiony

# 3. HTML/CSS (Statyczna struktura z linkami do CesiumJS)
# Ważne: usuwamy cały blok <script> z sekcji <body>
cesium_static_html = f"""
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="utf-8">
    <title>Cesium Drone Follow</title>
    <style>
        html, body, #cesiumContainer {{
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
            overflow: hidden;
        }}
    </style>    
    <script src="https://cesium.com/downloads/cesiumjs/releases/1.114/Build/Cesium/Cesium.js"></script>
    <link href="https://cesium.com/downloads/cesiumjs/releases/1.114/Build/Cesium/Widgets/widgets.css" rel="stylesheet">
</head>
<body>
<div id="cesiumContainer"></div>
</body>
</html>
"""

# 4. JavaScript (Logika Drona i Kamery)
# Jest to Twój oryginalny kod JS, ale umieszczony w zmiennej Pythona.
# Wstrzykujemy zmienną token_value do tego ciągu JS.
cesium_js_logic = f"""
Cesium.Ion.defaultAccessToken = "{token_value}";

const viewer = new Cesium.Viewer("cesiumContainer", {{
    terrain: Cesium.Terrain.fromWorldTerrain(),
    timeline: false,
    animation: false,
    baseLayerPicker: false,
    geocoder: false,
    homeButton: false,
    navigationHelpButton: false,
    fullscreenButton: false
}});

// TRASA DRONA
const punktyTrasy = [
    {{ lon: 21.181285, lat: 51.407653, h: 120 }}, // Radom (początek)
    {{ lon: 21.0122,  lat: 52.2297,  h: 400 }}, // Warszawa
    {{ lon: 19.9449,  lat: 50.0647,  h: 700 }}, // Kraków
    {{ lon: 17.0385,  lat: 51.1079,  h: 900 }}, // Wrocław
    {{ lon: 18.6466,  lat: 54.3520,  h: 600 }}, // Gdańsk
    {{ lon: 21.181285, lat: 51.407653, h: 250 }} // Radom (koniec)
];

const totalSeconds = 360; // Zmniejszone, żeby animacja trwała 6 minut (360s)
const start = Cesium.JulianDate.now();
const stop  = Cesium.JulianDate.addSeconds(start, totalSeconds, new Cesium.JulianDate());

viewer.clock.startTime = start.clone();
viewer.clock.stopTime = stop.clone();
viewer.clock.currentTime = start.clone();
viewer.clock.clockRange = Cesium.ClockRange.LOOP_STOP;
viewer.clock.multiplier = 1;
viewer.clock.shouldAnimate = true;

// Sampled Position
const property = new Cesium.SampledPositionProperty();

punktyTrasy.forEach((p, i) => {{
    const time = Cesium.JulianDate.addSeconds(
        start,
        (i / (punktyTrasy.length - 1)) * totalSeconds,
        new Cesium.JulianDate()
    );
    const pos = Cesium.Cartesian3.fromDegrees(p.lon, p.lat, p.h);
    property.addSample(time, pos);
}});

property.setInterpolationOptions({{
    interpolationDegree: 2,
    interpolationAlgorithm: Cesium.HermitePolynomialApproximation
}});

// DRON
const dron = viewer.entities.add({{
    availability: new Cesium.TimeIntervalCollection([
        new Cesium.TimeInterval({{ start, stop }})
    ]),
    position: property,
    orientation: new Cesium.VelocityOrientationProperty(property),
    model: {{
        uri: "https://raw.githubusercontent.com/CesiumGS/cesium/main/Apps/SampleData/models/CesiumDrone/CesiumDrone.glb",
        minimumPixelSize: 80,
        maximumScale: 200
    }},
    path: {{
        width: 4,
        leadTime: 0,
        trailTime: totalSeconds,
        material: Cesium.Color.YELLOW
    }}
}});

viewer.trackedEntity = dron;
// CAMERA OFFSET — follow camera
const cameraOffset = new Cesium.HeadingPitchRange(
    0,// heading
    Cesium.Math.toRadians(-30),// pitch
    2000// range (oddalenie)
);

// CINEMATIC FOLLOW CAMERA
viewer.scene.preRender.addEventListener(function () {{
    const time = viewer.clock.currentTime;
    const pos = dron.position.getValue(time);

    if (pos) {{
        viewer.camera.lookAt(pos, cameraOffset);
    }}
}});
"""

# 5. Wyświetlenie w Panelu i bezpieczne uruchomienie JS
cesium_pane = pn.pane.HTML(
    cesium_static_html,
    sizing_mode="stretch_both",
    # Opcjonalnie: ustawienie minimalnej wysokości dla bezpieczeństwa
    min_height=700 
)

# Ta funkcja wstrzykuje JS (logikę animacji) dopiero PO załadowaniu HTML/CSS/ZASOBÓW
cesium_pane.js_on_load(code=cesium_js_logic)

# Wyświetlenie w aplikacji
pn.Column(
    "# 🌍 Animacja Drona nad Polską (CesiumJS + Panel)",
    cesium_pane,
    sizing_mode="stretch_width"
).servable()