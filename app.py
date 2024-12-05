import sqlite3
import pandas as pd
import numpy as np
from shinyswatch import theme
from shiny import App, Inputs, Outputs, Session, render, ui, reactive
from shinywidgets import output_widget, render_widget
import plotly.graph_objects as go



conn = sqlite3.connect('nba_college.db')
c = conn.cursor()

names_query = """
SELECT DISTINCT player_name
FROM nba
"""
c.execute(names_query)
results6 = c.fetchall()
names = [i[0] for i in results6]








# Define the UI
app_ui = ui.page_fluid(
    ui.panel_title('College to NBA analysis'),
    ui.layout_sidebar(
        ui.sidebar(
            ui.h3("Filter"),
            ui.input_select(
                "name_select",  
                "Select a name:",  
                names
            ),
            ui.input_select(
                "stat_select",  
                "Stat:",  
                ["PTS", "AST", "REB", "STL", "BLK"]  
            ),
        ),
        ui.page_auto(
            ui.output_text("selected_name"),

            ui.layout_column_wrap(
                ui.value_box(
                    "Year",
                    ui.output_text('year_box_content'),
                    theme="gradient-blue-indigo"
                ),

                ui.value_box(
                    "Round Number",
                    ui.output_text('round_box_content'),
                    theme="gradient-blue-indigo",
                ),

                ui.value_box(
                    "Round Pick",
                    ui.output_text('pick_box_content'),
                    theme="gradient-blue-indigo",
                ),
                fill=False,
            ),
        output_widget('plot'))
    ),
    theme = theme.darkly
)















def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.text
    def selected_name():
        # Extract the selected value from the input_select
        name = input.name_select()
        return f"You selected: {name}"
    
    @reactive.Calc
    def draft_query():
        conn = sqlite3.connect('nba_college.db')
        c = conn.cursor()

        draft_query = f"""
        SELECT year, [round number], [round pick]
        FROM draft
        WHERE player_name = '{input.name_select()}'
        """

        c.execute(draft_query)
        results = c.fetchall()
        return results


    @output
    @render.text
    def year_box_content():
        return f'{draft_query()[0][0]}'
    
    @output
    @render.text
    def round_box_content():
        return f'{draft_query()[0][1]}'
    
    @output
    @render.text
    def pick_box_content():
        return f'{draft_query()[0][2]}'
    
    @reactive.Calc
    def college_query():
        stat = input.stat_select()
        conn = sqlite3.connect('nba_college.db')
        c = conn.cursor()

        cbb_averages_query = f"""
        SELECT AVG(PTS), AVG(AST), AVG(TRB), AVG(STL), AVG(BLK)
        FROM cbb
        WHERE player_name = '{input.name_select()}'
        """

        c.execute(cbb_averages_query)
        results6 = c.fetchall()
        cPTS = results6[0][0]
        cAST = results6[0][1]
        cTRB = results6[0][2]
        cSTL = results6[0][3]
        cBLK = results6[0][4]

        if stat == 'PTS':
            print(cPTS)
            return cPTS
        
        elif stat == 'AST':
            return cAST
        
        elif stat == 'REB':
            return cTRB
        
        elif stat == 'STL':
            return cSTL
        
        else:
            return cBLK
        

    @reactive.Calc
    def nba_query():
        stat = input.stat_select()
        conn = sqlite3.connect('nba_college.db')
        c = conn.cursor()
        
        nba_stats_query = f"""
        SELECT Year, PTS, AST, TRB, STL, BLK
        FROM nba
        WHERE player_name = '{input.name_select()}'
        """

        c.execute(nba_stats_query)
        results5 = c.fetchall()
        results5 = sorted(results5, key=lambda x: x[0])
        PTS = [i[1] for i in results5]
        AST = [i[2] for i in results5]
        TRB = [i[3] for i in results5]
        STL = [i[4] for i in results5]
        BLK = [i[5] for i in results5]

        if stat == 'PTS':
            return PTS
        
        elif stat == 'AST':
            return AST
        
        elif stat == 'REB':
            return TRB
        
        elif stat == 'STL':
            return STL
        
        else:
            return BLK
        

    @reactive.Calc
    def years_query():
        conn = sqlite3.connect('nba_college.db')
        c = conn.cursor()
        
        year_query = f"""
        SELECT Year
        FROM nba
        WHERE player_name = '{input.name_select()}'
        """

        c.execute(year_query)
        results5 = c.fetchall()
        results5 = sorted(results5, key=lambda x: x[0])
        years = [str(i[0]) for i in results5]

        
        return years
    
    @render_widget
    def plot():
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=years_query(), y=nba_query(), mode='lines+markers', name=f'NBA {input.stat_select()}', line=dict(width=3), marker=dict(size=10)))
        fig.add_trace(go.Scatter(x=years_query(), y=[college_query()]*len(years_query()), mode='lines', name=f'College {input.stat_select()} avg', line=dict(width=3)))
        
        fig.update_layout(
            title=f'{input.stat_select()} Comparison',
            xaxis_title='Years',
            yaxis_title=input.stat_select()
        )

        return fig













app = App(app_ui, server)


app.run()



