# f1_analysis_ccds

## Analysis of the 2025 Formula 1 Season: Teammate Qualifying Performance

This project provides an in-depth analysis of the 2025 Formula 1 season's qualifying sessions (Q1, Q2, and Q3). The primary focus is on comparing the performance of teammate drivers, identifying key differences in their driving across various track sections and telemetry data. By leveraging the `fastf1` library, this analysis generates insightful visualizations and data reports to highlight driver strengths and weaknesses during qualifying.

## Project Structure
├── LICENSE
├── Makefile
├── README.md
├── data
│   ├── external       <- Supporting data (e.g., team logos).
│   ├── interim        <- Transformed intermediate data.
│   ├── processed      <- Final datasets for analysis and visualization (e.g., drivers_info.csv, race_info.txt, etc).
│   └── raw            <- Original, unprocessed data (e.g., second_color.csv, login.txt).
├── docs               <- Project documentation.
├── features           <- Functions for creating analysis-specific features (e.g., 'Turn', 'faster_driver').
├── figures            <- Output visualizations (PNG files).
├── media_processing   <- tools for handling different media formats for a specific purpose (PNG files).
├── models             <- (Potentially for future predictive modeling, currently focused on descriptive analysis).
│   └── qual.py
│   └── race.py
│   └── utils          <- Collection of function needed to execute models.
├── notebooks          <- Jupyter notebooks for exploratory analysis.
│   └── *.ipynb
├── references         <- Data dictionaries, manuals, etc.
├── reports            <- Generated analysis reports (JPEG).
├── pyproject.toml     <- Project configuration.
├── requirements.txt   <- Project dependencies.
├── config.py          <- Project configuration variables.


## Qualifying Teammate Performance Analysis
This project provides a detailed comparison of teammate performance during the 2025 Formula 1 season. The analysis is divided into two main parts: Qualifying and Race.

**Qualifying Analysis**

The qualifying analysis focuses on driver performance during qualifying sessions (Q1, Q2, and Q3). Key aspects include:

* **Lap Time and Sector Time Comparison**: Tabular presentation of fastest lap times and sector times for teammates in each qualifying session.
* **Delta Time Plots**: Visualizing the time difference between teammates across the entire lap to pinpoint where time is gained or lost.
* **Speed Profile Comparison**: Comparing the speed of each teammate throughout their fastest lap, highlighting differences in straights and corners.
* **Corner Domination Analysis**: Identifying which driver has a time advantage in specific corners based on delta time analysis.
* **Throttle, Brake, and Cornering Profiles**: Comparing the percentage of lap time spent on full throttle, braking, and cornering for each driver.
* **Speed Trap Analysis:** Comparing the maximum speeds achieved by teammates at designated speed trap locations.

These analyses are conducted for each team in each qualifying session where both drivers set a valid lap time.  The results are saved as individual PNG plots and aggregated into CSV files, which are then compiled into comprehensive JPEG reports.

**Race Analysis**

The race analysis focuses on driver performance and strategy during the race. Key aspects include:
* **Lap Time Comparison**: Comparing lap times of both drivers.
* **Lap Time Scatterplot**: Showing lap times for each driver, including tyre compound information.
* **Pace Comparison**: Comparing the pace of each driver.
* **Tyre Strategy**: Visualizing the tyre compounds used by each driver during the race.
* **Pit Stop Time**: Comparing pit stop times for each driver.
* **Fastest Driver Per Lap**: Identifying the faster driver on each lap.
* **Lap Time Distribution**: Analyzing the distribution of lap times for each driver.
* **Final Gap**: Calculating the time difference between teammates at the end of the race.
* **Driver Information**: Providing key race information for each driver, including final position, gap to teammate, race time, average lap time, IQR of lap times, and pit stop information.

The results are saved as individual PNG plots and aggregated into CSV files, which are then compiled into comprehensive JPEG reports.

## Key Python Modules and Functions

The core logic of the analysis is implemented in the Python scripts within the `f1_analysis_ccds` directory:

* **`features.py`**: Contains functions to engineer features such as identifying turns (`add_turn`) and determining the faster driver in corner segments (`add_faster_driver`).
* **`utils/.../plots.py`**: Houses the visualization functions:
    * `show_driver_quali_dif_per_lap()`: Generates delta time plots.
    * `show_fastest_lap_per_quali_session()`: Creates speed profile comparisons.
    * `show_corner_advantage_per_quali_session()`: Visualizes corner advantages on the track map.
    * `create_bar_graph_per_driver()`: Generates bar charts for throttle, brake, and cornering percentages.
* **Main script (in the models folder)**: Orchestrates the analysis workflow:
    * Takes user input for the year, race number, and session type (Q or SQ).
    * Loads session data using `fastf1`.
    * Iterates through teams and qualifying sessions.
    * Calls functions from `plots.py` to generate visualizations.
    * Saves plots as PNG files in the `figures` directory.
    * Creates CSV files containing lap information and delta time data in the `csv` directory.
    * Generates PowerPoint reports (`.pptx` files) summarizing the analysis for each qualifying session, incorporating the generated plots and data.
* **Helper Functions**: Several utility functions (`read_credentials`, `rotate`, `get_corner_dist_for_drivers`, `convert_for_cmap`, `SubElement`, `_set_shape_transparency`, `Hex_RGB`) support the main analysis and presentation processes.

## Data Sources

The primary data source is the `fastf1` Python library, which provides access to Formula 1 data. Additional data sources include:

* **`data/external/team_logos/`**: For team logos in the PowerPoint reports.
* **`data/raw/second_color.csv`**: Maps F1 teams to secondary colors for visualizations.
* **`data/raw/login.txt`**: (Not intended for public repository) Contains credentials for potential Instagram posting functionality.

## Output and Reporting

The results of the analysis are presented through:

1.  **PNG Visualizations**: A collection of plots for each team and qualifying session, including delta time graphs, speed profiles, corner dominance maps, and throttle/brake/cornering bar charts.
2.  **CSV Data**: Detailed lap information and delta time data are saved in CSV files for further inspection or use in other tools.
3.  **JPEG Reports**: Automatically generated `.jpeg` reports for each qualifying session. Each report focuses on a specific team and includes:
    * Team logo and driver names.
    * Summary of lap and sector time differences.
    * Delta time plot.
    * Speed profile comparison.
    * Corner domination visualization.
    * Throttle, brake, and cornering bar charts.

## Potential Future Enhancements

* Integration of more detailed telemetry data (e.g., steering angle, gear changes, DRS usage).
* Development of predictive models for qualifying performance.
* Extension of the analysis to practice sessions, including best tyre strategy and prediction based on previous data.

This project provides a robust framework for analyzing Formula 1 qualifying performance and offers numerous avenues for future expansion and more sophisticated analysis.
