

import dash
from dash import html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

dash.register_page(__name__, path='/')

layout = dmc.MantineProvider(
    theme={
        # "components":{
        #     "Button":{
        #         "styles":{
        #             "color":"green"
        #         }
        #     }
        # }
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
                html.Br(),
                html.Br(),       
                html.Br(),
                html.Br(),
                dbc.Row(
                    children=[
                        dbc.Col(width=2),
                        dbc.Col(
                            className='align-center',
                            children=[
                                #html.H3('text'),
                                html.Br(),
                                html.Div(
                                    
                                    children=[
                                        dmc.Button(
                                            children=[
                                                dbc.NavLink('GENERATE FORM', href='/generate-form',style = {'color': 'white','font-weight':'bold'},className='navlink-parker'),#,className='nav-link'))
                                            ],
                                            size='xl',
                                            color='darkBlue'
                                            # color='green'
                                            # color='#FFCD00'
                                            # color= '#FFCD00'
                                            # classNames={'button':'dmc-button'}
                                        ),
                                    ],
                                    style={'textAlign':'center'},
                                    
                                )
                            
                            ],
                            width=4,
                            #justify="center"
                        ),
                        dbc.Col(
                            children=[
                                html.Br(),
                                html.Div(
                                    children=[
                                        dmc.Button(
                                            children=[
                                                dbc.NavLink('SUBMIT FORM', href='/submit-form',style = {'color': 'white','font-weight':'bold'},className='navlink-parker'),#,className='nav-link'))
                                            ],
                                            size='xl',
                                            color='darkBlue'
                                        ),
                                    ],
                                    style={'textAlign':'center'}
                                )

                            ],
                            width=4
                        ),
                        dbc.Col(width=2)
                    ]
                ),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                dbc.Row(
                    children=[
                        dbc.Col(width=4),
                        dbc.Col(
                            className='align-center',
                            children=[
                                #html.H3('text'),
                                html.Br(),
                                html.Div(
                                    
                                    # children=[
                                    #     dmc.Button(
                                    #         children=[
                                    #             dbc.NavLink('What is this tool?', href='/explain-tool',style = {'color': 'white','font-weight':'bold'},className='navlink-parker'),#,className='nav-link'))
                                    #         ],
                                    #         size='xl',
                                    #         color='darkBlue'
                                    #         # color='green'
                                    #         # color='#FFCD00'
                                    #         # color= '#FFCD00'
                                    #         # classNames={'button':'dmc-button'}
                                    #     ),
                                    # ],
                                    # style={'textAlign':'center'},
                                    
                                )
                            
                            ],
                            width=4,
                            #justify="center"
                        ),
                        dbc.Col(width=4)
                    ]
                )
            ],
        )
    ]
)