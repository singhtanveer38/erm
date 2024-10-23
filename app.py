from helper import connect, close_connection, read_config
import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import numpy as np

def filteredClass(class_df, std, section, exam):
    return class_df[(class_df["class"] == std) & (class_df["section"] == section) & (class_df["exam"] == exam)]

def filteredSubject(subject_df, std, section, exam, subject):
    return subject_df[(subject_df["class"] == std) & (subject_df["section"] == section) & (subject_df["exam"] == exam) & (subject_df["subject"] == subject)]

@callback(
        Output("percent_df_table", "data"),
        Input("class", "value"),
        Input("section", "value"),
        Input("exam", "value"),
        )
def update_percent_df_table(std, section, exam):
    return filteredClass(class_df, std, section, exam).sort_values(by=["percentage"], ascending=False).to_dict("records")

@callback(
        Output("subject_df_table", "data"),
        Input("class", "value"),
        Input("section", "value"),
        Input("exam", "value"),
        Input("subject", "value"),
        )
def update_subject_df_table(std, section, exam, subject):
    return filteredSubject(subject_df, std, section, exam, subject).sort_values(by=["percentage"], ascending=False).to_dict("records")

@callback(
        Output("total_enrolled", "children"),
        Input("class", "value"),
        Input("section", "value"),
        Input("exam", "value"),
        )
def update_total_enrolled(std, section, exam):
    return filteredClass(class_df, std, section, exam).shape[0]

@callback(
        Output("total_passed", "children"),
        Input("class", "value"),
        Input("section", "value"),
        Input("exam", "value"),
        )
def update_total_passed(std, section, exam):
    return class_df[(class_df["class"] == std) & (class_df["section"] == section) & (class_df["exam"] == exam) & (class_df["category"] != 'below_33')].shape[0]

@callback(
        Output("total_enrolled_subject", "children"),
        Input("class", "value"),
        Input("section", "value"),
        Input("exam", "value"),
        Input("subject", "value"),
        )
def update_subject_enrolled(std, section, exam, subject):
    return filteredSubject(subject_df, std, section, exam, subject).shape[0]

@callback(
        Output("total_passed_subject", "children"),
        Input("class", "value"),
        Input("section", "value"),
        Input("exam", "value"),
        Input("subject", "value"),
        )
def update_subject_passed(std, section, exam, subject):
    return subject_df[(subject_df["class"] == std) & (subject_df["section"] == section) & (subject_df["exam"] == exam) & (subject_df["subject"] == subject) & (subject_df["category"] != 'below_33')].shape[0]

@callback(
        Output("category_distribution_class", "figure"),
        Input("class", "value"),
        Input("section", "value"),
        Input("exam", "value"),
        )
def update_category_distribution_class(std, section, exam):
    fig = px.bar(
            class_df["category"][(class_df["class"] == std) & (class_df["section"] == section) & (class_df["exam"] == exam)].value_counts(),
            title="Category-wise Distrubution in Class",
            labels={"category": "Category", "value": "No. of Students"}
            )
    fig.update_layout(showlegend=False)
    return fig

@callback(
        Output("category_distribution_subject", "figure"),
        Input("class", "value"),
        Input("section", "value"),
        Input("exam", "value"),
        Input("subject", "value"),
        )
def update_category_distribution_subject(std, section, exam, subject):
    fig = px.bar(
            subject_df["category"][(subject_df["class"] == std) & (subject_df["section"] == section) & (subject_df["exam"] == exam) & (subject_df["subject"] == subject)].value_counts(),
            title="Category-wise Distrubution in subject",
            labels={"category": "Category", "value": "No. of Students"}
            )
    fig.update_layout(showlegend=False)
    return fig

# conn = psycopg2.connect(host="localhost", user="postgres", password="password", database="kv")
# curr = conn.cursor()
config = read_config()
conn, curr = connect(config["hostname"], config["port"], config["username"], config["password"], config["db_name"])

curr.execute("select * from marks")

df = pd.DataFrame(curr.fetchall(), columns=None)

conn.close()

df.columns = ["roll", "name", "class", "section", "exam", "exam_total", "subject", "marks"]
df.head()

subject_df = df.copy()
subject_df["percentage"] = round((subject_df["marks"]/subject_df["exam_total"]) * 100, 2)

subject_category = []
for i in subject_df["percentage"]:
    if i < 33:
        subject_category.append("below_33")
    elif 33 <= i < 45:
        subject_category.append("33_to_45")
    elif 45 <= i < 60:
        subject_category.append("45_to_60")
    elif 60 <= i < 75:
        subject_category.append("60_to_75")
    elif 75 <= i < 90:
        subject_category.append("75_to_90")
    elif i >= 90:
        subject_category.append("above_90")
    else:
        subject_category.append("absent")

subject_df["category"] = subject_category

class_df = df.copy()

class_df = class_df.groupby(by=["roll", "name", "class", "section", "exam", "exam_total"], as_index=False).agg({'marks': 'sum'})
class_df["percentage"] = round((class_df["marks"]/(class_df["exam_total"]*6))*100, 2)

class_category = []
for i in class_df["percentage"]:
    if i < 33:
        class_category.append("below_33")
    elif 33 <= i < 45:
        class_category.append("33_to_45")
    elif 45 <= i < 60:
        class_category.append("45_to_60")
    elif 60 <= i < 75:
        class_category.append("60_to_75")
    elif 75 <= i < 90:
        class_category.append("75_to_90")
    elif i >= 90:
        class_category.append("above_90")
    else:
        class_category.append("absent")

class_df["category"] = class_category

app = Dash(external_stylesheets=[dbc.themes.SPACELAB])
server = app.server

app.layout = dbc.Container([
        html.H1(children="KV Result Analysis"),

        html.H2(children="Overall Performance of Students"),

        html.P(children="Class"),
        dcc.Dropdown(class_df["class"].unique(), class_df["class"][0], id="class"),
        html.P(children="Section"),
        dcc.Dropdown(class_df["section"].unique(), class_df["section"][0], id="section"),
        html.P(children="Exam"),
        dcc.Dropdown(class_df["exam"].unique(), class_df["exam"][0], id="exam"),

        html.H3(children="Total Enrolled"),
        html.P(id="total_enrolled"),

        html.H3(children="Total Passed"),
        html.P(id="total_passed"),

        dash_table.DataTable(id="percent_df_table", page_size=10),

        dcc.Graph(id="category_distribution_class"),

        html.H2(children="Subject-Wise Performance of Students"),

        html.P(children="Subject"),

        dcc.Dropdown(subject_df["subject"].unique(), subject_df["subject"][0], id="subject"),

        html.H3(children="Total Enrolled"),
        html.P(id="total_enrolled_subject"),

        html.H3(children="Total Passed"),
        html.P(id="total_passed_subject"),

        dash_table.DataTable(id="subject_df_table", page_size=10),

        dcc.Graph(id="category_distribution_subject"),
        ])

app.run(debug=True)

#app.run_server(debug=False)
