
import gradio as gr
import pandas as pd
import numpy as np
import uuid

# Import the custom component and the HTML generator
from gradio_htmlplus import HTMLPlus
from leaderboard import generate_leaderboard_html

# Generate Mock Data
def create_mock_leaderboard_data(num_rows=15):
    """
    Creates a pandas DataFrame with random data for the leaderboard demo.

    Args:
        num_rows (int): The number of rows to generate.

    Returns:
        pd.DataFrame: A DataFrame containing mock leaderboard data.
    """
    data = {
        'run_id': [str(uuid.uuid4()) for _ in range(num_rows)],
        'model': [f'model-v{i}-{np.random.choice(["alpha", "beta", "gamma"])}' for i in range(num_rows)],
        'agent_type': np.random.choice(['tool', 'code', 'both'], num_rows),
        'provider': np.random.choice(['litellm', 'transformers'], num_rows),
        'success_rate': np.random.uniform(40, 99.9, num_rows),
        'total_tests': np.random.randint(50, 100, num_rows),
        'avg_steps': np.random.uniform(3, 8, num_rows),
        'avg_duration_ms': np.random.uniform(1500, 5000, num_rows),
        'total_tokens': np.random.randint(10000, 50000, num_rows),
        'total_cost_usd': np.random.uniform(0.01, 0.2, num_rows),
        'co2_emissions_g': np.random.uniform(0.5, 5, num_rows),
        'gpu_utilization_avg': [np.random.uniform(60, 95) if i % 2 == 0 else None for i in range(num_rows)],
        'timestamp': pd.to_datetime(pd.Timestamp.now() - pd.to_timedelta(np.random.rand(num_rows), unit='D')),
        'submitted_by': [f'user_{np.random.randint(1, 5)}' for _ in range(num_rows)],
    }
    df = pd.DataFrame(data)
    df['successful_tests'] = (df['total_tests'] * (df['success_rate'] / 100)).astype(int)
    df['failed_tests'] = df['total_tests'] - df['successful_tests']
    return df


with gr.Blocks(css=".gradio-container { max-width: 95% !important; }") as demo:
    gr.Markdown("# 🏆 Interactive Leaderboard with Action Buttons")
    gr.Markdown("Click on any row in the table to view its complete data, or click a button for a specific action.")

    # Create and display the initial table
    leaderboard_df = create_mock_leaderboard_data(15)
    leaderboard_html = generate_leaderboard_html(leaderboard_df)

    html_table = HTMLPlus(
        value=leaderboard_html,
        # Define both the action button and the table row as selectable elements.
        # The more specific selector should come first to ensure it's matched first.
        selectable_elements=[".tm-action-button", "tr"]
    )

    clicked_data_output = gr.JSON(label="Selected Row Data")
    action_log_output = gr.Textbox(label="Action Log", interactive=False)
    
    def on_element_selected(evt: gr.SelectData):
        """
        Handles select events from the HTMLPlus component. It differentiates actions
        based on which CSS selector was matched (evt.index).

        Args:
            evt (gr.SelectData): The event data object, containing the matched
                                 selector (`.index`) and the element's data
                                 attributes (`.value`).

        Returns:
            tuple: A tuple of values to update the output components.
                   Uses gr.skip() to avoid updating a component.
        """
        if evt.index == ".tm-action-button":
            # This block handles clicks on the 'Delete' button.
            action = evt.value.get('action')
            run_id = evt.value.get('run-id') or "Unknown" 
            
            log_message = f"ACTION: Button '{action}' clicked for Run ID: {run_id[:8]}..."
            
            # Update the log, but skip updating the JSON output.
            return gr.skip(), log_message

        elif evt.index == "tr":
            # This block handles clicks on the table row itself.
            data = evt.value
            run_id = data.get('run-id') or "Unknown"
            
            log_message = f"INFO: Row selected for Run ID: {run_id[:8]}..."
            
            # The frontend sends all data attributes as strings.
            # Convert numeric strings back to numbers for cleaner display.
            numeric_keys = [
                'success-rate', 'total-tests', 'avg-steps', 'avg-duration-ms', 
                'total-tokens', 'total-cost-usd', 'co2-emissions-g', 
                'gpu-utilization-avg', 'successful-tests', 'failed-tests'
            ]
            
            for key in numeric_keys:
                if key in data and data[key] not in ['None', None, '']:
                    try:
                        num_val = float(data[key])
                        if num_val.is_integer():
                            data[key] = int(num_val)
                        else:
                            data[key] = round(num_val, 4)
                    except (ValueError, TypeError):
                        pass  # Leave as a string if conversion fails

            # Update both the JSON output and the log.
            return data, log_message
        
        # A fallback for any unexpected event.
        return gr.skip(), "Unknown action occurred."

    # Connect the 'select' event to the callback function, mapping its
    # return values to the two output components.
    html_table.select(
        fn=on_element_selected,
        inputs=None,
        outputs=[clicked_data_output, action_log_output]
    )

if __name__ == "__main__":
    demo.launch()