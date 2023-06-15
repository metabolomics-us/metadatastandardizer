from turtle import down
from dataclasses import replace
from dash import dcc, html,dash_table,callback, ctx,MATCH,ALL,Patch
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash


import numpy as np
import pandas as pd
from xlsxwriter.utility import xl_rowcol_to_cell
import json
import base64
import io
from pprint import pprint
import requests

from . import samplemetadatauploadchecker


dash.register_page(__name__, path='/submit-form')

# BASE_URL_API = "http://127.0.0.1:4999/"
BASE_URL_API = "http://api_alias:4999/"

with open('assets/form_header_dict_basics.json','r') as f:
    FORM_HEADER_DICT=json.load(f)
with open('assets/extra_columns.json','r') as f:
    EXTRA_COLUMNS=json.load(f)

NUM_STEPS_SUBMIT=5
SPLIT_CHAR='~'
NEIGHBORS_TO_RETRIEVE=100
HEADERS_WITH_SHORT_NGRAMS={'heightUnit','weightUnit','ageUnit','massUnit','volumeUnit','timeUnit','drugDoseUnit'}
HEADERS_TO_NOT_CURATE={'mass','volume','height','weight','age','drugDoseMagnitude','time','cellCount'}

with open('additional_files/subset_per_heading.json', 'r') as fp:
    subset_per_heading_json=json.load(fp)


def generate_all_columns(list_of_jsons_value_lists_are_potential_columns):

    total_valid_columns=set()
    for temp_json in list_of_jsons_value_lists_are_potential_columns:
        for temp_key in temp_json:
            for temp_header in temp_json[temp_key]:
                total_valid_columns.add(temp_header)

    return total_valid_columns
ALL_METADATA_COLUMNS=generate_all_columns([FORM_HEADER_DICT,EXTRA_COLUMNS])


def parse_stored_excel_file(store_panda):
    '''
    extracts the {header:[written_string]} relationship
    '''
    temp_header_dict=dict()
    for temp_header in store_panda.columns:
        temp_header_dict[temp_header]=store_panda[temp_header].dropna().unique().tolist()
    #split inefficiently so that we can just comment out the next part if we desire

    output_dict=dict()
    for temp_key in temp_header_dict.keys():
        output_dict[temp_key.split('.')[0]]=list()


    for temp_key in temp_header_dict.keys():
        output_dict[temp_key.split('.')[0]] = output_dict[temp_key.split('.')[0]] + temp_header_dict[temp_key]
    
    return output_dict

def split_columns_if_delimited(temp_dataframe):
    #we always do this function, but only actually split if delimit character is prsent
    #for each column
    #split it
    #delete the orignal
    #append the new ones
    #much easier to conserve the order than to reorder
    #do in parallel with temp_dataframe_2
    new_dataframe_list=list()
    # print(temp_dataframe.dtypes)
    for temp_column in temp_dataframe.columns:
        if temp_dataframe[temp_column].dtype==object:
            # print(temp_dataframe[temp_column].str.split(SPLIT_CHAR,expand=True).add_prefix(temp_column+'.'))
            temp_expanded_columns=temp_dataframe[temp_column].astype(str).str.split(SPLIT_CHAR,expand=True).add_prefix(temp_column+'.')
        else:
            temp_expanded_columns=temp_dataframe[temp_column].astype(str)
        new_dataframe_list.append(temp_expanded_columns)

    output_dataframe=pd.concat(new_dataframe_list,axis='columns')
    output_dataframe.fillna(value=np.nan,inplace=True)

    return output_dataframe

