import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import altair
from pre_processing import df

# Streamlit app
st.title("Football Team Performance Dashboard")

# Display dataframe
st.write("Here is the performance data for the teams:")
st.dataframe(df.head())
