import pandas as pd
import panel as pn
import param

class Leaderboard(param.Parameterized):
    def __init__(self, **params):
        super().__init__(**params)
        # Initialize leaderboard data
        self.leaderboard_data = self.fetch_leaderboard_data()
        self.leaderboard_table = pn.widgets.DataFrame(self.leaderboard_data, name="Leaderboard", width=800, height=400)
        
    def fetch_leaderboard_data(self):
        # Sample data; replace with actual data fetching logic
        data = {
            "Student": ["Alice", "Bob", "Charlie"],
            "Score": [90, 85, 80]
        }
        return pd.DataFrame(data)

    def update_leaderboard(self):
        self.leaderboard_data = self.fetch_leaderboard_data()
        self.leaderboard_table.value = self.leaderboard_data

    def draw_view(self):
        return pn.Column(self.leaderboard_table)