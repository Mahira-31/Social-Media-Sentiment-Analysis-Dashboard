"""
Social Media Sentiment Analysis Dashboard

A dashboard for analyzing sentiment data across different social media platforms.
This application provides visualization and analysis tools for understanding sentiment patterns.

To run the application:
1. Make sure you have Python 3 and required libraries (pandas, matplotlib, numpy, tkinter)
2. Execute: python3 m.py

The application will generate sample data automatically.
You can also load your own data using the "Load Dataset" button.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import threading
import os
import platform
import sys

# Suppress the deprecation warning for macOS Tk
if platform.system() == 'Darwin':
    os.environ['TK_SILENCE_DEPRECATION'] = '1'

# Debug info
print(f"Python version: {sys.version}")
print(f"Tkinter version: {tk.TkVersion}")
print(f"Operating system: {platform.system()} {platform.release()}")
print(f"Working directory: {os.getcwd()}")

# Check for required packages
required_packages = ["pandas", "matplotlib", "numpy"]
for package in required_packages:
    try:
        __import__(package)
        print(f"{package} is installed")
    except ImportError:
        print(f"ERROR: {package} is not installed")

class SentimentDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Social Media Sentiment Analysis Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f5f5f5")
        
        # Set app theme - removed MacWindowStyle call as it caused issues
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configure styles
        self.style.configure("TFrame", background="#f5f5f5")
        self.style.configure("Header.TLabel", background="#4a6fa5", foreground="white", font=("Helvetica", 16, "bold"), padding=10)
        self.style.configure("TLabel", background="#f5f5f5", font=("Helvetica", 12))
        self.style.configure("Stats.TLabel", background="#ffffff", font=("Helvetica", 13), padding=5)
        self.style.configure("TButton", font=("Helvetica", 12), padding=5)
        self.style.configure("TNotebook", background="#f5f5f5", tabposition="n")
        self.style.configure("TNotebook.Tab", background="#d9d9d9", foreground="black", padding=[10, 5], font=("Helvetica", 12))
        self.style.map("TNotebook.Tab", background=[("selected", "#4a6fa5")], foreground=[("selected", "white")])
        
        # Variables
        self.df = None
        self.current_filter = "All"
        self.platforms = []
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Create header
        self.create_header()
        
        # Create content area with notebook
        self.create_notebook()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. Please load a dataset.")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Try to load dataset automatically
        try:
            self.load_default_dataset()
        except Exception as e:
            print(f"Could not load default dataset: {e}")
    
    def create_header(self):
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Dashboard title
        title_label = ttk.Label(header_frame, text="Social Media Sentiment Analysis", style="Header.TLabel")
        title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Buttons frame
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side=tk.RIGHT, padx=5)
        
        # Load data button
        load_btn = ttk.Button(btn_frame, text="Load Dataset", command=self.load_data)
        load_btn.pack(side=tk.LEFT, padx=5)
        
        # Refresh button
        refresh_btn = ttk.Button(btn_frame, text="Refresh", command=self.refresh_dashboard)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Help button
        help_btn = ttk.Button(btn_frame, text="Help", command=self.show_help)
        help_btn.pack(side=tk.LEFT, padx=5)
    
    def create_notebook(self):
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Overview tab
        self.overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text="Overview")
        
        # Detailed Analysis tab
        self.analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_frame, text="Detailed Analysis")
        
        # Data Explorer tab
        self.explorer_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.explorer_frame, text="Data Explorer")
        
        # Set up overview tab
        self.setup_overview_tab()
        
        # Set up analysis tab
        self.setup_analysis_tab()
        
        # Set up explorer tab
        self.setup_explorer_tab()
    
    def setup_overview_tab(self):
        # Left column - stats
        stats_frame = ttk.Frame(self.overview_frame)
        stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Filter frame
        filter_frame = ttk.LabelFrame(stats_frame, text="Filter by Platform")
        filter_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
        
        self.platform_var = tk.StringVar(value="All")
        
        # Will populate this when we load data
        self.platform_dropdown = ttk.Combobox(filter_frame, textvariable=self.platform_var, state="readonly")
        self.platform_dropdown.pack(fill=tk.X, padx=10, pady=10)
        self.platform_dropdown.bind("<<ComboboxSelected>>", self.filter_changed)
        
        # Stats cards
        stats_container = ttk.Frame(stats_frame)
        stats_container.pack(fill=tk.BOTH, expand=True)
        
        # Create stats cards
        self.create_stat_card(stats_container, "Total Posts", "total_posts", 0)
        self.create_stat_card(stats_container, "Positive Sentiment", "positive_count", 0, "#4CAF50")
        self.create_stat_card(stats_container, "Neutral Sentiment", "neutral_count", 0, "#FFC107")
        self.create_stat_card(stats_container, "Negative Sentiment", "negative_count", 0, "#F44336")
        
        # Right column - charts
        charts_frame = ttk.Frame(self.overview_frame)
        charts_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create charts placeholder frames
        pie_frame = ttk.LabelFrame(charts_frame, text="Sentiment Distribution")
        pie_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.pie_placeholder = ttk.Label(pie_frame, text="Chart will appear here after loading data")
        self.pie_placeholder.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        platform_frame = ttk.LabelFrame(charts_frame, text="Platform Comparison")
        platform_frame.pack(fill=tk.BOTH, expand=True)
        self.platform_placeholder = ttk.Label(platform_frame, text="Chart will appear here after loading data")
        self.platform_placeholder.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_stat_card(self, parent, title, key, value, color="#4a6fa5"):
        card = ttk.Frame(parent, style="TFrame")
        card.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = ttk.Label(card, text=title, font=("Helvetica", 12))
        title_label.pack(anchor=tk.W, padx=10, pady=(10, 0))
        
        # Value with colored indicator
        value_frame = ttk.Frame(card)
        value_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Create a style for this specific indicator
        style_name = f"{key.capitalize()}.TFrame"
        self.style.configure(style_name, background=color)
        
        indicator = ttk.Frame(value_frame, width=5, height=30, style=style_name)
        indicator.pack(side=tk.LEFT, padx=(0, 10))
        
        value_var = tk.StringVar(value=str(value))
        setattr(self, f"{key}_var", value_var)
        value_label = ttk.Label(value_frame, textvariable=value_var, font=("Helvetica", 18, "bold"))
        value_label.pack(side=tk.LEFT)
        
        # Store references to update later
        setattr(self, f"{key}_indicator", indicator)
        setattr(self, f"{key}_color", color)
    
    def setup_analysis_tab(self):
        # Top filters and controls
        control_frame = ttk.Frame(self.analysis_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Left side - platforms
        platform_frame = ttk.LabelFrame(control_frame, text="Select Platforms")
        platform_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.platform_vars = {}
        self.platform_checkboxes_frame = ttk.Frame(platform_frame)
        self.platform_checkboxes_frame.pack(fill=tk.BOTH, padx=10, pady=10)
        
        # Right side - sentiment filter
        sentiment_frame = ttk.LabelFrame(control_frame, text="Filter by Sentiment")
        sentiment_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        self.sentiment_var = tk.StringVar(value="All")
        sentiments = ["All", "Positive", "Neutral", "Negative"]
        
        for sentiment in sentiments:
            rb = ttk.Radiobutton(sentiment_frame, text=sentiment, value=sentiment, variable=self.sentiment_var, command=self.update_analysis_charts)
            rb.pack(anchor=tk.W, padx=10, pady=5)
        
        # Bottom - charts
        charts_container = ttk.Frame(self.analysis_frame)
        charts_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create sentiment trend chart frame
        trend_frame = ttk.LabelFrame(charts_container, text="Sentiment Trends Over Time")
        trend_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.trend_placeholder = ttk.Label(trend_frame, text="Chart will appear here after loading data")
        self.trend_placeholder.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create word frequency chart frame
        word_frame = ttk.LabelFrame(charts_container, text="Common Words by Sentiment")
        word_frame.pack(fill=tk.BOTH, expand=True)
        
        self.word_placeholder = ttk.Label(word_frame, text="Chart will appear here after loading data")
        self.word_placeholder.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_explorer_tab(self):
        # Controls at top
        control_frame = ttk.Frame(self.explorer_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Search field
        search_label = ttk.Label(control_frame, text="Search:")
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind("<Return>", lambda event: self.search_data())
        
        search_btn = ttk.Button(control_frame, text="Search", command=self.search_data)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(control_frame, text="Clear", command=self.clear_search)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Platform Filter
        platform_filter_frame = ttk.Frame(control_frame)
        platform_filter_frame.pack(side=tk.LEFT, padx=20)
        
        platform_label = ttk.Label(platform_filter_frame, text="Platform:")
        platform_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.explorer_platform_var = tk.StringVar(value="All")
        self.explorer_platform_combo = ttk.Combobox(platform_filter_frame, textvariable=self.explorer_platform_var, state="readonly", width=15)
        self.explorer_platform_combo.pack(side=tk.LEFT, padx=5)
        self.explorer_platform_combo.bind("<<ComboboxSelected>>", self.filter_explorer_data)
        
        # Export button on the right
        export_btn = ttk.Button(control_frame, text="Export Data", command=self.export_data)
        export_btn.pack(side=tk.RIGHT, padx=5)
        
        # Table view
        table_frame = ttk.Frame(self.explorer_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create Treeview for data display
        columns = ("id", "platform", "sentiment", "text", "user", "timestamp", "country", "hashtags")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Pre-configure tags for sentiment colors
        self.tree.tag_configure("positive", background="#e8f5e9")
        self.tree.tag_configure("neutral", background="#fff8e1")
        self.tree.tag_configure("negative", background="#ffebee")
        
        # Set column headings
        self.tree.heading("id", text="ID", command=lambda: self.treeview_sort_column("id", False))
        self.tree.heading("platform", text="Platform", command=lambda: self.treeview_sort_column("platform", False))
        self.tree.heading("sentiment", text="Sentiment", command=lambda: self.treeview_sort_column("sentiment", False))
        self.tree.heading("text", text="Text")
        self.tree.heading("user", text="User", command=lambda: self.treeview_sort_column("user", False))
        self.tree.heading("timestamp", text="Date/Time", command=lambda: self.treeview_sort_column("timestamp", False))
        self.tree.heading("country", text="Country", command=lambda: self.treeview_sort_column("country", False))
        self.tree.heading("hashtags", text="Hashtags")
        
        # Set column widths
        self.tree.column("id", width=50, minwidth=50)
        self.tree.column("platform", width=80, minwidth=80)
        self.tree.column("sentiment", width=80, minwidth=80)
        self.tree.column("text", width=300, minwidth=200)
        self.tree.column("user", width=100, minwidth=80)
        self.tree.column("timestamp", width=150, minwidth=120)
        self.tree.column("country", width=80, minwidth=80)
        self.tree.column("hashtags", width=150, minwidth=100)
        
        # Enable item selection with double-click to show details
        self.tree.bind("<Double-1>", self.show_item_details)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=y_scrollbar.set)
        
        x_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=x_scrollbar.set)
        
        # Pack everything
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status bar for data info
        self.data_info_var = tk.StringVar()
        self.data_info_var.set("No data loaded")
        data_info_label = ttk.Label(self.explorer_frame, textvariable=self.data_info_var, anchor=tk.W)
        data_info_label.pack(fill=tk.X, padx=10, pady=5)
    
    def load_default_dataset(self):
        """Try to load the dataset from common locations"""
        self.status_var.set("Attempting to load default dataset...")
        
        try:
            # Generate sample data immediately
            self.status_var.set("Generating sample data for demonstration...")
            df = generate_sample_data()
            self.df = df
            self.process_data()
            self.status_var.set("Sample data generated successfully!")
        except Exception as e:
            self.status_var.set(f"Error loading dataset: {e}")
            
    def load_data(self):
        """Load dataset from file"""
        file_path = filedialog.askopenfilename(
            title="Select Dataset",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Show loading message
            self.status_var.set("Loading dataset...")
            self.root.update()
            
            # Load in a separate thread
            def load_thread():
                try:
                    df = pd.read_csv(file_path)
                    self.df = df
                    
                    # Update UI in main thread
                    self.root.after(0, self.data_loaded)
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load dataset: {e}"))
                    self.root.after(0, lambda: self.status_var.set("Error loading dataset."))
            
            threading.Thread(target=load_thread).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dataset: {e}")
            self.status_var.set("Error loading dataset.")
    
    def data_loaded(self):
        """Called when data is successfully loaded"""
        self.status_var.set(f"Dataset loaded with {len(self.df)} records.")
        self.process_data()
    
    def process_data(self):
        """Process the loaded data and update UI"""
        if self.df is None:
            return
        
        # Basic data cleanup
        # Column mapping specific to the sentimentdataset.csv format
        column_mapping = {
            'Text': 'text',
            'Sentiment': 'sentiment',
            'Platform': 'platform',
            'Timestamp': 'timestamp',
            'User': 'user',
            'Hashtags': 'hashtags',
            'Retweets': 'retweets',
            'Likes': 'likes',
            'Country': 'country',
            'Year': 'year',
            'Month': 'month',
            'Day': 'day',
            'Hour': 'hour'
        }
        
        # Check if we have the correct columns and rename them
        for old_col, new_col in column_mapping.items():
            if old_col in self.df.columns:
                self.df.rename(columns={old_col: new_col}, inplace=True)
        
        # If we still don't have our required columns, try to infer them
        expected_columns = ["text", "sentiment", "platform"]
        if not all(col in self.df.columns for col in expected_columns):
            cols = list(self.df.columns)
            
            # Check for columns with similar names
            for col in cols:
                # Look for Text-like columns
                if any(keyword in col.lower() for keyword in ['text', 'content', 'message']):
                    self.df.rename(columns={col: 'text'}, inplace=True)
                # Look for Sentiment-like columns
                elif any(keyword in col.lower() for keyword in ['sentiment', 'emotion', 'feeling']):
                    self.df.rename(columns={col: 'sentiment'}, inplace=True)
                # Look for Platform-like columns
                elif any(keyword in col.lower() for keyword in ['platform', 'source', 'media']):
                    self.df.rename(columns={col: 'platform'}, inplace=True)
        
        # Add ID column if not present
        if "id" not in self.df.columns:
            self.df["id"] = range(1, len(self.df) + 1)
        
        # Clean up text data
        if 'text' in self.df.columns:
            self.df['text'] = self.df['text'].astype(str).str.strip()
        
        # Normalize sentiment values
        if 'sentiment' in self.df.columns:
            # Map various sentiment values to standard ones
            sentiment_mapping = {
                'positive': 'Positive',
                'neutral': 'Neutral',
                'negative': 'Negative',
                'pos': 'Positive',
                'neu': 'Neutral',
                'neg': 'Negative',
                'joy': 'Positive',
                'happy': 'Positive',
                'sad': 'Negative',
                'anger': 'Negative',
                'fear': 'Negative',
                'surprise': 'Neutral',
                'excitement': 'Positive',
                'happiness': 'Positive',
                'love': 'Positive',
                'adoration': 'Positive',
                'amusement': 'Positive',
                'anxiety': 'Negative',
                'contempt': 'Negative',
                'disappointment': 'Negative',
                'disgust': 'Negative',
                'grief': 'Negative',
                'loneliness': 'Negative',
                'confusion': 'Neutral',
                'curiosity': 'Neutral',
                'indifference': 'Neutral'
            }
            
            # Apply mapping for case-insensitive matching
            self.df['sentiment'] = self.df['sentiment'].astype(str).str.strip().str.lower()
            self.df['sentiment'] = self.df['sentiment'].apply(
                lambda x: next((sentiment_mapping[k] for k in sentiment_mapping if k in x.lower()), 
                               'Positive' if any(pos in x.lower() for pos in ['elation', 'happiness', 'joy', 'contentment', 'grateful', 'enthusiasm', 'fulfillment']) else
                               'Negative' if any(neg in x.lower() for neg in ['despair', 'grief', 'bitter', 'frustration', 'angry', 'shame', 'regret', 'envy']) else
                               'Neutral'))
        
        # Get list of unique platforms
        self.platforms = ["All"] + sorted(self.df["platform"].unique().tolist())
        
        # Update platform dropdowns
        self.platform_dropdown["values"] = self.platforms
        self.platform_dropdown.current(0)
        
        # Update Explorer platform dropdown
        self.explorer_platform_combo["values"] = self.platforms
        self.explorer_platform_combo.current(0)
        
        # Clear and recreate platform checkboxes
        for widget in self.platform_checkboxes_frame.winfo_children():
            widget.destroy()
        
        self.platform_vars = {}
        for platform in self.platforms[1:]:  # Skip 'All'
            var = tk.BooleanVar(value=True)
            self.platform_vars[platform] = var
            cb = ttk.Checkbutton(self.platform_checkboxes_frame, text=platform, variable=var, command=self.update_analysis_charts)
            cb.pack(anchor=tk.W, padx=5, pady=2)
        
        # Update all visuals
        self.update_stats()
        self.update_overview_charts()
        self.update_analysis_charts()
        self.populate_data_table()
    
    def filter_changed(self, event=None):
        """Handle platform filter change"""
        self.current_filter = self.platform_var.get()
        self.update_stats()
        self.update_overview_charts()
    
    def update_stats(self):
        """Update statistics cards"""
        if self.df is None:
            return
        
        filtered_df = self.df
        if self.current_filter != "All":
            filtered_df = self.df[self.df["platform"] == self.current_filter]
        
        # Update total posts
        total = len(filtered_df)
        self.total_posts_var.set(str(total))
        
        # Count by sentiment
        positive = len(filtered_df[filtered_df["sentiment"] == "Positive"])
        neutral = len(filtered_df[filtered_df["sentiment"] == "Neutral"])
        negative = len(filtered_df[filtered_df["sentiment"] == "Negative"])
        
        # Update sentiment counts
        self.positive_count_var.set(str(positive))
        self.neutral_count_var.set(str(neutral))
        self.negative_count_var.set(str(negative))
        
        # Update indicator colors - ttk.Frame needs style configuration
        # Create or update styles for each indicator
        self.style.configure("Total.TFrame", background="#4a6fa5")
        self.style.configure("Positive.TFrame", background="#4CAF50")
        self.style.configure("Neutral.TFrame", background="#FFC107")
        self.style.configure("Negative.TFrame", background="#F44336")
        
        # Apply the styles
        self.total_posts_indicator.configure(style="Total.TFrame")
        self.positive_count_indicator.configure(style="Positive.TFrame")
        self.neutral_count_indicator.configure(style="Neutral.TFrame")
        self.negative_count_indicator.configure(style="Negative.TFrame")
    
    def update_overview_charts(self):
        """Update charts on overview tab"""
        if self.df is None:
            return
        
        # Get filtered data
        filtered_df = self.df
        if self.current_filter != "All":
            filtered_df = self.df[self.df["platform"] == self.current_filter]
        
        # Clear previous charts
        for widget in self.pie_placeholder.master.winfo_children():
            widget.destroy()
        
        for widget in self.platform_placeholder.master.winfo_children():
            widget.destroy()
        
        # Create sentiment distribution pie chart
        sentiment_counts = filtered_df["sentiment"].value_counts()
        
        fig1, ax1 = plt.subplots(figsize=(5, 4), dpi=100)
        colors = ["#4CAF50", "#FFC107", "#F44336"]
        explode = (0.1, 0, 0)  # explode the 1st slice
        
        # Make sure we have all sentiments in the plot even if count is 0
        data = [
            sentiment_counts.get("Positive", 0),
            sentiment_counts.get("Neutral", 0),
            sentiment_counts.get("Negative", 0)
        ]
        
        labels = ["Positive", "Neutral", "Negative"]
        # Add percentages to the labels
        total = sum(data)
        if total > 0:
            percentages = [(count / total) * 100 for count in data]
            labels = [f"{label} ({count}, {percentage:.1f}%)" for label, count, percentage in zip(labels, data, percentages)]
        
        if sum(data) > 0:  # Only create pie chart if we have data
            ax1.pie(data, explode=explode, labels=labels,
                    autopct='%1.1f%%', shadow=True, startangle=90, colors=colors)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        else:
            ax1.text(0.5, 0.5, "No data available", horizontalalignment='center', verticalalignment='center', transform=ax1.transAxes)
            ax1.axis('off')
        
        pie_canvas = FigureCanvasTkAgg(fig1, master=self.pie_placeholder.master)
        pie_canvas.draw()
        pie_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create platform comparison chart
        if self.current_filter == "All":
            # Calculate sentiment by platform
            platform_sentiments = {}
            valid_platforms = sorted(self.df["platform"].unique())
            
            for platform in valid_platforms:
                platform_df = self.df[self.df["platform"] == platform]
                sentiment_counts = platform_df["sentiment"].value_counts()
                platform_sentiments[platform] = [
                    sentiment_counts.get("Positive", 0),
                    sentiment_counts.get("Neutral", 0),
                    sentiment_counts.get("Negative", 0)
                ]
            
            # Filter out platforms with no data
            platform_sentiments = {k: v for k, v in platform_sentiments.items() if sum(v) > 0}
            
            if platform_sentiments:
                # Convert to percentages for better comparison
                for platform in platform_sentiments:
                    total = sum(platform_sentiments[platform])
                    if total > 0:
                        platform_sentiments[platform] = [(count / total) * 100 for count in platform_sentiments[platform]]
                
                # Create grouped bar chart
                fig2, ax2 = plt.subplots(figsize=(8, 4), dpi=100)
                
                x = np.arange(len(platform_sentiments))
                width = 0.2
                
                # Plot bars for each sentiment
                positive_bars = ax2.bar(x - width, [platform_sentiments[p][0] for p in platform_sentiments], width, label='Positive', color='#4CAF50')
                neutral_bars = ax2.bar(x, [platform_sentiments[p][1] for p in platform_sentiments], width, label='Neutral', color='#FFC107')
                negative_bars = ax2.bar(x + width, [platform_sentiments[p][2] for p in platform_sentiments], width, label='Negative', color='#F44336')
                
                # Add labels, title and custom x-axis tick labels
                ax2.set_ylabel('Percentage')
                ax2.set_title('Sentiment Distribution by Platform')
                ax2.set_xticks(x)
                ax2.set_xticklabels(platform_sentiments.keys())
                ax2.legend()
                
                # Add data labels on bars
                def autolabel(rects):
                    """Attach a text label above each bar in rects, displaying its height."""
                    for rect in rects:
                        height = rect.get_height()
                        ax2.annotate(f'{height:.1f}%',
                                    xy=(rect.get_x() + rect.get_width() / 2, height),
                                    xytext=(0, 3),  # 3 points vertical offset
                                    textcoords="offset points",
                                    ha='center', va='bottom', fontsize=8)
                
                autolabel(positive_bars)
                autolabel(neutral_bars)
                autolabel(negative_bars)
                
                # Add value counts to the legend
                handles, labels = ax2.get_legend_handles_labels()
                platform_totals = {}
                for platform in platform_sentiments:
                    platform_df = self.df[self.df["platform"] == platform]
                    platform_totals[platform] = len(platform_df)
                
                # Add total count to the title
                total_posts = sum(platform_totals.values())
                ax2.set_title(f'Sentiment Distribution by Platform (Total: {total_posts} posts)')
                
                # Add platform count labels
                for i, platform in enumerate(platform_sentiments):
                    ax2.text(i, -5, f"n={platform_totals[platform]}", ha='center', fontsize=8)
                
                # Adjust y-axis to make room for platform count labels
                ax2.set_ylim(bottom=-8)
                
                # Adjust layout
                fig2.tight_layout()
                
                platform_canvas = FigureCanvasTkAgg(fig2, master=self.platform_placeholder.master)
                platform_canvas.draw()
                platform_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            else:
                # Display message if no platforms to compare
                ttk.Label(self.platform_placeholder.master, text="No platform data available for comparison").pack(fill=tk.BOTH, expand=True)
        else:
            # Display message that platform comparison is only available when "All" platforms are selected
            ttk.Label(self.platform_placeholder.master, text=f"Platform comparison available when 'All' platforms are selected\nCurrently showing data for: {self.current_filter}").pack(fill=tk.BOTH, expand=True)
    
    def update_analysis_charts(self):
        """Update charts on analysis tab"""
        if self.df is None:
            return
        
        # Filter by selected platforms
        selected_platforms = [platform for platform, var in self.platform_vars.items() if var.get()]
        if not selected_platforms:
            df_filtered = pd.DataFrame()  # Empty dataframe if no platforms selected
        else:
            df_filtered = self.df[self.df["platform"].isin(selected_platforms)].copy()  # Use copy() to avoid warnings
        
        # Apply sentiment filter if needed
        sentiment_filter = self.sentiment_var.get()
        if sentiment_filter != "All":
            df_filtered = df_filtered[df_filtered["sentiment"] == sentiment_filter].copy()
        
        # Clear previous charts
        for widget in self.trend_placeholder.master.winfo_children():
            widget.destroy()
        
        for widget in self.word_placeholder.master.winfo_children():
            widget.destroy()
        
        if df_filtered.empty:
            ttk.Label(self.trend_placeholder.master, text="No data available for selected filters").pack()
            ttk.Label(self.word_placeholder.master, text="No data available for selected filters").pack()
            return
        
        # Create trend chart using timestamp data if available
        fig1, ax1 = plt.subplots(figsize=(8, 4), dpi=100)
        
        # Check if we have timestamp data
        has_timestamp = 'timestamp' in df_filtered.columns
        has_date_components = all(col in df_filtered.columns for col in ['year', 'month', 'day'])
        
        if has_timestamp or has_date_components:
            # Prepare time-based data
            if has_timestamp:
                # Convert timestamp to datetime if it's not already
                if not pd.api.types.is_datetime64_dtype(df_filtered['timestamp']):
                    df_filtered.loc[:, 'date'] = pd.to_datetime(df_filtered['timestamp'], errors='coerce')
                else:
                    df_filtered.loc[:, 'date'] = df_filtered['timestamp']
            elif has_date_components:
                # Create date from year, month, day components
                df_filtered.loc[:, 'date'] = pd.to_datetime(
                    df_filtered[['year', 'month', 'day']].astype(str).agg('-'.join, axis=1), 
                    errors='coerce'
                )
            
            # Group by date and platform, count sentiments
            df_filtered.loc[:, 'year_month'] = df_filtered['date'].dt.strftime('%Y-%m')
            
            # For each platform, create sentiment trend lines
            platform_colors = {
                'Twitter': '#1DA1F2',  # Twitter blue
                'Facebook': '#4267B2',  # Facebook blue
                'Instagram': '#E1306C',  # Instagram pink/purple
            }
            
            # Default colors for other platforms
            default_colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#a4de6c']
            
            # Prepare data for line chart
            for i, platform in enumerate(selected_platforms):
                platform_df = df_filtered[df_filtered['platform'] == platform]
                
                if platform_df.empty:
                    continue
                
                # Get sentiment counts by month
                sentiment_trends = {}
                
                # Get unique months in chronological order
                time_points = sorted(platform_df['year_month'].unique())
                
                if not time_points:
                    continue
                
                # For each sentiment, get counts per month
                sentiments_to_plot = ['Positive', 'Neutral', 'Negative'] if sentiment_filter == 'All' else [sentiment_filter]
                
                for sentiment in sentiments_to_plot:
                    monthly_counts = []
                    
                    for month in time_points:
                        month_data = platform_df[platform_df['year_month'] == month]
                        sentiment_count = len(month_data[month_data['sentiment'] == sentiment])
                        total_count = len(month_data)
                        percentage = (sentiment_count / total_count * 100) if total_count > 0 else 0
                        monthly_counts.append(percentage)
                    
                    sentiment_trends[sentiment] = monthly_counts
                
                # Plot lines with appropriate colors
                platform_color = platform_colors.get(platform, default_colors[i % len(default_colors)])
                line_styles = ['-', '--', '-.']
                
                for j, sentiment in enumerate(sentiments_to_plot):
                    if sentiment == 'Positive':
                        color = '#4CAF50'  # Green
                    elif sentiment == 'Neutral':
                        color = '#FFC107'  # Amber
                    elif sentiment == 'Negative':
                        color = '#F44336'  # Red
                    else:
                        color = default_colors[j % len(default_colors)]
                    
                    line_style = line_styles[j % len(line_styles)]
                    
                    # Plot the line
                    ax1.plot(
                        time_points, 
                        sentiment_trends[sentiment], 
                        line_style, 
                        label=f"{platform} {sentiment}", 
                        color=color,
                        marker='o',
                        markersize=4
                    )
        else:
            # Fallback to simulated data if no timestamp info
            import random
            time_points = 10
            sentiment_trends = {}
            
            # Generate data points for each platform
            for platform in selected_platforms:
                platform_df = self.df[self.df["platform"] == platform]
                total = len(platform_df)
                
                # Generate points with some randomness but trending toward actual distribution
                pos_pct = len(platform_df[platform_df["sentiment"] == "Positive"]) / total if total > 0 else 0.33
                neu_pct = len(platform_df[platform_df["sentiment"] == "Neutral"]) / total if total > 0 else 0.33
                neg_pct = len(platform_df[platform_df["sentiment"] == "Negative"]) / total if total > 0 else 0.33
                
                # Create trends with randomness
                pos_trend = [(pos_pct * 100) * (0.85 + random.random() * 0.3) for _ in range(time_points)]
                neu_trend = [(neu_pct * 100) * (0.85 + random.random() * 0.3) for _ in range(time_points)]
                neg_trend = [(neg_pct * 100) * (0.85 + random.random() * 0.3) for _ in range(time_points)]
                
                sentiment_trends[platform] = {
                    "Positive": pos_trend,
                    "Neutral": neu_trend,
                    "Negative": neg_trend
                }
            
            # Plot lines
            x = range(1, time_points + 1)
            line_styles = ['-', '--', '-.', ':']
            colors = {"Positive": "#4CAF50", "Neutral": "#FFC107", "Negative": "#F44336"}
            
            for i, platform in enumerate(selected_platforms):
                ls = line_styles[i % len(line_styles)]
                
                # Plot each sentiment if not filtered
                if sentiment_filter == "All" or sentiment_filter == "Positive":
                    ax1.plot(x, sentiment_trends[platform]["Positive"], ls, label=f"{platform} Positive", color="#4CAF50")
                
                if sentiment_filter == "All" or sentiment_filter == "Neutral":
                    ax1.plot(x, sentiment_trends[platform]["Neutral"], ls, label=f"{platform} Neutral", color="#FFC107")
                
                if sentiment_filter == "All" or sentiment_filter == "Negative":
                    ax1.plot(x, sentiment_trends[platform]["Negative"], ls, label=f"{platform} Negative", color="#F44336")
        
        # Add labels and legend
        ax1.set_xlabel('Time Period')
        ax1.set_ylabel('Percentage')
        ax1.set_title('Sentiment Trends Over Time')
        ax1.legend(loc='best')
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Add data points
        trend_canvas = FigureCanvasTkAgg(fig1, master=self.trend_placeholder.master)
        trend_canvas.draw()
        trend_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create word frequency chart by sentiment
        from collections import Counter
        import re
        
        # Text processing function
        def process_text(text):
            if not isinstance(text, str):
                return []
            words = re.sub(r'[^\w\s]', '', text.lower()).split()
            stop_words = {'the', 'and', 'is', 'in', 'it', 'to', 'that', 'of', 'a', 'for', 'on', 'with', 'as', 'this', 
                         'at', 'by', 'an', 'be', 'are', 'from', 'has', 'have', 'had', 'was', 'were', 'will', 'would',
                         'could', 'should', 'can', 'may', 'might', 'must', 'im', 'ive', 'youre', 'hes', 'shes', 'theyre',
                         'weve', 'theyve', 'dont', 'doesnt', 'didnt', 'hasnt', 'havent', 'couldnt', 'wouldnt', 'shouldnt'}
            return [word for word in words if word not in stop_words and len(word) > 2]
        
        # Process words by sentiment
        sentiment_words = {"Positive": [], "Neutral": [], "Negative": []}
        
        for _, row in df_filtered.iterrows():
            words = process_text(row["text"])
            sentiment = row["sentiment"]
            if sentiment in sentiment_words:
                sentiment_words[sentiment].extend(words)
        
        # Get top words for each sentiment
        top_words = {}
        n_words = 10  # Number of top words to show
        
        for sentiment, words in sentiment_words.items():
            if sentiment_filter == "All" or sentiment == sentiment_filter:
                if words:
                    top_words[sentiment] = Counter(words).most_common(n_words)
                else:
                    top_words[sentiment] = []
        
        # Create word frequency chart
        fig2, ax2 = plt.subplots(figsize=(8, 4), dpi=100)
        
        # Plot horizontal bars for each sentiment
        colors = {"Positive": "#4CAF50", "Neutral": "#FFC107", "Negative": "#F44336"}
        bars_per_sentiment = n_words
        y_offset = 0
        y_ticks = []
        y_labels = []
        
        for sentiment in ["Positive", "Neutral", "Negative"]:
            if sentiment not in top_words:
                continue
                
            words_counts = top_words[sentiment]
            if not words_counts:
                continue
                
            y_positions = range(y_offset, y_offset + len(words_counts))
            word_counts = [count for _, count in words_counts]
            words = [word for word, _ in words_counts]
            
            # Plot bars
            ax2.barh(y_positions, word_counts, align='center', color=colors[sentiment], 
                     alpha=0.8, label=sentiment)
            
            # Update y-ticks
            y_ticks.extend(y_positions)
            y_labels.extend([f"{word} ({sentiment})" for word in words])
            
            # Update offset for next sentiment
            y_offset += len(words_counts) + 1  # +1 for spacing between sentiment groups
        
        # Set y-ticks and labels
        ax2.set_yticks(y_ticks)
        ax2.set_yticklabels(y_labels)
        
        # Add labels and legend
        ax2.set_xlabel('Frequency')
        ax2.set_title('Most Common Words by Sentiment')
        ax2.legend(loc='lower right')
        
        # Adjust layout
        fig2.tight_layout()
        
        word_canvas = FigureCanvasTkAgg(fig2, master=self.word_placeholder.master)
        word_canvas.draw()
        word_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def populate_data_table(self):
        """Populate data explorer table with data"""
        if self.df is None:
            return
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Use our helper method to populate the table
        self.populate_explorer_with_data(self.df)
        
        # Update info label
        total_count = len(self.df)
        platform_counts = self.df["platform"].value_counts().to_dict()
        sentiment_counts = self.df["sentiment"].value_counts().to_dict()
        
        platform_str = ", ".join([f"{platform}: {count}" for platform, count in platform_counts.items()])
        sentiment_str = ", ".join([f"{sentiment}: {count}" for sentiment, count in sentiment_counts.items()])
        
        self.data_info_var.set(f"Total records: {total_count} | Platforms: {platform_str} | Sentiments: {sentiment_str}")
    
    def search_data(self):
        """Search in the data table"""
        if self.df is None:
            return
            
        search_term = self.search_var.get().strip().lower()
        if not search_term:
            messagebox.showinfo("Search", "Please enter a search term")
            return
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Search across multiple columns
        matches = []
        for idx, row in self.df.iterrows():
            # Get values to search in
            text = str(row.get("text", "")).lower()
            platform = str(row.get("platform", "")).lower()
            sentiment = str(row.get("sentiment", "")).lower()
            user = str(row.get("user", "")).lower()
            hashtags = str(row.get("hashtags", "")).lower()
            country = str(row.get("country", "")).lower()
            timestamp = str(row.get("timestamp", "")).lower()
            
            # Check if search term matches any field
            if (search_term in text or 
                search_term in platform or 
                search_term in sentiment or 
                search_term in user or
                search_term in hashtags or 
                search_term in country or
                search_term in timestamp):
                matches.append(row)
        
        # Create a DataFrame from matches for easier handling
        if matches:
            matches_df = pd.DataFrame(matches).reset_index(drop=True)
            # Populate table with matches
            self.populate_explorer_with_data(matches_df)
        else:
            self.data_info_var.set(f"No matches found for '{search_term}'")
        
        # Update info text
        if matches:
            self.data_info_var.set(f"Found {len(matches)} matching records for '{search_term}'")
        
        # Mark search as active
        self.search_active = True
    
    def clear_search(self):
        """Clear search and restore full data table"""
        self.search_var.set("")
        self.populate_data_table()
        self.search_active = False
    
    def export_data(self):
        """Export data to CSV file"""
        if self.df is None:
            messagebox.showinfo("Export", "No data to export")
            return
            
        try:
            # Ask for file path
            file_path = filedialog.asksaveasfilename(
                title="Export Data",
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            
            if not file_path:
                return
                
            # Check if we're exporting filtered data
            if hasattr(self, 'search_active') and self.search_active:
                # Get the IDs currently in the tree view
                ids = []
                for item in self.tree.get_children():
                    item_id = self.tree.item(item, "values")[0]
                    try:
                        ids.append(int(item_id))
                    except ValueError:
                        continue
                
                # Filter dataframe to those IDs
                if ids:
                    export_df = self.df[self.df["id"].isin(ids)]
                else:
                    export_df = self.df
            elif self.current_filter != "All":
                # Filter by platform
                export_df = self.df[self.df["platform"] == self.current_filter]
            else:
                # Export all data
                export_df = self.df
            
            # Export to CSV
            export_df.to_csv(file_path, index=False)
            
            # Show success message
            messagebox.showinfo("Export", f"Data exported successfully to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
            print(f"Export error: {e}")
    
    def refresh_dashboard(self):
        """Refresh all dashboard components"""
        if self.df is None:
            messagebox.showinfo("Refresh", "No data loaded to refresh.")
            return
            
        try:
            self.status_var.set("Refreshing dashboard...")
            self.root.update()
            
            # Reset filters
            self.platform_var.set("All")
            self.current_filter = "All"
            
            for platform, var in self.platform_vars.items():
                var.set(True)
                
            self.sentiment_var.set("All")
            
            # Clear search
            self.search_var.set("")
            if hasattr(self, 'search_active'):
                self.search_active = False
            
            # Reprocess data
            self.process_data()
            
            # Update UI
            self.status_var.set("Dashboard refreshed successfully!")
        except Exception as e:
            messagebox.showerror("Refresh Error", f"Error refreshing dashboard: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
            print(f"Refresh error: {e}")
    
    def show_help(self):
        """Show help information"""
        help_text = """