def add_dot_zero_if_none(temp_dataframe):
    column_rename_dict={
        temp_col:temp_col+'.0' for temp_col in temp_dataframe if '.' not in temp_col
    }
    

    temp_dataframe.rename(
        column_rename_dict,
        inplace=True,
        axis='columns'
        
    )
    print('########################################################')
    print(column_rename_dict)
    print(temp_dataframe)


    return temp_dataframe


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
    # children=[dbc.Spinner(size="lg", color='#1A3E68', type="border", fullscreen=False,children=[
    children=[
        html.Div(
            children=[

                dcc.Store('store_furthest_active',data=0),
                dcc.Store('upload_store'),
                dcc.Store('author_store'),
                dcc.Store('store_2'),
                dcc.Store('store_3'),
                dcc.Store('store_4'),
                
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
                                            id="stepper_submit_form",
                                            active=0,
                                            color='darkBlue',
                                            breakpoint="sm",
                                            children=[
                                                
                                                dmc.StepperStep(
                                                    id='step_1',
                                                    label="First step",
                                                    description="Upload Form",
                                                    children=
                                                    [
                                                        dbc.Spinner(size="lg", color='#1A3E68', type="border", fullscreen=False,children=[
                                                        html.Br(),
                                                        html.Div(id='submit_step_1_error_div'),
                                                        dbc.Row(
                                                            children=[
                                                                dbc.Col(width=4),
                                                                dbc.Col(
                                                                    children=[
                                                                        dcc.Upload(
                                                                            id='upload_form',
                                                                            children=html.Div([
                                                                                'Upload Completed Form',
                                                                            ]),
                                                                            style={
                                                                                'width': '100%',
                                                                                'height': '60px',
                                                                                'lineHeight': '60px',
                                                                                'borderWidth': '1px',
                                                                                'borderStyle': 'dashed',
                                                                                'borderRadius': '5px',
                                                                                'textAlign': 'center',
                                                                                'margin': '10px'
                                                                            },
                                                                        ),
                                                                    ],
                                                                    width=4
                                                                ),
                                                                dbc.Col(width=4)
                                                            ]
                                                        ),   
                                                        ])                                             
                                                    ]
                                                ),
                                                dmc.StepperStep(
                                                    id='step_2',
                                                    label="Second step",
                                                    description="Validate Automatic Curation",
                                                    children=[
                                                        # dbc.Spinner(size="lg", color='#1A3E68', type="border", fullscreen=False,children=[
                                                        # html.H6('second step')
                                                        html.Div(id="submit_step_2_error_div",children=[]),
                                                        dmc.Checkbox(
                                                            id={
                                                                'type':'step_2_curation_checkbox',
                                                                'index':'temp'
                                                            },
                                                            # multi=False,
                                                            # #placeholder='Type compound name to search',
                                                            # options=['Type substring to populate options.'],
                                                            # optionHeight=60
                                                            checked=False,
                                                            style={'horizontal-align': 'center'}
                                                        ),
                                                        dmc.Checkbox(
                                                            id='step_2_curation_checkbox_all_correct',
                                                            checked=False,
                                                            style={'horizontal-align': 'center'}
                                                        ),
                                                    # ]) 
                                                    ]
                                                ),
                                                dmc.StepperStep(
                                                    id='step_3',
                                                    label="3 step",
                                                    description="Match to Substrings",
                                                    children=[
                                                        html.H6('3 step')
                                                        
                                                    ] 
                                                ),
                                                dmc.StepperStep(
                                                    id='step_4',
                                                    label="4 step",
                                                    description="Create New Terms",
                                                    children=[
                                                        html.Div(id="submit_step_4_error_div",children=[]),
                                                        
                                                    ] 
                                                ),
                                                dmc.StepperStep(
                                                    id='step_5',
                                                    label="5 step",
                                                    description="Download Curated Form",
                                                    children=[
                                                        dbc.Spinner(size="lg", color='#1A3E68', type="border", fullscreen=False,children=[
                                                            dcc.Download(id="download_curated_form"),
                                                            

                                                            html.Br(),
                                                            html.Br(),
                                                            html.Br(),
                                                            dbc.Row(
                                                                children=[
                                                                    dbc.Col(width=2),
                                                                    dbc.Col(
                                                                        children=[
                                                                            html.Div(
                                                                                children=[dmc.Group(
                                                                                    align='center',
                                                                                    children=[
                                                                                        html.Div(
                                                                                            # dmc.Button(
                                                                                            #     dbc.NavLink('Go home', href='/',style = {'color': 'white','font-weight':'bold'},className='navlink-parker'),#,className='nav-link')),
                                                                                            #     id='button_download_curated',color='darkBlue',size='md'
                                                                                            # ),
                                                                                            dmc.Button('Download Standardized Form', id='button_download_curated',color='darkBlue',size='md'),
                                                                                            className="d-grid gap-1 col-4 mx-auto",
                                                                                            style={'textAlign':'center'}
                                                                                        ),


                                                                                        html.Div(
                                                                                            dmc.Button(
                                                                                                dbc.NavLink('Return Home', href='/',style = {'color': 'white','font-weight':'bold'},className='navlink-parker'),#,className='nav-link')),
                                                                                                id='button_download_curated',color='darkBlue',size='md'
                                                                                            ),
                                                                                            className="d-grid gap-1 col-4 mx-auto",
                                                                                            style={'textAlign':'center'}
                                                                                        ),
                                                                                    ]
                                                                                )],
                                                                            style={'textAlign':'center'}
                                                                            )
                                                                        ],
                                                                        width=8
                                                                    ),


                                                                    dbc.Col(width=2)
                                                                ]
                                                            ),
                                                            html.Br(),
                                                            html.Br(),
                                                        ])
                                                    ]
                                                ),
















                                                        
                                                        
                                                        
                                                        
                                                #         html.Br(),
                                                #         html.Br(),
                                                #         dbc.Row(
                                                #             children=[
                                                #                 dbc.Col(width=4),
                                                #                 dbc.Col(
                                                #                     children=[
                                                #                         html.Div(
                                                #                             children=[
                                                #                                 html.H6('Download the standardized metadata form.'),
                                                #                                 #html.H6('Reupload '),
                                                #                                 html.Br(),
                                                #                             ],
                                                #                             #className="d-grid gap-4 col-6 mx-auto",
                                                #                             style={'textAlign':'center'}
                                                #                         ),
                                                #                     ],
                                                #                     width=4
                                                #                 ),
                                                #                 dbc.Col(width=4)
                                                #             ]
                                                #         ),
                                                #         dbc.Row(
                                                #             children=[
                                                #                 dbc.Col(width=4),
                                                #                 dbc.Col(
                                                #                     children=[
                                                #                         html.Div(
                                                #                             dmc.Button(
                                                #                                 # children=[dbc.Spinner(size="sm"), " Loading..."],
                                                #                                 children=['Download Form'],
                                                                                
                                                #                                 id='button_download_curated',color='darkBlue',size='md'
                                                #                             ),
                                                #                             className="d-grid gap-2 col-6 mx-auto",
                                                #                             style={'textAlign':'center'}
                                                #                         ),
                                                #                     ],
                                                #                     width=4
                                                #                 ),
                                                #                 dbc.Col(width=4)
                                                #             ]
                                                #         ),
                                                #         ])
                                                #     ] 
                                                # ),

                                                # we never reach this

                                                dmc.StepperCompleted(
                                                    # label='some_label',
                                                    # description='some description',
                                                    children=[
                                                        html.Br(),
                                                        dbc.Row(
                                                            children=[
                                                                dbc.Col(width=4),
                                                                dbc.Col(
                                                                    children=[
                                                                        html.Div(
                                                                            dmc.Button(
                                                                                dbc.NavLink('Go home', href='/',style = {'color': 'white','font-weight':'bold'},className='navlink-parker'),#,className='nav-link')),
                                                                                id='button_download_curated',color='darkBlue',size='md'
                                                                            ),
                                                                            className="d-grid gap-2 col-6 mx-auto",
                                                                            style={'textAlign':'center'}
                                                                        ),
                                                                    ],
                                                                    width=4
                                                                ),
                                                                dbc.Col(width=4)
                                                            ]
                                                        ),





                                                        # dbc.Row(
                                                        #     children=[
                                                        #         dbc.Col(width=5),
                                                        #         dbc.Col(
                                                        #             children=[
                                                        #                 html.Div(
                                                        #                     dbc.Button(
                                                        #                         dbc.NavLink('Go home', href='/',style = {'color': 'white','font-weight':'bold'},className='navlink-parker'),#,className='nav-link'))
                                                        #                     ),
                                                        #                     className="d-grid gap-2 col-6 mx-auto",
                                                        #                 ),
                                                        #             ],
                                                        #             width=2
                                                        #         ),
                                                        #         dbc.Col(width=5)
                                                        #     ]
                                                        # ),
                                                    ]
                                                ),
                                            ]
                                        )
                                    ]
                                ),
                                dbc.Col(width=1),
                            ]
                        ),
                        dmc.Group(
                            position="center",
                            mt="xl",
                            children=[
                                dmc.Button("Prev. step", id="stepper_submit_form_back",color='darkBlue',size='md'),# variant="default"),
                                dmc.Button("Next step", id="stepper_submit_form_next",color='darkBlue',size='md')
                            ],
                        ),
                    ]
                )
            ],
        )
    ]
    # )]
)

