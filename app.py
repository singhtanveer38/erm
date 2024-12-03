from helper import connect, close_connection, read_config
import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import numpy as np

def filteredClass(class_df, std, section, exam):
    return class_df[(class_df["class"] == std) & (class_df["section"] == section) & (class_df["exam_name"] == exam)]

def filteredSubject(subject_df, std, section, exam, subject):
    return subject_df[(subject_df["class"] == std) & (subject_df["section"] == section) & (subject_df["exam_name"] == exam) & (subject_df["subject"] == subject)]

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
    return class_df[(class_df["class"] == std) & (class_df["section"] == section) & (class_df["exam_name"] == exam) & (class_df["category"] != '0_to_33')].shape[0]

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
    return subject_df[(subject_df["class"] == std) & (subject_df["section"] == section) & (subject_df["exam_name"] == exam) & (subject_df["subject"] == subject) & (subject_df["category"] != '0_to_33')].shape[0]

@callback(
        Output("category_distribution_class", "figure"),
        Input("class", "value"),
        Input("section", "value"),
        Input("exam", "value"),
        )
def update_category_distribution_class(std, section, exam):
    fig = px.bar(
            class_df["category"][(class_df["class"] == std) & (class_df["section"] == section) & (class_df["exam_name"] == exam)].value_counts(),
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
            subject_df["category"][(subject_df["class"] == std) & (subject_df["section"] == section) & (subject_df["exam_name"] == exam) & (subject_df["subject"] == subject)].value_counts(),
            title="Category-wise Distrubution in subject",
            labels={"category": "Category", "value": "No. of Students"}
            )
    fig.update_layout(showlegend=False)
    return fig

config = read_config()
conn, curr = connect(config["hostname"], config["port"], config["username"], config["password"], config["db_name"])

curr.execute("select * from marks")
subject_df = pd.DataFrame(curr.fetchall(), columns=None)
subject_df.columns = ["roll", "name", "class", "section", "exam_name", "exam_marks", "subject", "marks_obtained", "attendence", "percentage", "category"]

curr.execute("select * from overall_result")
class_df = pd.DataFrame(curr.fetchall(), columns=None)
class_df.columns = ["roll", "name", "class", "section", "exam_name", "exam_total", "marks_obtained", "percentage", "category"]

conn.close()

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
        dcc.Dropdown(class_df["exam_name"].unique(), class_df["exam_name"][0], id="exam"),

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

if __name__ == '__main__':
    app.run(debug=False)
