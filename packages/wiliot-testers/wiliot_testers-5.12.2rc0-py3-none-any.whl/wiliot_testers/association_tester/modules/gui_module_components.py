from dash import Dash, html, dcc, dash_table, ctx
import dash_bootstrap_components as dbc


def get_rescan_modal(is_r2r_printer: bool):
    return dbc.Modal(
    [
        dbc.ModalHeader("Rescan Window", close_button=False),
        dbc.ModalBody(
            html.Div([
                html.Div([
                    html.H5("Scanner", style={"textAlign": "center", "color": "black", "marginBottom": "10px"}),
                    dbc.Button("Rescan", id="rescan-btn", className="w-100", style={"height": "60px", "background-color": "#0dabb6", "border": "0px"}),
                    dbc.Button("Disconnect Scanner", id="connect-btn", className="w-100", style={"height": "60px", "marginTop": "10px", "background-color": "#0dabb6", "border": "0px"}),
                ], style={
                    "backgroundColor": "#f8f7f4",
                    "color": "white",
                    "width": "240px",
                    "height": "240px",
                    "padding": "12px",
                    "display": "flex",
                    "flexDirection": "column",
                    "justifyContent": "flex-start",
                    "borderRadius": "6px"
                }),
                html.Div([
                    html.H5(children="Printer" if is_r2r_printer else "", style={"textAlign": "center", "color": "black", "marginBottom": "10px"}),
                    dbc.Button("Reprint Last Label", id="reprint-btn", className="w-100", style={"height": "60px", "background-color": "#0dabb6", "border": "0px", "display": "block" if is_r2r_printer else "none"}),
                ], style={
                    "backgroundColor": "#f8f7f4",
                    "color": "white",
                    "width": "240px",
                    "height": "240px",
                    "padding": "12px",
                    "display": "flex",
                    "flexDirection": "column",
                    "justifyContent": "flex-start",
                    "borderRadius": "6px"
                }),
            ], style={"display": "flex", "flexDirection": "row", "justifyContent": "space-between", "gap": "20px"}),
        ),
        dbc.ModalFooter([
            dbc.Textarea(id="scan-results", rows=4, disabled=True, style={"backgroundColor": "#f8f7f4"}),
            html.Div([
                dbc.Button("Stop", id="stop-rescan-modal", style={"background-color": "#0dabb6", "border": "0px"}),
                dbc.Button("Continue", id="continue-rescan-modal", disabled=True, style={"background-color": "#0dabb6", "border": "0px"}),
            ], className="d-flex justify-content-between w-100 mt-2")
        ])
    ],
    id="rescan-modal",
    is_open=True,  # start closed
    backdrop=False,  # click outside to close
    keyboard=False,  # ESC to close
    centered=True)

def get_upload_modal():
    return dbc.Modal(
    [
        dbc.ModalHeader("Upload Window", close_button=False),
        dbc.ModalBody(
            html.Div([
                html.Label("Environment", style={"textAlign": "center", "color": "black", "marginBottom": "10px"}),
                dcc.Dropdown(id='env-dropdown-upload-modal',options=['prod', 'dev', 'test'],value='prod'),
                html.Label("Owner ID", style={"textAlign": "center", "color": "black", "marginBottom": "10px"}),
                dbc.Input(id="owner-id-upload-modal", type="text", value=''),
            ], style={
                "backgroundColor": "#f8f7f4",
                "color": "white",
                "height": "240px",
                "padding": "12px",
                "display": "flex",
                "flexDirection": "column",
                "justifyContent": "flex-start",
                "borderRadius": "6px"
            }),
        ),
        dbc.ModalFooter([
            dbc.Textarea(id="results-upload-modal", rows=4, disabled=True, style={"backgroundColor": "#f8f7f4"}),
            html.Div([
                dbc.Button("Dismiss", id="dismiss-btn-upload-modal", style={"background-color": "#0dabb6", "border": "0px"}),
                dbc.Button("Upload", id="upload-btn-upload-modal", style={"background-color": "#0dabb6", "border": "0px"}),
            ], className="d-flex justify-content-between w-100 mt-2")
        ])
    ],
    id="upload-modal",
    is_open=False,  # start closed
    backdrop=False,  # click outside to close
    keyboard=False,  # ESC to close
    centered=True)

if __name__ == "__main__":
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = html.Div([get_upload_modal()])
    app.layout.children[0].is_open = True
    app.run(debug=True)