@callback(
    [
        Output(component_id="store_3", component_property="data", allow_duplicate=True),
    ],
    [
        Input(component_id={'type':'dropdown_empty_options','index':ALL}, component_property="value"),
    ],
    [
        State(component_id="store_3", component_property="data"),
    ],
    prevent_initial_call=True
)
def update_store_3_data(input_store_dropdown_empty_options_value_ALL,store_3_data):
    store_3_panda=pd.DataFrame.from_records(store_3_data)

    output_valid=list()
    output_main=list()
    for temp_string in input_store_dropdown_empty_options_value_ALL:
        try:
            output_valid.append(temp_string.split(' AKA ')[0])
            output_main.append(temp_string.split(' AKA ')[1])
            
        except AttributeError:
            output_valid.append(None)
            output_main.append(None)
        except IndexError:
            output_valid.append(temp_string)
            output_main.append(temp_string)


    store_3_panda['valid_string']=output_valid
    store_3_panda['main_string']=output_main

    return [store_3_panda.to_dict(orient='records')]



@callback(
    [
        Output(component_id="store_4", component_property="data", allow_duplicate=True),
    ],
    [
        Input(component_id={'type':'input_creation','index':ALL}, component_property="value"),
    ],
    [
        State(component_id="store_4", component_property="data"),
    ],
    prevent_initial_call=True
)
def update_store_4_data(input_creation_value_ALL,store_4_data):
    store_4_panda=pd.DataFrame.from_records(store_4_data)
    store_4_panda['valid_string']=input_creation_value_ALL
    store_4_panda['main_string']=input_creation_value_ALL

    return [store_4_panda.to_dict(orient='records')]

def generate_excel_for_download_from_stores(upload_panda,store_2_panda,store_3_panda,store_4_panda):
    total_replacement_panda=pd.concat(
        [store_4_panda,store_3_panda,store_2_panda],
        axis='index'
    )
    total_replacement_panda.drop_duplicates(
        subset=['header','written_string'],
        keep='first',
        inplace=True,
        ignore_index=True
    )

    replacement_dict=dict()
    for temp_tuple in total_replacement_panda.groupby('header'):
        replacement_dict[temp_tuple[0]]=dict()
        for index,series in temp_tuple[1].iterrows():
            replacement_dict[temp_tuple[0]][series['written_string']]=series['main_string']

  # print(replacement_dict)
  # print(upload_panda)


    for temp_col in upload_panda.columns:

        if temp_col.split('.')[0] in HEADERS_TO_NOT_CURATE:
            continue

        if temp_col.split('.')[0] not in replacement_dict.keys():
            continue

        upload_panda[temp_col].replace(
            to_replace=replacement_dict[temp_col.split('.')[0]],
            inplace=True
        )    
    return upload_panda,total_replacement_panda

def fill_author_sheet_curated(temp_writer,workbook,worksheet,temp_study_id,temp_author_id,provided_author_name):
    worksheet=temp_writer.sheets['author_metadata_curated']
    # worksheet.hide_gridlines()

    example_format_bold=workbook.add_format({
        'bold': 1,
        'align': 'center',
        'valign': 'vcenter',
        'font_size':11
    })
    example_format_text=workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'font_size':11
    })

    worksheet.write('A1','Requested Information',example_format_bold)
    worksheet.write('B1','Value',example_format_bold)
    worksheet.write('A2','Provided Author Name',example_format_bold)
    worksheet.write('B2',provided_author_name,example_format_text)

    worksheet.write('A3','Generated Author ID',example_format_bold)
    worksheet.write('B3',temp_author_id,example_format_text)

    worksheet.write('A4','Generated Study ID',example_format_bold)
    worksheet.write('B4',temp_study_id,example_format_text)

    # worksheet.autofit()
    worksheet.set_column('A:A', 25)
    worksheet.set_column('B:B', 25)

    return workbook, worksheet



