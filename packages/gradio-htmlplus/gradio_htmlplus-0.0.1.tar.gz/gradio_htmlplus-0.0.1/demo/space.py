
import gradio as gr
from app import demo as app
import os

_docs = {'HTMLPlus': {'description': 'Creates a component to display arbitrary HTMLPlus output. As this component does not accept user input, it is rarely used as an input component.\n', 'members': {'__init__': {'value': {'type': 'str | Callable | None', 'default': 'None', 'description': 'The HTMLPlus content to display. Only static HTMLPlus is rendered (e.g. no JavaScript. To render JavaScript, use the `js` or `head` parameters in the `Blocks` constructor). If a function is provided, the function will be called each time the app loads to set the initial value of this component.'}, 'label': {'type': 'str | I18nData | None', 'default': 'None', 'description': 'The label for this component. Is used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.'}, 'every': {'type': 'Timer | float | None', 'default': 'None', 'description': 'Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.'}, 'inputs': {'type': 'Component | Sequence[Component] | set[Component] | None', 'default': 'None', 'description': 'Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.'}, 'show_label': {'type': 'bool', 'default': 'False', 'description': 'If True, the label will be displayed. If False, the label will be hidden.'}, 'visible': {'type': 'bool | Literal["hidden"]', 'default': 'True', 'description': 'If False, component will be hidden. If "hidden", component will be visually hidden and not take up space in the layout but still exist in the DOM'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTMLPlus DOM. Can be used for targeting CSS styles.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional list of strings that are assigned as the classes of this component in the HTMLPlus DOM. Can be used for targeting CSS styles.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.'}, 'key': {'type': 'int | str | tuple[int | str, ...] | None', 'default': 'None', 'description': "in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render."}, 'preserved_by_key': {'type': 'list[str] | str | None', 'default': '"value"', 'description': "A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor."}, 'min_height': {'type': 'int | None', 'default': 'None', 'description': 'The minimum height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If HTMLPlus content exceeds the height, the component will expand to fit the content.'}, 'max_height': {'type': 'int | None', 'default': 'None', 'description': 'The maximum height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If content exceeds the height, the component will scroll.'}, 'container': {'type': 'bool', 'default': 'False', 'description': 'If True, the HTMLPlus component will be displayed in a container. Default is False.'}, 'padding': {'type': 'bool', 'default': 'True', 'description': 'If True, the HTMLPlus component will have a certain padding (set by the `--block-padding` CSS variable) in all directions. Default is True.'}, 'autoscroll': {'type': 'bool', 'default': 'False', 'description': 'If True, will automatically scroll to the bottom of the component when the content changes, unless the user has scrolled up. If False, will not scroll to the bottom when the content changes.'}, 'selectable_elements': {'type': 'List[str] | None', 'default': 'None', 'description': "A list of CSS selectors (e.g., ['tr', '.my-button']) for elements within the HTML that are selectable. When an element matching a selector is clicked, the `select` event is triggered. The event data will contain the selector that was matched and the data from the element."}}, 'postprocess': {'value': {'type': 'str | None', 'description': 'Expects a `str` consisting of valid HTMLPlus.'}}, 'preprocess': {'return': {'type': 'str | None', 'description': '(Rarely used) passes the HTMLPlus as a `str`.'}, 'value': None}}, 'events': {'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the HTMLPlus changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'click': {'type': None, 'default': None, 'description': 'Triggered when the HTMLPlus is clicked.'}, 'select': {'type': None, 'default': None, 'description': 'Event listener for when the user selects or deselects the HTMLPlus. Uses event data gradio.SelectData to carry `value` referring to the label of the HTMLPlus, and `selected` to refer to state of the HTMLPlus. See EventData documentation on how to use this event data'}}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'HTMLPlus': []}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_htmlplus`

<div style="display: flex; gap: 7px;">
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  
</div>

Gradio HTML Advanced Component
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_htmlplus
```

## Usage

```python

import gradio as gr
import pandas as pd
import numpy as np
import uuid

# Import the custom component and the HTML generator
from gradio_htmlplus import HTMLPlus
from leaderboard import generate_leaderboard_html

# Generate Mock Data
def create_mock_leaderboard_data(num_rows=15):
    \"\"\"
    Creates a pandas DataFrame with random data for the leaderboard demo.

    Args:
        num_rows (int): The number of rows to generate.

    Returns:
        pd.DataFrame: A DataFrame containing mock leaderboard data.
    \"\"\"
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
        \"\"\"
        Handles select events from the HTMLPlus component. It differentiates actions
        based on which CSS selector was matched (evt.index).

        Args:
            evt (gr.SelectData): The event data object, containing the matched
                                 selector (`.index`) and the element's data
                                 attributes (`.value`).

        Returns:
            tuple: A tuple of values to update the output components.
                   Uses gr.skip() to avoid updating a component.
        \"\"\"
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
```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `HTMLPlus`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["HTMLPlus"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["HTMLPlus"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, (Rarely used) passes the HTMLPlus as a `str`.
- **As output:** Should return, expects a `str` consisting of valid HTMLPlus.

 ```python
def predict(
    value: str | None
) -> str | None:
    return value
```
""", elem_classes=["md-custom", "HTMLPlus-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          HTMLPlus: [], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
