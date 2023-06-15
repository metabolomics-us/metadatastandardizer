
from random import sample
import dash
from dash import dcc, html,dash_table,callback, ctx,MATCH,ALL
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc

import numpy as np
import pandas as pd
from xlsxwriter.utility import xl_rowcol_to_cell
import json
import base64
import io
from pprint import pprint
import requests


NUM_STEPS_EXPLAINER=3


dash.register_page(__name__, path='/explain-tool')


layout = dmc.MantineProvider(
    theme={
        "colors":{
            "darkBlue":[
                "#617285",
                "#54677D",
                "#485D77",
                "#3C5471",
                "#304C6D",
                "#25456A",
                "#1A3E68",
                "#1E3857",
                "#203349",
                "#212E3E",
                "#202A35",
                "#1F262E",
                "#1D2228"
            ]
        }
    },
    children=[
        html.Div(
            children=[
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Div(
                    children=[
                        dbc.Row(
                            children=[
                                dbc.Col(width=1),
                                dbc.Col(
                                    children=[
                
                                        dmc.Stepper(
                                            id="stepper_explainer",
                                            active=0,
                                            color='darkBlue',
                                            breakpoint="sm",

                                            children=[
                                                dmc.StepperStep(
                                                    id='generate_step_1',
                                                    label="Overview",
                                                    description="What is it?",
                                                    children=[
                                                        html.Br(),
                                                        dbc.Row(
                                                            children=[
                                                                dbc.Col(width=4),
                                                                dbc.Col(
                                                                    html.Div(
                                                                        children=[

                                                                            html.H4('What is this tool?'),
                                                                            # html.H6('Automatic Curation Step'),
                                                                            html.H6('This tool allows users to create sample metadata sheets'),
                                                                            html.H6('These sheets are curated then sent back to the user. They are also stored in a database.'),
                                                                            html.H6('Curating submitted sheets makes programmatic meta analysis very easy.'),
                                                                            html.H6(''),
                                                                            


                                                                        ],
                                                                        # className="d-flex justify-content-center align-items-center"
                                                                        className="justify-content-center"
                                                                    ),
                                                                    width=6
                                                                ),
                                                                dbc.Col(width=2)
                                                            ]
                                                        )
                                                    ]
                                                ),
                                                dmc.StepperStep(
                                                    label="Generate",
                                                    description="Making a form",
                                                    children=[
                                                        html.Br(),
                                                        dbc.Row(
                                                            children=[
                                                                dbc.Col(width=4),
                                                                dbc.Col(
                                                                    html.Div(
                                                                        children=[

                                                                            html.H4('What is this tool?'),
                                                                            # html.H6('Automatic Curation Step'),
                                                                            html.H6('This tool allows users to create sample metadata sheets'),
                                                                            html.H6('These sheets are curated then sent back to the user. They are also stored in a database.'),
                                                                            html.H6('Curating submitted sheets makes programmatic meta analysis very easy.'),
                                                                            html.H6(''),
                                                                            html.Img(src='assets/ingester_1.png')

                                                                        ],
                                                                        # className="d-flex justify-content-center align-items-center"
                                                                        className="justify-content-center"
                                                                    ),
                                                                    width=6
                                                                ),
                                                                dbc.Col(width=2)
                                                            ]
                                                        )
                                                    ]
                                                ),
                                                dmc.StepperStep(
                                                    label="Third step",
                                                    description="Download form",
                                                    children=[
                                                        

                                                        html.Br(),
                                                        html.Br(),
                                                        html.Br(),
                                                        dbc.Row(
                                                            children=[
                                                               


                                                          
                                                            ]
                                                        ),
                                                        html.Br(),
                                                        html.Br(),




                                                    ]
                                                ),
                                                # we never actually reac this step.
                                                dmc.StepperCompleted(
                                                    children=[
                                                        
                                                    ]
                                                ),
                                            ],
                                        ),
                                    ],
                                    width=10
                                ),
                                dbc.Col(width=1)
                            ]
                        ),   
                        dmc.Group(
                            position="center",
                            mt="xl",
                            children=[
                                dmc.Button("Prev. step", id="stepper_explainer_back",color='darkBlue',size='md'),
                                dmc.Button("Next step", id="stepper_explainer_next",color='darkBlue',size='md')
                            ],
                        ),
                    ]
                )
            ]
        )
    ]
)





@callback(
    [
        Output(component_id="stepper_explainer", component_property="active"),
    ],
    [
        Input(component_id='stepper_explainer_back', component_property="n_clicks"),
        Input(component_id='stepper_explainer_next', component_property="n_clicks")
    ],
    [
        State(component_id="stepper_explainer", component_property="active"),
    ],
    prevent_initial_call=True
)
def update(stepper_explainer_back_n_clicks, stepper_explainer_next_n_clicks, current):


    if ctx.triggered_id=="stepper_explainer_back" and current>0:
        current-=1
    elif ctx.triggered_id=="stepper_explainer_next" and current<(NUM_STEPS_EXPLAINER-1):
        current+=1        

    return [current]