@callback(
    [
        Output(component_id="download_curated_form", component_property="data")
    ],
    [
        Input(component_id='button_download_curated', component_property="n_clicks")
    ],
    [
        State(component_id="upload_store", component_property="data"),
        State(component_id="store_2", component_property="data"),
        State(component_id="store_3", component_property="data"),
        State(component_id="store_4", component_property="data"),
        State(component_id="author_store", component_property="data"),
    ],
    prevent_initial_call=True
)
def control_download_button(
    button_download_curated_n_clicks,
    upload_store_data,
    store_2_data,
    store_3_data,
    store_4_data,
    author_store_data
):
    upload_panda=pd.DataFrame.from_records(upload_store_data)
    store_2_panda=pd.DataFrame.from_records(store_2_data)
    store_3_panda=pd.DataFrame.from_records(store_3_data)
    store_4_panda=pd.DataFrame.from_records(store_4_data)
    author_panda=pd.DataFrame.from_records(author_store_data)


    download_panda,total_replacement_panda=generate_excel_for_download_from_stores(upload_panda,store_2_panda,store_3_panda,store_4_panda)


    #we have to also manually change the non curated nan to 'not available' because they do not receive the curation treatment
    download_panda.replace(
        to_replace={'nan':'not available'},
        inplace=True
    )


    ####generate the downlaodable excel file
    output_stream=io.BytesIO()
    temp_writer=pd.ExcelWriter(output_stream,engine='xlsxwriter')
    workbook=temp_writer.book

    empty_df=pd.DataFrame()
    empty_df.to_excel(temp_writer,sheet_name='title_page',index=False)
    #skip the last row which has the merger archetype info


    provided_author_name=author_panda.at[0,'Value']
    if pd.isnull(provided_author_name)==True:
        provided_author_name='noauthornameprovided'
    
    ####this is where we call the submission API####
    #sending provided author name, sample metadata sheet
    #receiving a study id and an author id if successful
    temp_study_id='1234.52345'
    temp_author_id='oliverfiehn'

    study_upload_success=requests.post(
        BASE_URL_API+'/addstudytodatabase/',json={
            'provided_author_name':provided_author_name,
            'sample_metadata_sheet_panda':download_panda.to_dict(orient='records')
        },
        # timeout=0.1
    ).json()
    temp_study_id=study_upload_success['study_id']
    temp_author_id=study_upload_success['author_id']



    #####


    empty_df.to_excel(temp_writer,sheet_name='author_metadata_curated',index=False)
    worksheet=temp_writer.sheets['author_metadata_curated']
    workbook, worksheet=fill_author_sheet_curated(temp_writer,workbook,worksheet,temp_study_id,temp_author_id,provided_author_name)

    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(download_panda)

    download_panda.to_excel(
        temp_writer,
        sheet_name='sample_sheet_curated',
        #index=False,
        #startrow=1,
        #take off the weird .0.1 etc
        header=[element.split('.')[0] for element in download_panda.columns]
    )

    #https://xlsxwriter.readthedocs.io/working_with_pandas.html
    #https://community.plotly.com/t/generate-multiple-tabs-in-excel-file-with-dcc-send-data-frame/53460/7
    workbook=temp_writer.book
    worksheet=temp_writer.sheets['sample_sheet_curated']

    worksheet.autofit()

    worksheet=temp_writer.sheets['title_page']
    worksheet.hide_gridlines()
    worksheet.write('B2','Standardized metadata on next sheet')

    temp_writer.save()
    temp_data=output_stream.getvalue()


    #####accumulate all new vocabulary terms per header

    #######################
    ###update use count###
    for index,series in total_replacement_panda.iterrows():
        
        try:

            usecount_success=requests.post(
                BASE_URL_API+'/updateusecountresource/',json={
                    'header':series['header'],
                    'main_string':series['main_string']
                },
                # timeout=0.1
            )


           
        except:
          # print('bypassed that long use_count session')
            pass
        
        
        
        
    ######################

    ####train new vocab####
    #we only want to train each "type of vocabulary" once
    if len(store_4_panda.index)>0:
        for temp_tuple in store_4_panda.groupby('header'):
        
            vocab_add_success=requests.post(
                BASE_URL_API+'/addtermstovocabularyresource/',json={
                    'header':temp_tuple[0],
                    'new_vocabulary':temp_tuple[1]['main_string'].unique().tolist()
                }
            )
            # no longer want to train each time because it is very slow
            # instead, train only according to some clock, like once every day or something
            # update, for the moment, until we install timer, train everytime
            # try:
            training_success=requests.post(
                BASE_URL_API+'/trainvocabularyresource/',json={
                    'header':temp_tuple[0],
                },
                # timeout=1
            )
            # except:
              # print('bypassed that long training session')
                # pass

    return [
        dcc.send_bytes(temp_data,"Fiehnlab_metadata_standardization_form_CURATED.xlsx")
    ]