Social Media Sentiment Analysis Dashboard

This dashboard helps you analyze sentiment data from various social media platforms.

Data Structure:
- The dashboard works with CSV data containing social media posts and their sentiment analysis.
- Required columns: Text, Sentiment, Platform
- Optional columns: Timestamp, User, Hashtags, Retweets, Likes, Country, etc.

Dashboard Tabs:
1. Overview Tab:
   - View overall sentiment statistics
   - Filter by platform
   - See sentiment distribution pie chart
   - Compare sentiment across platforms

2. Detailed Analysis Tab:
   - Select multiple platforms for comparison
   - Filter by specific sentiment
   - View sentiment trends over time
   - Analyze most common words by sentiment

3. Data Explorer Tab:
   - Browse all data records in a table format
   - Search across data fields
   - Export filtered or complete dataset

Features:
- Load custom datasets using the 'Load Dataset' button
- Filter by platform or sentiment
- Search for specific content
- Export data to CSV

Tips:
- For sentiment trends, the dashboard uses timestamp or date components if available
- Word analysis removes common stop words to focus on meaningful content
- Color coding helps identify positive, neutral, and negative sentiments
- Use the export function to save your filtered data for further analysis

Dataset format should include:
- Text: The content of the social media post
- Sentiment: The sentiment classification (Positive, Neutral, Negative)
- Platform: The social media platform (Twitter, Facebook, Instagram, etc.)
"""
        
        # Create help dialog
        help_window = tk.Toplevel(self.root)
        help_window.title("Dashboard Help")
        help_window.geometry("600x500")
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Add scrollable text widget
        text_frame = ttk.Frame(help_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, width=80, height=30)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Insert help text
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)  # Make read-only
        
        # Add Close button
        close_btn = ttk.Button(help_window, text="Close", command=help_window.destroy)
        close_btn.pack(pady=10)
    
    def filter_explorer_data(self, event=None):
        """Filter the explorer data table by platform"""
        selected_platform = self.explorer_platform_var.get()
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filter data by platform if needed
        if selected_platform == "All":
            filtered_data = self.df
        else:
            filtered_data = self.df[self.df["platform"] == selected_platform]
        
        # Populate table with filtered data
        self.populate_explorer_with_data(filtered_data)
        
        # Update status bar
        total_count = len(filtered_data)
        self.data_info_var.set(f"Showing {total_count} records for {selected_platform}")
    
    def treeview_sort_column(self, col, reverse):
        """Sort treeview contents when a column header is clicked"""
        if self.df is None:
            return
            
        # Get all items from treeview
        item_list = []
        for item_id in self.tree.get_children():
            item_values = self.tree.item(item_id, "values")
            item_list.append(item_values)
        
        # Sort the list based on the column
        try:
            # Try numeric sort first
            item_list.sort(key=lambda x: float(x[self.tree["columns"].index(col)]), reverse=reverse)
        except ValueError:
            # Fall back to string sort
            item_list.sort(key=lambda x: str(x[self.tree["columns"].index(col)]).lower(), reverse=reverse)
        
        # Clear the treeview
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)
        
        # Add sorted items back to treeview
        for item in item_list:
            # Get sentiment for color tagging
            sentiment = item[self.tree["columns"].index("sentiment")].lower()
            self.tree.insert("", tk.END, values=item, tags=(sentiment,))
        
        # Reverse sort next time
        self.tree.heading(col, command=lambda: self.treeview_sort_column(col, not reverse))
    
    def show_item_details(self, event):
        """Show detailed view of a selected item"""
        # Get the selected item
        selected_item = self.tree.selection()
        if not selected_item:
            return
            
        # Get the item values
        item_values = self.tree.item(selected_item[0], "values")
        if not item_values:
            return
            
        # Get the ID
        try:
            item_id = int(item_values[0])
        except (ValueError, IndexError):
            return
            
        # Find the corresponding row in the dataframe
        row = self.df[self.df["id"] == item_id]
        if len(row) == 0:
            return
            
        # Create a detail popup window
        detail_window = tk.Toplevel(self.root)
        detail_window.title("Post Details")
        detail_window.geometry("600x500")
        detail_window.transient(self.root)
        detail_window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(detail_window, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add data fields
        # Get data values with fallbacks to empty string
        text = str(row["text"].values[0]) if "text" in row.columns and len(row["text"].values) > 0 else ""
        platform = str(row["platform"].values[0]) if "platform" in row.columns and len(row["platform"].values) > 0 else ""
        sentiment = str(row["sentiment"].values[0]) if "sentiment" in row.columns and len(row["sentiment"].values) > 0 else ""
        user = str(row["user"].values[0]) if "user" in row.columns and len(row["user"].values) > 0 else ""
        timestamp = str(row["timestamp"].values[0]) if "timestamp" in row.columns and len(row["timestamp"].values) > 0 else ""
        country = str(row["country"].values[0]) if "country" in row.columns and len(row["country"].values) > 0 else ""
        hashtags = str(row["hashtags"].values[0]) if "hashtags" in row.columns and len(row["hashtags"].values) > 0 else ""
        retweets = str(row["retweets"].values[0]) if "retweets" in row.columns and len(row["retweets"].values) > 0 else ""
        likes = str(row["likes"].values[0]) if "likes" in row.columns and len(row["likes"].values) > 0 else ""
        
        # Create a frame with sentiment color
        color = "#e8f5e9" if sentiment.lower() == "positive" else "#fff8e1" if sentiment.lower() == "neutral" else "#ffebee"
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Platform and user info
        ttk.Label(header_frame, text=f"Platform: {platform}", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT)
        ttk.Label(header_frame, text=f"User: {user}", font=("Helvetica", 12)).pack(side=tk.RIGHT)
        
        # Sentiment indicator
        sentiment_frame = ttk.Frame(main_frame)
        sentiment_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create colored frame
        sentiment_indicator = tk.Frame(sentiment_frame, width=20, height=20, bg=color)
        sentiment_indicator.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(sentiment_frame, text=f"Sentiment: {sentiment}", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT)
        
        # Post content
        content_frame = ttk.LabelFrame(main_frame, text="Content")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Scrollable text area for content
        text_widget = tk.Text(content_frame, wrap=tk.WORD, height=8, font=("Helvetica", 11))
        text_scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=text_scrollbar.set)
        
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Insert text and make readonly
        text_widget.insert(tk.END, text)
        text_widget.config(state=tk.DISABLED)
        
        # Metadata
        meta_frame = ttk.LabelFrame(main_frame, text="Metadata")
        meta_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create 2-column grid for metadata
        ttk.Label(meta_frame, text="Date/Time:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        ttk.Label(meta_frame, text=timestamp).grid(row=0, column=1, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(meta_frame, text="Country:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        ttk.Label(meta_frame, text=country).grid(row=1, column=1, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(meta_frame, text="Hashtags:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=3)
        ttk.Label(meta_frame, text=hashtags).grid(row=2, column=1, sticky=tk.W, padx=5, pady=3)
        
        ttk.Label(meta_frame, text="Engagement:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=3)
        ttk.Label(meta_frame, text=f"Retweets: {retweets}, Likes: {likes}").grid(row=3, column=1, sticky=tk.W, padx=5, pady=3)
        
        # Close button
        close_btn = ttk.Button(main_frame, text="Close", command=detail_window.destroy)
        close_btn.pack(pady=(0, 10))
    
    def populate_explorer_with_data(self, data_df):
        """Helper method to populate explorer with given dataframe"""
        if data_df is None or data_df.empty:
            self.data_info_var.set("No matching data found")
            return
            
        # Add data rows
        for _, row in data_df.iterrows():
            # Color code by sentiment
            tag = row["sentiment"].lower() if "sentiment" in row else ""
            
            # Get values to display
            id_val = row.get("id", "")
            platform_val = row.get("platform", "")
            sentiment_val = row.get("sentiment", "")
            text_val = row.get("text", "")
            user_val = row.get("user", "")
            timestamp_val = row.get("timestamp", "")
            country_val = row.get("country", "")
            hashtags_val = row.get("hashtags", "")
            
            # Truncate text if too long
            if isinstance(text_val, str) and len(text_val) > 100:
                text_val = text_val[:97] + "..."
                
            # Truncate hashtags if too long
            if isinstance(hashtags_val, str) and len(hashtags_val) > 50:
                hashtags_val = hashtags_val[:47] + "..."
            
            # Insert row with color tag
            self.tree.insert("", tk.END, values=(
                id_val,
                platform_val,
                sentiment_val,
                text_val,
                user_val,
                timestamp_val,
                country_val,
                hashtags_val
            ), tags=(tag,))


def generate_sample_data():
    """Generate sample data for testing"""
    import pandas as pd
    import random
    
    # Sample platforms
    platforms = ["Twitter", "Facebook", "Instagram"]
    
    # Sample texts by sentiment
    positive_texts = [
        "I absolutely love this product!",
        "Best experience ever, highly recommend!",
        "The service was excellent and the staff were friendly.",
        "This made my day, thank you so much!",
        "Incredible performance, exceeded all expectations.",
        "Very impressed with the quality and speed.",
        "The new features are amazing, great work team!",
        "Such a positive experience from start to finish.",
        "I'm thrilled with my purchase, worth every penny.",
        "Fantastic customer service, very helpful and responsive."
    ]
    
    neutral_texts = [
        "The product works as expected.",
        "Service was okay, nothing special.",
        "It has both pros and cons.",
        "Not bad, but could be better.",
        "Average performance for the price.",
        "It's functional but not outstanding.",
        "Does what it says, nothing more nothing less.",
        "I'm on the fence about this one.",
        "Reasonable quality for the cost.",
        "It's fine for temporary use."
    ]
    
    negative_texts = [
        "Disappointed with the overall quality.",
        "The customer service was terrible.",
        "I wouldn't recommend this to anyone.",
        "Waste of money, doesn't work properly.",
        "Very frustrating experience, won't use again.",
        "The product broke after just one week.",
        "Poor design and even worse implementation.",
        "Not worth the price, look elsewhere.",
        "Extremely slow service and unfriendly staff.",
        "This fell far short of my expectations."
    ]
    
    # Generate data
    data = []
    for i in range(1, 501):  # 500 records
        # Determine sentiment with skew toward neutral
        r = random.random()
        if r < 0.35:
            sentiment = "Positive"
            text = random.choice(positive_texts)
        elif r < 0.75:
            sentiment = "Neutral"
            text = random.choice(neutral_texts)
        else:
            sentiment = "Negative"
            text = random.choice(negative_texts)
        
        # Add some randomness to texts
        if random.random() > 0.7:
            words = ["really", "very", "somewhat", "kind of", "extremely", "slightly"]
            text = f"{random.choice(words)} {text}"
        
        # Pick a platform with weighted distribution
        platform = random.choice(platforms)  # Simplified to avoid weight issue
        
        data.append({
            "id": i,
            "text": text,
            "sentiment": sentiment,
            "platform": platform
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    return df


def main():
    """Main function to run the application"""
    print("Starting the Sentiment Dashboard application...")
    try:
        root = tk.Tk()
        print("Tkinter root window created")
        
        # Create and start app
        app = SentimentDashboard(root)
        print("Application instance created")
        
        # Generate sample data if needed
        if app.df is None:
            try:
                print("Generating sample data...")
                df = generate_sample_data()
                app.df = df
                app.process_data()
                app.status_var.set("Sample data generated for demonstration.")
                print("Sample data generated successfully!")
            except Exception as e:
                print(f"Error generating sample data: {e}")
        
        print("Entering main event loop...")
        root.mainloop()
        print("Application closed.")
    except Exception as e:
        print(f"ERROR STARTING APPLICATION: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()