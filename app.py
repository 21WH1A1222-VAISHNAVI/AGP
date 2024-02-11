from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO

app = Flask(__name__)

# Assuming df is loaded from a CSV file
df = pd.read_csv('/Users/bhavithasankranthi/Downloads/flask/predicted_values.csv')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot():
    selected_test = request.form['glucema_test']
    print("Selected test input:", selected_test)

    glucema_test_lower = selected_test.lower()
    df['Glucema Test'] = df['Glucema Test'].astype(str).str.lower()

    # Merging TIR1 and TIR2 into a single TIR category
    df['TIR'] = df[['TIR1', 'TIR2']].sum(axis=1)
    selected_data = df[df['Glucema Test'] == glucema_test_lower][['TBR1', 'TBR2', 'TIR', 'TAR1', 'TAR2']]

    if selected_data.empty:
        return "No data found for Glucema Test: {}".format(selected_test)
    else:
        # Set up plot
        fig, ax = plt.subplots(figsize=(1, 6))  # Adjust the size of the plot here

        # Define bar positions
        bar_positions = np.arange(1)

        # Define colors
        colors = ['brown', 'red', 'green', 'yellow', 'orange']

        # Iterate over data columns and plot stacked bars
        y_ticks = [0]
        custom_y_labels = [0]
        for i, (col, color) in enumerate(zip(selected_data.columns, colors)):
            if col == 'TIR':
                bar_height = selected_data['TIR']
            else:
                bar_height = selected_data[col]
            bottom = np.sum(selected_data.iloc[:, :i], axis=1) if i > 0 else 0
            ax.bar(bar_positions, bar_height, label=f'{col}', bottom=bottom, color=color)
            y_ticks.append(bar_height.values[0] + y_ticks[-1])
            custom_y_labels.append(bar_height.values[0] + custom_y_labels[-1])

        # Set custom y ticks and labels
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(['0', '54', '70', '180', '250', '250+'])

        # Remove x ticks
        ax.set_xticks([])

        # Add legend outside the plot
        ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1))

        # Save the plot to a BytesIO object
        img_stream = BytesIO()
        plt.savefig(img_stream, format='png', bbox_inches='tight')  # Ensure tight layout
        img_stream.seek(0)
        img_data = base64.b64encode(img_stream.read()).decode('utf-8')

        # Close the plot to prevent memory leaks
        plt.close(fig)

        # Calculate percentages
        total = selected_data.sum(axis=1).values[0]
        high_percentage = (selected_data['TBR1'].values[0] / total) * 100
        very_high_percentage = (selected_data['TBR2'].values[0] / total) * 100
        target_percentage = (selected_data['TIR'].values[0] / total) * 100
        low_percentage = (selected_data['TAR1'].values[0] / total) * 100
        very_low_percentage = (selected_data['TAR2'].values[0] / total) * 100

        # Pass the percentages to the template
        return render_template('plot.html', img_data=img_data, high_percentage=high_percentage,
                               very_high_percentage=very_high_percentage, target_percentage=target_percentage,
                               low_percentage=low_percentage, very_low_percentage=very_low_percentage)

@app.route('/submit-remarks', methods=['POST'])
def submit_remarks():
    doctor_remarks = request.form['doctor-remarks']
    # Process the doctor remarks here if needed
    # Redirect to index route
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