@callback(
    [
        Output(component_id="stepper_submit_form", component_property="active"),
        Output(component_id="store_furthest_active", component_property="data"),
        
        Output(component_id="store_2", component_property="data"),
        Output(component_id="store_3", component_property="data"),
        Output(component_id="store_4", component_property="data"),

        Output(component_id="submit_step_1_error_div", component_property="children", allow_duplicate=True),
        Output(component_id="step_2", component_property="children"),
        Output(component_id="submit_step_2_error_div", component_property="children"),
        Output(component_id="step_3", component_property="children"),
        Output(component_id="step_4", component_property="children"),
        Output(component_id="submit_step_4_error_div", component_property="children"),

    ],
    [
        Input(component_id='stepper_submit_form_back', component_property="n_clicks"),
        Input(component_id='stepper_submit_form_next', component_property="n_clicks"),
        Input(component_id="upload_store", component_property="data"),
        Input(component_id={'type':'step_2_curation_checkbox','index':ALL}, component_property="checked"),
        Input(component_id={'type':'dropdown_empty_options','index':ALL}, component_property="value"),
    ],
    [
        State(component_id="stepper_submit_form", component_property="active"),
        State(component_id="store_furthest_active", component_property="data"),
        State(component_id="upload_store", component_property="data"),
        State(component_id="store_2", component_property="data"),
        State(component_id="store_3", component_property="data"),
        State(component_id="store_4", component_property="data"),
        State(component_id="submit_step_1_error_div", component_property="children"),
        State(component_id="step_2", component_property="children"),
        State(component_id="submit_step_2_error_div", component_property="children"),
        State(component_id="step_3", component_property="children"),
        State(component_id="step_4", component_property="children"),
        State(component_id="submit_step_4_error_div", component_property="children"),
        State(component_id={'type':'step_2_curation_checkbox','index':ALL}, component_property="checked"),
        State(component_id='step_2_curation_checkbox_all_correct', component_property="checked"),
        State(component_id={'type':'dropdown_empty_options','index':ALL}, component_property="value"),
        State(component_id={'type':'input_creation','index':ALL}, component_property="value"),
    ],
    prevent_initial_call=True,
    suppress_callback_exceptions=True
)
def update_step_submit(
    stepper_submit_form_back_n_clicks, 
    stepper_submit_form_next_n_clicks, 
    input_upload_store_data,
    input_step_2_curation_checkbox_n_clicks_ALL,
    input_store_dropdown_empty_options_value_ALL,
    stepper_submit_form_active,
    store_furthest_active_data,
    upload_store_data,
    store_2_data,
    store_3_data,
    store_4_data,
    submit_step_1_error_div_children,
    step_2_children,
    submit_step_2_error_div_children,
    step_3_children,
    step_4_children,
    submit_step_4_error_div_children,
    state_step_2_curation_checkbox_n_clicks_ALL,
    step_2_curation_checkbox_all_correct_checked,
    state_dropdown_empty_options_value_ALL,
    input_creation_value_ALL
):
    '''
    we wnat to only do work according to the step that we are outputting
    for example, we only want to output the step_2_children if stepper_submit_form_active becomes 1
    '''
    
    # need_to_generate_new_children=True
    #if a new upload triggered things
    if ctx.triggered_id=='upload_store': #the ALL ones
        store_furthest_active_data=stepper_submit_form_active
        return [stepper_submit_form_active,store_furthest_active_data,store_2_data,store_3_data,store_4_data,submit_step_1_error_div_children,step_2_children,submit_step_2_error_div_children,step_3_children,step_4_children,submit_step_4_error_div_children]

    #if a button click in one of the children steps triggered things
    if type(ctx.triggered_id)==dash._utils.AttributeDict:
        store_furthest_active_data=stepper_submit_form_active
        return [stepper_submit_form_active,store_furthest_active_data,store_2_data,store_3_data,store_4_data,submit_step_1_error_div_children,step_2_children,submit_step_2_error_div_children,step_3_children,step_4_children,submit_step_4_error_div_children]

    #if we are going back, just go back
    if ctx.triggered_id=="stepper_submit_form_back" and stepper_submit_form_active>0:
        stepper_submit_form_active-=1
        junk_patch=Patch()
        #the [] is returned to get rid of error messages
        return [stepper_submit_form_active,junk_patch,junk_patch,junk_patch,junk_patch,junk_patch,junk_patch,[],junk_patch,junk_patch,[]]

    #if we are going forward....
    elif ctx.triggered_id=="stepper_submit_form_next" and stepper_submit_form_active<(NUM_STEPS_SUBMIT-1):
        #if we are on the first step
        if stepper_submit_form_active==0:

            submit_step_1_errors=submit_step_1_error_checker(upload_store_data)

            #if there are errors
            if submit_step_1_errors!=False:
                junk_patch=Patch()
                curate_button_children=dbc.Row(
                    children=[
                        dbc.Col(width=4),
                        dbc.Col(
                            children=[dmc.Alert(submit_step_1_errors,withCloseButton=True)],
                            width=4,
                        ),
                        dbc.Col(width=4)
                    ]
                )
                return [stepper_submit_form_active,store_furthest_active_data,store_2_data,store_3_data,store_4_data,curate_button_children,step_2_children,submit_step_2_error_div_children,step_3_children,step_4_children,submit_step_4_error_div_children]
        elif stepper_submit_form_active==1:
            submit_step_2_errors=submit_step_2_error_checker(state_step_2_curation_checkbox_n_clicks_ALL,step_2_curation_checkbox_all_correct_checked)
            if submit_step_2_errors!=False:
                junk_patch=Patch()
                curate_button_children=dbc.Row(
                    children=[
                        dbc.Col(width=4),
                        dbc.Col(
                            children=[dmc.Alert(submit_step_2_errors,withCloseButton=True)],
                            width=4,
                        ),
                        dbc.Col(width=4)
                    ]
                )
                return [stepper_submit_form_active,store_furthest_active_data,store_2_data,store_3_data,store_4_data,submit_step_1_error_div_children,step_2_children,curate_button_children,step_3_children,step_4_children,submit_step_4_error_div_children]
        elif stepper_submit_form_active==3:
            submit_step_4_errors=submit_step_4_error_checker(input_creation_value_ALL,store_3_data)
            if submit_step_4_errors!=False:
                junk_patch=Patch()
                curate_button_children=dbc.Row(
                    children=[
                        dbc.Col(width=4),
                        dbc.Col(
                            children=[dmc.Alert(submit_step_4_errors,withCloseButton=True)],
                            width=4,
                        ),
                        dbc.Col(width=4)
                    ]
                )
                return [stepper_submit_form_active,store_furthest_active_data,store_2_data,store_3_data,store_4_data,submit_step_1_error_div_children,step_2_children,submit_step_2_error_div_children,step_3_children,step_4_children,curate_button_children]


        #if the errors are non existent, then proceed with updates
        stepper_submit_form_active+=1   
        junk_patch=Patch()
        if stepper_submit_form_active > store_furthest_active_data:
            store_furthest_active_data=stepper_submit_form_active
        else:
            return [stepper_submit_form_active,junk_patch,junk_patch,junk_patch,junk_patch,junk_patch,junk_patch,junk_patch,junk_patch,junk_patch,junk_patch]

    # #if we enter step 2
    if stepper_submit_form_active==1:
        upload_store_panda=pd.DataFrame.from_records(upload_store_data)
        '''
            species.0 species.1.0 species.1.1 organ.0
        0     humen       mouse   porcupine   liver
        1     humen        mouo        None   lunge
        '''

        written_strings_per_category=parse_stored_excel_file(upload_store_panda)
        '''
        {'organ': ['liver', 'lunge'],
        'species': ['humen', 'mouse', 'mouo', 'porcupine']}
        '''

        panda_for_store_2,step_2_children=generate_step_2_layout_and_data_for_store(written_strings_per_category)
        store_2_data=panda_for_store_2.to_dict(orient='records')

    elif stepper_submit_form_active==2:
        panda_for_store_3,step_3_children=generate_step_3_layout_and_data_for_store(
            store_2_data,
            state_step_2_curation_checkbox_n_clicks_ALL,
        )
        store_3_data=panda_for_store_3.to_dict(orient='records')

    elif stepper_submit_form_active==3:
        panda_for_store_4,step_4_children=generate_step_4_layout_and_data_for_store(
            store_3_data,
            state_dropdown_empty_options_value_ALL
        )
        store_4_data=panda_for_store_4.to_dict(orient='records')

    return [stepper_submit_form_active,store_furthest_active_data,store_2_data,store_3_data,store_4_data,submit_step_1_error_div_children,step_2_children,submit_step_2_error_div_children,step_3_children,step_4_children,submit_step_4_error_div_children]


def submit_step_4_error_checker(input_creation_value_ALL,store_3_data):
    #if any are none, then return with error

    for temp in input_creation_value_ALL:
        if temp=='' or temp==None:
            return 'Values cannot be empty. Either add a new term or accept one on previous steps.'
    
    outbound_json={
        'new_vocabulary':input_creation_value_ALL
    }

    temp_values=requests.post(BASE_URL_API+'/validatetermsfortrainingresource/',json=outbound_json).json()

    for temp_error in temp_values['errors']:
        if temp_error!=False:
            return temp_error

    return False

def submit_step_2_error_checker(state_step_2_curation_checkbox_n_clicks_ALL,step_2_curation_checkbox_all_correct_checked):

    #^ means XOR in python for bitwise comparisons
    if ((any(state_step_2_curation_checkbox_n_clicks_ALL)) ^ step_2_curation_checkbox_all_correct_checked):
        return False
    else:
        return ['Please indicate if curations are wrong OR all are correct.']

