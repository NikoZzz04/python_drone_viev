import panel as pn

pn.extension()

cesium_html = """
<div id="cesiumContainer" style="width:100%; height:100%;"></div>
<link href="https://cesium.com/downloads/cesiumjs/releases/1.115/Build/Cesium/Widgets/widgets.css" rel="stylesheet">
<script src="https://cesium.com/downloads/cesiumjs/releases/1.115/Build/Cesium/Cesium.js"></script>
<script>
    Cesium.Ion.defaultAccessToken =
        "MY_TOKEN";

    const viewer = new Cesium.Viewer("cesiumContainer", {
        terrain: Cesium.Terrain.fromWorldTerrain(),
        timeline: false,
        animation: false,
        baseLayerPicker: false,
        geocoder: false,
        homeButton: false,
        navigationHelpButton: false,
        fullscreenButton: false
    });

    // TRASA DRONA
    const punktyTrasy = [
        { lon: 21.181285, lat: 51.407653, h: 120 },
        { lon: 21.0122,   lat: 52.2297,   h: 400 },
        { lon: 19.9449,   lat: 50.0647,   h: 700 },
        { lon: 17.0385,   lat: 51.1079,   h: 900 },
        { lon: 18.6466,   lat: 54.3520,   h: 600 },
        { lon: 21.181285, lat: 51.407653, h: 250 }
    ];

    const totalSeconds = 3600;
    const start = Cesium.JulianDate.now();
    const stop  = Cesium.JulianDate.addSeconds(start, totalSeconds, new Cesium.JulianDate());

    viewer.clock.startTime = start.clone();
    viewer.clock.stopTime = stop.clone();
    viewer.clock.currentTime = start.clone();
    viewer.clock.clockRange = Cesium.ClockRange.LOOP_STOP;
    viewer.clock.multiplier = 1;
    viewer.clock.shouldAnimate = true;

    // Sampled Position
    const property = new Cesium.SampledPositionProperty();

    punktyTrasy.forEach((p, i) => {
        const time = Cesium.JulianDate.addSeconds(
            start,
            (i / (punktyTrasy.length - 1)) * totalSeconds,
            new Cesium.JulianDate()
        );
        const pos = Cesium.Cartesian3.fromDegrees(p.lon, p.lat, p.h);
        property.addSample(time, pos);
    });

    property.setInterpolationOptions({
        interpolationDegree: 2,
        interpolationAlgorithm: Cesium.HermitePolynomialApproximation
    });

    // DRON
    const dron = viewer.entities.add({
        availability: new Cesium.TimeIntervalCollection([
            new Cesium.TimeInterval({ start, stop })
        ]),
        position: property,
        orientation: new Cesium.VelocityOrientationProperty(property),
        model: {
            uri: "https://raw.githubusercontent.com/CesiumGS/cesium/main/Apps/SampleData/models/CesiumDrone/CesiumDrone.glb",
            minimumPixelSize: 80,
            maximumScale: 200
        },
        path: {
            width: 4,
            leadTime: 0,
            trailTime: totalSeconds,
            material: Cesium.Color.YELLOW
        }
    });

    // CAMERA OFFSET — follow camera
    const cameraOffset = new Cesium.HeadingPitchRange(
        0,                            // heading
        Cesium.Math.toRadians(-30),   // pitch
        2000                          // range (oddalenie)
    );

    // CINEMATIC FOLLOW CAMERA
    viewer.scene.preRender.addEventListener(function () {
        const time = viewer.clock.currentTime;
        const pos = dron.position.getValue(time);

        if (pos) {
            viewer.camera.lookAt(pos, cameraOffset);
        }
    });

</script>
"""

pn.pane.HTML(cesium_html, height=600, sizing_mode='stretch_width').servable()