import param
import panel as pn
import asyncio
import re
import autogen as autogen
from src.UI.avatar import avatar
import src.Agents.agents as agents
from src import globals as globals
import networkx as nx
from bokeh.plotting import figure
from bokeh.models import Circle, MultiLine, HoverTool, ColumnDataSource
from bokeh.palettes import Spectral8

class ReactiveGraphChat(param.Parameterized):
    def __init__(self, groupchat_manager=None, graph_groupchat_manager=None, **params):
        super().__init__(**params)
        
        pn.extension(design="material")
        self.groupchat_manager = groupchat_manager
        self.graph_groupchat_manager = graph_groupchat_manager
        # Learn tab
        self.GRAPH_TAB_NAME = "GraphTab"
        self.graph_tab_interface = pn.chat.ChatInterface(callback=self.a_graph_tab_callback, name=self.GRAPH_TAB_NAME)
        self.knowledge_graph_plot = pn.pane.Bokeh(sizing_mode="stretch_both")

    ############ tab1: Learn interface
    async def a_graph_tab_callback(self, contents: str, user: str, instance: pn.chat.ChatInterface):
        '''
            All panel callbacks for the learn tab come through this callback function
            Because there are two chat panels, we need to save the instance
            Then, when update is called, check the instance name
        '''                      
        if not globals.initiate_chat_task_created:
            asyncio.create_task(self.groupchat_manager.delayed_initiate_chat(agents.knowledge_tracer, self.groupchat_manager, contents))  
        else:
            if globals.input_future and not globals.input_future.done():                
                globals.input_future.set_result(contents)                 
            else:
                print("No input being awaited.")
    
    def update_graph_tab(self, recipient, messages, sender, config):
        last_content = messages[-1]['content'] 
        if all(key in messages[-1] for key in ['name']):
            self.graph_tab_interface.send(last_content, user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
        else:
            self.graph_tab_interface.send(last_content, user=recipient.name, avatar=avatar[recipient.name], respond=False)
        
        # Update knowledge graph visualization
        self.update_knowledge_graph_visualization()

    def update_knowledge_graph_visualization(self):
        # Assume self.groupchat_manager.knowledge_graph is your KnowledgeGraph instance
        G = self.groupchat_manager.knowledge_graph.graph

        # Create a layout for the graph
        pos = nx.spring_layout(G)

        # Create a Bokeh plot
        plot = figure(title="Knowledge Graph", x_range=(-1.1, 1.1), y_range=(-1.1, 1.1),
                      tools="pan,wheel_zoom,box_zoom,reset,save", sizing_mode="stretch_both")

        # Create node data
        node_xs, node_ys = zip(*pos.values())
        node_names = list(G.nodes())
        node_difficulties = [G.nodes[node]['difficulty'] for node in G.nodes()]
        node_colors = [Spectral8[difficulty % len(Spectral8)] for difficulty in node_difficulties]

        node_source = ColumnDataSource({
            'x': node_xs,
            'y': node_ys,
            'name': node_names,
            'difficulty': node_difficulties,
            'color': node_colors
        })

        # Render nodes
        nodes = plot.circle('x', 'y', size=20, source=node_source, color='color')

        # Create edge data
        edge_xs, edge_ys = [], []
        for start_node, end_node in G.edges():
            x0, y0 = pos[start_node]
            x1, y1 = pos[end_node]
            edge_xs.append([x0, x1])
            edge_ys.append([y0, y1])

        # Render edges
        plot.multi_line(edge_xs, edge_ys, line_color="#CCCCCC", line_alpha=0.8, line_width=1)

        # Add hover tool
        hover = HoverTool(tooltips=[("Topic", "@name"), ("Difficulty", "@difficulty")])
        plot.add_tools(hover)

        # Remove grid lines and axis
        plot.grid.grid_line_color = None
        plot.axis.visible = False

        # Update the knowledge graph plot
        self.knowledge_graph_plot.object = plot

    ########## Create the "windows" and draw the tabs
    def draw_view(self):         
        tabs = pn.Tabs(  
            ("Graph", pn.Column(self.graph_tab_interface, self.knowledge_graph_plot))
        )
        return tabs

    @property
    def groupchat_manager(self) ->  autogen.GroupChatManager:
        return self._groupchat_manager
    
    @groupchat_manager.setter
    def groupchat_manager(self, groupchat_manager: autogen.GroupChatManager):
        self._groupchat_manager = groupchat_manager