def submit_step_1_error_checker(upload_store_data):
    if upload_store_data==None:
        return 'Must upload a valid .xlsx'
    else:
        return False


def generate_step_4_layout_and_data_for_store(store_3_data,state_dropdown_empty_options_value_ALL):
    store_3_panda=pd.DataFrame.from_records(store_3_data)

    subset_boolean_list=[True if temp==None else False for temp in state_dropdown_empty_options_value_ALL]

    store_4_panda_output=store_3_panda.loc[subset_boolean_list]

    if len(store_4_panda_output.index)==0:
        output_children=[
            html.Br(),
            html.Br(),
            dbc.Row(
                children=[
                    dbc.Col(
                        width=3
                    ),    
                    dbc.Col(
                        html.Div(
                            children=[
                                html.H3('Previous curations accepted - please continue')
                            ],
                            style={'text-align':'center'}
                        )
                    ),
                    dbc.Col(
                        width=3
                    ),   
                    html.Div(
                        id="submit_step_4_error_div",
                        children=[]       
                    )
                ]
            ),
        ]
        html.H3('need to figure out when there are no curations to do')
    else:
        output_children=list()

        output_children.append(html.Br())

        output_children.append(
            dbc.Row(
                children=[
                    dbc.Col(width=4),
                    dbc.Col(
                        html.Div(
                            dbc.Card(
                                children=[
                                    html.H6(''),
                                    # html.H6('Automatic Curation Step'),
                                    html.H4('•We add these terms for the next user•'),
                                    html.H4('•Please confirm spelling•',style={"color": "red", "font-weight": "bold"}),
                                    html.H6(''),
                                ],
                                color='#fff4e4',
                                style={
                                    'textAlign':'center',
                                    "box-shadow": "1px 2px 7px 0px red",
                                    "border-radius": "10px"
                                }
                            ),
                            
                        ),
                        width=4
                    ),
                    dbc.Col(width=4),
                ]
            )
        )
        output_children.append(html.Br())

        output_children.append(
            dbc.Row(
                children=[
                    dbc.Col(width=3),
                    dbc.Col(
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    html.H2('You Wrote'),
                                    style={'text-align':'left'},
                                    width=4
                                ),
                                dbc.Col(
                                    html.H2('Terms for future use'),
                                    style={'text-align':'center'},
                                    # width=3
                                ),   
                            ]
                        ),
                        width=5
                    ),
                    dbc.Col(width=4)
                ]
            )
        )
        output_children.append(
            html.Div(
                id="submit_step_4_error_div",
                children=[]       
            )
        )

        for index,series in store_4_panda_output.iterrows():
            output_children.append(
                dbc.Row(
                    children=[
                        dbc.Col(width=3),
                        dbc.Col(
                            children=[
                                dbc.Card(
                                    children=[
                                        dbc.Row(
                                            children=[
                                                dbc.Col(
                                                    html.H6(series['header']+': '+series['written_string']),
                                                    style={'text-align':'center','white-space':'normal'},
                                                    width=3
                                                ),
                                                dbc.Col(
                                                    html.Div(
                                                        dcc.Input(
                                                            id={
                                                                'type':'input_creation',
                                                                'index':series['header']+'_'+series['written_string'],
                                                            },
                                                            value=series['written_string']
                                                            #placeholder="Please enter new term"
                                                        ),
                                                        className="d-flex justify-content-center align-items-center"
                                                    ),
                                                    # width=3
                                                )
                                            ]
                                        )
                                    ],
                                    color='#fff4e4',
                                    style={
                                        "box-shadow": "1px 2px 7px 0px grey",
                                        "border-radius": "10px"
                                    },
                                    className="text-center text-nowrap my-2 p-2 mw-55"
                                )
                            ],
                            width=6
                        ),
                        dbc.Col(width=3)
                    ],
                ),
            )


    store_4_panda_output['valid_string']=np.nan
    store_4_panda_output['main_string']=np.nan

    return [store_4_panda_output,output_children]


def generate_step_3_layout_and_data_for_store(store_2_data,step_2_curation_checkbox_n_clicks_ALL):

    store_2_panda=pd.DataFrame.from_records(store_2_data)

    store_3_panda_output=store_2_panda.copy().loc[step_2_curation_checkbox_n_clicks_ALL]

    written_strings_to_substring_panda=store_2_panda.loc[step_2_curation_checkbox_n_clicks_ALL]
    if len(written_strings_to_substring_panda.index)==0:

        output_children=[
            html.Br(),
            html.Br(),
            dbc.Row(
                children=[
                    dbc.Col(
                        width=3
                    ),    
                    dbc.Col(
                        html.Div(
                            children=[
                                html.H3('Previous curations accepted - please continue')
                            ],
                            style={'text-align':'center'}
                        )
                    ),
                    dbc.Col(
                        width=3
                    ),   
                ]
            )
        ]
    else:
        output_children=list()

        output_children.append(
            html.Br()
        )

        output_children.append(
            dbc.Row(
                children=[
                    dbc.Col(width=4),
                    dbc.Col(
                        html.Div(
                            dbc.Card(
                                children=[
                                    html.H6(''),
                                    # html.H6('Automatic Curation Step'),
                                    html.H4('•Manually check vocabularies for matches•',style={"color": "red", "font-weight": "bold"}),
                                    html.H4('•If no match, leave blank•',style={"color": "red", "font-weight": "bold"}),
                                    # html.H4('•If no match, leave blank•',style={"color": "black", "font-weight": "bold"}),
                                    # html.H6('•Species searches may lag•'),
                                    html.H6(''),
                                ],
                                color='#fff4e4',
                                style={
                                    'textAlign':'center',
                                    "box-shadow": "1px 2px 7px 0px red",
                                    "border-radius": "10px"
                                }
                            ),
                            
                        ),
                        width=4
                    ),
                    dbc.Col(width=4),
                ]
            )
        )
        output_children.append(html.Br())

        output_children.append(
            dbc.Row(
                children=[
                    dbc.Col(width=3),
                    dbc.Col(
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    html.H2('You Wrote'),
                                    style={'text-align':'left'},
                                    width=4
                                ),
                                dbc.Col(
                                    html.H2('Vocabulary Search'),
                                    style={'text-align':'center'},
                                ),   

                            ]
                        ),
                        width=5
                    ),
                    dbc.Col(width=4)
                        
                ]
            )
        )

            
        for index,series in store_3_panda_output.iterrows():
            
            output_children.append(
                dbc.Row(
                    children=[
                        dbc.Col(width=3),
                        dbc.Col(
                            children=[

                                dbc.Card(
                                    children=[
                                        dbc.Row(
                                            children=[
                                                dbc.Col(
                                                    html.H6(series['header']+': '+series['written_string']),
                                                    style={'text-align':'center','white-space':'normal'},
                                                    width=3
                                                ),
                                                dbc.Col(
                                                    dcc.Dropdown(
                                                        id={
                                                            'type':'dropdown_empty_options',
                                                            'index':series['header']+'_'+series['written_string']
                                                        },
                                                        multi=False,
                                                        placeholder='Type to search',
                                                        options=['Type to populate options.'],
                                                        optionHeight=60
                                                    ),
                                                    style={'text-align':'center'},
                                                    # width=3
                                                ),
                                            ]
                                        )
                                    ],
                                    color='#fff4e4',
                                    style={
                                        "box-shadow": "1px 2px 7px 0px grey",
                                        "border-radius": "10px"
                                    },
                                    className="text-center text-nowrap my-2 p-2 mw-55"
                                )
                            ],
                            width=6
                        ),
                        dbc.Col(width=3)
                    ],
                ),
            )
              


    store_3_panda_output['valid_string']=np.nan
    store_3_panda_output['main_string']=np.nan

    return [store_3_panda_output,output_children]

               
