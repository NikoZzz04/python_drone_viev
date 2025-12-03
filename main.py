import panel as pn

pn.extension(sizing_mode="stretch_both")

app = pn.Column(
    pn.pane.Markdown("## 🚁 Cesium Drone Flight Demo"),
    pn.pane.HTML(
        '<iframe src="http://localhost:8000/dron.html" '
        'style="width:100%; height:100vh; border:none;"></iframe>',
        sizing_mode="stretch_width"
    ),
    sizing_mode="stretch_both",
)

app.servable()
