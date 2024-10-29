import gradio as gr
import pandas as pd
import plotly.express as px

# Import the data
df = pd.read_csv('Train_final.csv')

# Define categorical and numeric columns for selection
# Exclude 'Customer ID' and 'Name' from categorical options
categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
categorical_columns = [col for col in categorical_columns if col not in ['Customer ID', 'Name','Credit Score']]
numeric_columns = df.select_dtypes(include=['number']).columns.tolist()

# Function to generate plots
def generate_custom_plot(credit_scores, categorical_var, numeric_var, view_freq_dist, aggregate_by, graph_type):
    dff = df.copy()
    
    # Handle "None of the Above" option
    if credit_scores == ["None of the above"]:
        credit_scores = []
    
    # Filter by Credit Score if selected
    if credit_scores:
        dff = dff[dff['Credit Score'].isin(credit_scores)]
    
    # Handle Frequency Distribution
    if view_freq_dist:
        freq_fig = px.histogram(dff, x=categorical_var, title=f"Frequency Distribution of {categorical_var}")
        freq_fig.update_layout(height=500, width=700)  # Adjusted size for frequency plot
        return freq_fig
    
    # Aggregation method
    if aggregate_by == "mean":
        aggregated_df = dff.groupby(categorical_var)[numeric_var].mean().reset_index()
    elif aggregate_by == "sum":
        aggregated_df = dff.groupby(categorical_var)[numeric_var].sum().reset_index()
    elif aggregate_by == "running sum":
        aggregated_df = dff.groupby(categorical_var)[numeric_var].sum().cumsum().reset_index()
    
    # Plotting based on selected graph type
    if graph_type == "bar chart":
        fig = px.bar(aggregated_df, x=categorical_var, y=numeric_var, title=f"{numeric_var} by {categorical_var} ({aggregate_by})")
        fig.update_traces(texttemplate='%{y}', textposition='outside')  # Add data labels
    elif graph_type == "pie chart":
        fig = px.pie(aggregated_df, names=categorical_var, values=numeric_var, title=f"{numeric_var} by {categorical_var} ({aggregate_by})")
        fig.update_traces(textinfo='percent+label')  # Add data labels
    elif graph_type == "line chart":
        fig = px.line(aggregated_df, x=categorical_var, y=numeric_var, title=f"{numeric_var} by {categorical_var} ({aggregate_by})")
        fig.update_traces(texttemplate='%{y}', textposition='top')  # Add data labels

    fig.update_layout(height=500, width=700)  # Adjusted size for output plots
    return fig

# Define Gradio Interface
interface = gr.Interface(
    fn=generate_custom_plot,
    inputs=[
        gr.CheckboxGroup(choices=["None of the above"] + df['Credit Score'].unique().tolist(), label="Select Credit Score"),
        gr.Dropdown(choices=["None of the above"] + categorical_columns, label="Select Categorical Variable"),
        gr.Dropdown(choices=["None of the above"] + numeric_columns, label="Select Numeric Variable"),
        gr.Checkbox(label="View Frequency Distribution"),
        gr.Dropdown(choices=["None of the above", "mean", "sum", "running sum"], label="Aggregate by"),
        gr.Dropdown(choices=["None of the above", "bar chart", "pie chart", "line chart"], label="Graph Type")
    ],
    outputs=gr.Plot(label="Resulting Plot"),
    title="Visualising my Customers",
    description="Plotting customer data based on user choice"
)

# Launch the interface
interface.launch()