@callback(
    [
        Output(component_id={'type':'dropdown_empty_options','index':MATCH},component_property='options'),
    ],
    [
        Input(component_id={'type':'dropdown_empty_options','index':MATCH},component_property='search_value'),
    ],
)
def update_options(
    dropdown_empty_options_search_value,
    # header_written_pair_children
):
    '''
    generates the labels in the substring dropdown
    ISSUE 36
    ISSUE 37
    '''


    if not dropdown_empty_options_search_value:
        raise PreventUpdate

    if ctx.triggered_id['index'].split('_')[0] not in HEADERS_WITH_SHORT_NGRAMS:
        if len(dropdown_empty_options_search_value)<3:
            raise PreventUpdate

    current_index=ctx.triggered_id['index'].split('_')[0].split('.')[0]

    outbound_json={
        'header':current_index,
        'substring':dropdown_empty_options_search_value
    }
    temp_values=requests.post(BASE_URL_API+'/generatesubstringmatchesresource/',json=outbound_json).json()

  # print(temp_values)

    return [
        [
            {'label': temp_string,'value': temp_string} if (temp_string.split(' AKA ')[0] != temp_string.split(' AKA ')[1]) else {'label': temp_string.split(' AKA ')[0],'value': temp_string} for temp_string in temp_values
        ]
    ]




def generate_step_2_layout_and_data_for_store(written_strings_per_category):

    curation_dict=dict()
    #get curation proposals
    for temp_header in written_strings_per_category.keys():

        if temp_header not in subset_per_heading_json.keys():
            continue
        curation_dict[temp_header]=dict()

        for temp_written_string in written_strings_per_category[temp_header]:

            prediction_request={
                "header":temp_header,
                "written_strings":[temp_written_string],
                "neighbors_to_retrieve":NEIGHBORS_TO_RETRIEVE
            }

            response = requests.post(BASE_URL_API + "/predictvocabularytermsresource/", json=prediction_request)
            this_strings_neighbors = pd.read_json(response.json(), orient="records")  
        
            curation_dict[temp_header][temp_written_string]={
                'main_string':this_strings_neighbors.at[0,'main_string'],
                'valid_string':this_strings_neighbors.at[0,'valid_string']
            }
    
    #what we really should do is make the panda firs so that the rest of this method can look like steps 3 and 4
    curation_panda_dict={
        'header':[],
        'written_string':[],
        'valid_string':[],
        'main_string':[]
    }
    for temp_header in curation_dict.keys():
        for temp_written_string in (curation_dict[temp_header]):
            curation_panda_dict['header'].append(temp_header)
            curation_panda_dict['written_string'].append(temp_written_string)
            curation_panda_dict['valid_string'].append(curation_dict[temp_header][temp_written_string]['valid_string'])
            curation_panda_dict['main_string'].append(curation_dict[temp_header][temp_written_string]['main_string'])
    curation_panda=pd.DataFrame.from_dict(curation_panda_dict)

    output_children=list()

    output_children.append(
        html.Div(
            id="submit_step_2_error_div",
            children=[]       
        )
    )
    output_children.append(
        html.Br()
    )
    output_children.append(
        dbc.Row(
            children=[
                dbc.Col(width=4),
                dbc.Col(
                    html.Div(
                        dbc.Card(
                            children=[
                                html.H6(''),
                                html.H4('•We map written words to vocabulary terms•'),
                                html.H4('•Please mark any mistakes•',style={"color": "red", "font-weight": "bold"}),
                                html.H6(''),
                            ],
                            color='#fff4e4',
                            style={
                                'textAlign':'center',
                                "box-shadow": "1px 2px 7px 0px red",
                                "border-radius": "10px"
                            }
                        ),
                    ),
                    width=4
                ),
                dbc.Col(width=4),
            ]
        )
    )
    output_children.append(html.Br())
    output_children.append(
        html.Div(
            id="submit_step_2_error_div",
            children=[]       
        )
    )
    output_children.append(html.Br())

    output_children.append(
        dbc.Row(
            children=[
                dbc.Col(width=3),
                dbc.Col(
                    html.H2('You Wrote'),
                    style={'text-align':'center'},
                    width=2
                ),
                dbc.Col(
                    html.H2('We Guessed'),
                    style={'text-align':'center'},
                    width=2
                ),   
                dbc.Col(
                    html.H2('Incorrect?') ,
                    style={'text-align':'center'},
                    width=2
                ),
            ]
        )
    )
    for index,series in curation_panda.iterrows():
        
        output_children.append(
            dbc.Row(
                children=[
                    dbc.Col(width=3),
                    dbc.Col(
                        children=[
                            dbc.Card(
                                children=[
                                    dbc.Row(
                                        children=[
                                            dbc.Col(
                                                html.H6(series['header']+': '+series['written_string']),
                                                style={'text-align':'center','white-space':'normal'},
                                                width=4
                                            ),
                                            dbc.Col(
                                                html.H6(
                                                    series['main_string']
                                                ),
                                                style={'text-align':'center'},
                                                width=4
                                            ), 
                                            dbc.Col(
                                                html.Div(
                                                    dmc.Checkbox(
                                                        id={
                                                            'type':'step_2_curation_checkbox',
                                                            'index':str(temp_header)+'_'+str(temp_written_string)
                                                        },
                                                        checked=False,
                                                        style={'horizontal-align': 'center'},
                                                        styles= {
                                                            "input": {"borderColor": 'black'}
                                                        },
                                                        color='darkBlue'
                                                    ),
                                                    className="d-flex justify-content-center align-items-center"
                                                    #style={'text-align':'center'},
                                                ),
                                                align='center',
                                                width=4
                                            ),
                                        ]
                                    )
                                ],
                                color='#fff4e4',
                                style={
                                    "box-shadow": "1px 2px 7px 0px grey",
                                    "border-radius": "10px"
                                },
                                className="text-center text-nowrap my-2 p-2 mw-55"
                            )
                        ],
                        width=6
                    ),
                    dbc.Col(width=3)
                ],
            ),
        )


    output_children.append(
        html.Br(),
    )

    output_children.append(
        dbc.Row(
            children=[
                dbc.Col(width=4),
                dbc.Col(
                    children=[
                        dbc.Card(
                            children=[
                                dbc.Row(
                                    children=[
                                        dbc.Col(width=3),
                                        dbc.Col(
                                            children=[
                                                html.H6('No errors? Check here:'),
                                            ],
                                        ),
                                        dbc.Col(
                                            children=[
                                                dmc.Checkbox(
                                                    id='step_2_curation_checkbox_all_correct',
                                                    checked=False,
                                                    style={'horizontal-align': 'center'},

                                                    styles= {
                                                        "input": {"borderColor": 'black'}
                                                    },
                                                    color='darkBlue'
                                                ),
                                            ],
                                        ),

                                    ]
                                )
                            ],
                            color='#fff4e4',
                            style={
                                "box-shadow": "1px 2px 7px 0px grey",
                                "border-radius": "10px"
                            },
                            className="text-center text-nowrap my-2 p-2 mw-55"
                        )
                    ],
                    width=4
                ),
                dbc.Col(width=6)

            ],
            
        ),
        
    )


    return curation_panda,output_children


@callback(
    [
        Output(component_id="upload_form",component_property="children"),
        Output(component_id="upload_store",component_property="data"),
        Output(component_id="submit_step_1_error_div",component_property="children"),
        Output(component_id="author_store",component_property="data"),
    ],
    [
        Input(component_id="upload_form", component_property="contents"),
    ],
    [
        State(component_id="upload_form", component_property="filename"),
    ],
    prevent_initial_call=True
)
def upload_form(
    upload_form_contents,
    upload_form_filename,
):
    if upload_form_contents==None:
        raise PreventUpdate
    
    '''
    accept the form back from the user
    need to have a more fully fledged format-checking and error throwing suite
    '''

    content_type, content_string = upload_form_contents.split(',')

    #declare instance of upload error tester here
    #run through error tests. excel tests first
    #the error checker returns False for each condition that doesnt have a problem
    #so we check for each problem, and if they are all false, move on to the next situation
    my_SampleMetadataUploadChecker=samplemetadatauploadchecker.SampleMetadataUploadChecker(
        content_string,
        # FORM_HEADER_DICT
        # header_button_column_relationships
        ALL_METADATA_COLUMNS
    )
    excel_sheet_checks=list()
    excel_sheet_checks.append(my_SampleMetadataUploadChecker.create_workbook())
    if excel_sheet_checks[0]==False:
        excel_sheet_checks.append(my_SampleMetadataUploadChecker.lacks_sheetname())
    #if we ahve any errors
    if any(map(lambda x: isinstance(x,str),excel_sheet_checks)):
        curate_button_children=dbc.Row(
            children=[
                dbc.Col(width=4),
                dbc.Col(
                    children=[dmc.Alert(element,withCloseButton=True) for element in excel_sheet_checks if element!=False],
                    width=4,
                ),
                dbc.Col(width=4)
            ]
        )
        temp_dataframe_output=None
        temp_author_output=None

    else:
        dataframe_checks=list()
        my_SampleMetadataUploadChecker.create_dataframe()
        dataframe_checks.append(my_SampleMetadataUploadChecker.headers_malformed())
        dataframe_checks.append(my_SampleMetadataUploadChecker.contains_underscore())
        dataframe_checks.append(my_SampleMetadataUploadChecker.contains_no_sample_rows())
        # if there are any errors
        if any(map(lambda x: isinstance(x,str),dataframe_checks)):
            curate_button_children=dbc.Row(
                children=[
                    dbc.Col(width=4),
                    dbc.Col(
                        children=[dmc.Alert(element,withCloseButton=True) for element in dataframe_checks if element!=False],
                        width=4,
                    ),
                    dbc.Col(width=4)
                ]
            )
            
            temp_dataframe_output=None
            temp_author_output=None

        #if there are no problems with the excel file or dataframe
        else:
            curate_button_children=[]

            decoded=base64.b64decode(content_string)
            temp_dataframe=pd.read_excel(
                io.BytesIO(decoded),
                sheet_name='sample_sheet',
                #skiprows=1
                index_col=0
            )

            

            temp_dataframe=split_columns_if_delimited(temp_dataframe)

            temp_dataframe=add_dot_zero_if_none(temp_dataframe)
            print(temp_dataframe)
            # temp_dataframe_output=dict()
            temp_dataframe_output=temp_dataframe.to_dict(orient='records')

            temp_dataframe=pd.read_excel(
                io.BytesIO(decoded),
                sheet_name='author_metadata',
                #skiprows=1
                index_col=None
            )

            temp_author_output=temp_dataframe.to_dict(orient='records')
            print(temp_dataframe)



    displayed_name=html.Div([upload_form_filename],className='text-center')
    return [displayed_name,temp_dataframe_output,curate_button_children,temp_author_output]