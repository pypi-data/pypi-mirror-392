"""
Composite Indicator Builder - Enhanced GUI with Data Cleaning
Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: merwanroudane/indic

Professional GUI with comprehensive data preprocessing and cleaning capabilities.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from datetime import datetime
from scipy import stats

from .methods import (
    EqualWeights, BOD_Calculation, Entropy_Calculation,
    PCA_Calculation, Minimal_Uncertainty, GeometricMean,
    HarmonicMean, FactorAnalysis_Calculation, CorrelationWeights,
    normalizar_dados
)

# Set appearance and theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Dr. Roudane's custom color palette
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'danger': '#d62728',
    'info': '#17becf',
    'dark': '#2b2b2b',
    'light': '#f0f0f0',
    'accent': '#9467bd'
}


class DataCleaningWindow(ctk.CTkToplevel):
    """Separate window for data cleaning and preprocessing"""

    def __init__(self, parent, df, callback):
        super().__init__(parent)

        self.title("Data Cleaning & Preprocessing - Dr. Merwan Roudane")
        self.geometry("1000x700")

        self.df = df.copy()
        self.original_df = df.copy()
        self.callback = callback

        self.create_ui()

    def create_ui(self):
        """Create the data cleaning interface"""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🧹 Data Cleaning & Preprocessing",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=10)

        # Tabview for different cleaning operations
        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tabs
        self.tab_missing = self.tabview.add("Missing Values")
        self.tab_outliers = self.tabview.add("Outliers")
        self.tab_transform = self.tabview.add("Transform")
        self.tab_filter = self.tabview.add("Filter")
        self.tab_summary = self.tabview.add("Summary")

        # Build each tab
        self.build_missing_tab()
        self.build_outliers_tab()
        self.build_transform_tab()
        self.build_filter_tab()
        self.build_summary_tab()

        # Bottom buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=10)

        ctk.CTkButton(
            button_frame,
            text="✅ Apply & Close",
            command=self.apply_changes,
            fg_color=COLORS['success'],
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=5, fill="x", expand=True)

        ctk.CTkButton(
            button_frame,
            text="🔄 Reset All",
            command=self.reset_changes,
            fg_color=COLORS['danger'],
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=5, fill="x", expand=True)

        ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            command=self.destroy,
            height=40,
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=5, fill="x", expand=True)

    def build_missing_tab(self):
        """Build missing values handling tab"""
        container = ctk.CTkScrollableFrame(self.tab_missing)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Info
        info_text = f"Missing values detected: {self.df.isnull().sum().sum()}"
        ctk.CTkLabel(
            container,
            text=info_text,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)

        # Missing values details
        missing_frame = ctk.CTkFrame(container)
        missing_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            missing_frame,
            text="Missing Values by Column:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=5)

        for col in self.df.columns:
            missing_count = self.df[col].isnull().sum()
            if missing_count > 0:
                text = f"{col}: {missing_count} missing ({missing_count/len(self.df)*100:.1f}%)"
                ctk.CTkLabel(missing_frame, text=text).pack(anchor="w", padx=20)

        # Handling methods
        method_frame = ctk.CTkFrame(container)
        method_frame.pack(fill="x", pady=20)

        ctk.CTkLabel(
            method_frame,
            text="Select Handling Method:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=5)

        self.missing_method = ctk.StringVar(value="drop_rows")

        methods = [
            ("drop_rows", "Drop rows with missing values"),
            ("drop_cols", "Drop columns with missing values"),
            ("mean", "Fill with mean (numeric only)"),
            ("median", "Fill with median (numeric only)"),
            ("mode", "Fill with mode"),
            ("forward", "Forward fill"),
            ("backward", "Backward fill"),
            ("interpolate", "Linear interpolation")
        ]

        for value, text in methods:
            ctk.CTkRadioButton(
                method_frame,
                text=text,
                variable=self.missing_method,
                value=value
            ).pack(anchor="w", padx=20, pady=2)

        ctk.CTkButton(
            container,
            text="Apply Missing Value Treatment",
            command=self.handle_missing,
            fg_color=COLORS['primary']
        ).pack(pady=10)

    def build_outliers_tab(self):
        """Build outliers detection and removal tab"""
        container = ctk.CTkScrollableFrame(self.tab_outliers)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            container,
            text="🔍 Outlier Detection & Removal",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)

        # Method selection
        method_frame = ctk.CTkFrame(container)
        method_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            method_frame,
            text="Detection Method:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=5)

        self.outlier_method = ctk.StringVar(value="iqr")

        ctk.CTkRadioButton(
            method_frame,
            text="IQR Method (Interquartile Range)",
            variable=self.outlier_method,
            value="iqr"
        ).pack(anchor="w", padx=20, pady=2)

        ctk.CTkRadioButton(
            method_frame,
            text="Z-Score Method (|z| > 3)",
            variable=self.outlier_method,
            value="zscore"
        ).pack(anchor="w", padx=20, pady=2)

        ctk.CTkRadioButton(
            method_frame,
            text="Modified Z-Score (MAD-based)",
            variable=self.outlier_method,
            value="modified_zscore"
        ).pack(anchor="w", padx=20, pady=2)

        # Action selection
        action_frame = ctk.CTkFrame(container)
        action_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            action_frame,
            text="Action:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=5)

        self.outlier_action = ctk.StringVar(value="remove")

        ctk.CTkRadioButton(
            action_frame,
            text="Remove outlier rows",
            variable=self.outlier_action,
            value="remove"
        ).pack(anchor="w", padx=20, pady=2)

        ctk.CTkRadioButton(
            action_frame,
            text="Cap outliers (winsorize)",
            variable=self.outlier_action,
            value="cap"
        ).pack(anchor="w", padx=20, pady=2)

        ctk.CTkRadioButton(
            action_frame,
            text="Replace with median",
            variable=self.outlier_action,
            value="median"
        ).pack(anchor="w", padx=20, pady=2)

        ctk.CTkButton(
            container,
            text="Detect & Handle Outliers",
            command=self.handle_outliers,
            fg_color=COLORS['primary']
        ).pack(pady=10)

    def build_transform_tab(self):
        """Build data transformation tab"""
        container = ctk.CTkScrollableFrame(self.tab_transform)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            container,
            text="🔄 Data Transformations",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)

        # Normalization
        norm_frame = ctk.CTkFrame(container)
        norm_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            norm_frame,
            text="Normalization/Standardization:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=5)

        self.norm_method = ctk.StringVar(value="minmax")

        ctk.CTkRadioButton(
            norm_frame,
            text="Min-Max Normalization [0, 1]",
            variable=self.norm_method,
            value="minmax"
        ).pack(anchor="w", padx=20, pady=2)

        ctk.CTkRadioButton(
            norm_frame,
            text="Z-Score Standardization (μ=0, σ=1)",
            variable=self.norm_method,
            value="zscore"
        ).pack(anchor="w", padx=20, pady=2)

        ctk.CTkRadioButton(
            norm_frame,
            text="Robust Scaling (median-based)",
            variable=self.norm_method,
            value="robust"
        ).pack(anchor="w", padx=20, pady=2)

        ctk.CTkButton(
            container,
            text="Apply Normalization",
            command=self.apply_normalization,
            fg_color=COLORS['primary']
        ).pack(pady=10)

        # Mathematical transformations
        transform_frame = ctk.CTkFrame(container)
        transform_frame.pack(fill="x", pady=20)

        ctk.CTkLabel(
            transform_frame,
            text="Mathematical Transformations:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=5)

        self.math_transform = ctk.StringVar(value="log")

        ctk.CTkRadioButton(
            transform_frame,
            text="Log transformation (ln)",
            variable=self.math_transform,
            value="log"
        ).pack(anchor="w", padx=20, pady=2)

        ctk.CTkRadioButton(
            transform_frame,
            text="Square root",
            variable=self.math_transform,
            value="sqrt"
        ).pack(anchor="w", padx=20, pady=2)

        ctk.CTkRadioButton(
            transform_frame,
            text="Box-Cox transformation",
            variable=self.math_transform,
            value="boxcox"
        ).pack(anchor="w", padx=20, pady=2)

        ctk.CTkButton(
            container,
            text="Apply Transformation",
            command=self.apply_math_transform,
            fg_color=COLORS['primary']
        ).pack(pady=10)

    def build_filter_tab(self):
        """Build data filtering tab"""
        container = ctk.CTkScrollableFrame(self.tab_filter)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            container,
            text="🔎 Filter Data",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)

        # Remove duplicates
        dup_frame = ctk.CTkFrame(container)
        dup_frame.pack(fill="x", pady=10)

        duplicates = self.df.duplicated().sum()
        ctk.CTkLabel(
            dup_frame,
            text=f"Duplicate rows found: {duplicates}",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=5)

        ctk.CTkButton(
            dup_frame,
            text="Remove Duplicates",
            command=self.remove_duplicates,
            fg_color=COLORS['primary']
        ).pack(pady=5)

        # Remove columns
        col_frame = ctk.CTkFrame(container)
        col_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            col_frame,
            text="Remove Columns:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=5)

        self.cols_to_remove = []
        self.col_checkboxes = {}

        for col in self.df.columns:
            var = ctk.BooleanVar(value=False)
            self.col_checkboxes[col] = var
            cb = ctk.CTkCheckBox(
                col_frame,
                text=col,
                variable=var
            )
            cb.pack(anchor="w", padx=20, pady=2)

        ctk.CTkButton(
            col_frame,
            text="Remove Selected Columns",
            command=self.remove_columns,
            fg_color=COLORS['danger']
        ).pack(pady=5)

    def build_summary_tab(self):
        """Build data summary tab"""
        container = ctk.CTkScrollableFrame(self.tab_summary)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        self.update_summary(container)

    def update_summary(self, container):
        """Update the summary information"""
        # Clear existing widgets
        for widget in container.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            container,
            text="📊 Data Summary",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)

        # Basic info
        info_frame = ctk.CTkFrame(container)
        info_frame.pack(fill="x", pady=10)

        info_text = f"""
        Shape: {self.df.shape[0]} rows × {self.df.shape[1]} columns
        
        Missing Values: {self.df.isnull().sum().sum()}
        
        Duplicate Rows: {self.df.duplicated().sum()}
        
        Numeric Columns: {len(self.df.select_dtypes(include=[np.number]).columns)}
        
        Memory Usage: {self.df.memory_usage(deep=True).sum() / 1024:.2f} KB
        """

        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        ).pack(pady=10, padx=20)

        # Column types
        types_frame = ctk.CTkFrame(container)
        types_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            types_frame,
            text="Column Data Types:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=5)

        for col in self.df.columns:
            text = f"{col}: {self.df[col].dtype}"
            ctk.CTkLabel(types_frame, text=text, font=ctk.CTkFont(size=10)).pack(anchor="w", padx=20)

    def handle_missing(self):
        """Handle missing values based on selected method"""
        method = self.missing_method.get()

        try:
            if method == "drop_rows":
                self.df = self.df.dropna()
            elif method == "drop_cols":
                self.df = self.df.dropna(axis=1)
            elif method == "mean":
                numeric_cols = self.df.select_dtypes(include=[np.number]).columns
                self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].mean())
            elif method == "median":
                numeric_cols = self.df.select_dtypes(include=[np.number]).columns
                self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].median())
            elif method == "mode":
                for col in self.df.columns:
                    self.df[col].fillna(self.df[col].mode()[0], inplace=True)
            elif method == "forward":
                self.df = self.df.fillna(method='ffill')
            elif method == "backward":
                self.df = self.df.fillna(method='bfill')
            elif method == "interpolate":
                numeric_cols = self.df.select_dtypes(include=[np.number]).columns
                self.df[numeric_cols] = self.df[numeric_cols].interpolate()

            messagebox.showinfo("Success", f"Missing values handled using {method} method!")
            self.update_summary(self.tab_summary)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to handle missing values:\n{str(e)}")

    def handle_outliers(self):
        """Detect and handle outliers"""
        method = self.outlier_method.get()
        action = self.outlier_action.get()

        try:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            outlier_mask = pd.Series([False] * len(self.df))

            for col in numeric_cols:
                if method == "iqr":
                    Q1 = self.df[col].quantile(0.25)
                    Q3 = self.df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower = Q1 - 1.5 * IQR
                    upper = Q3 + 1.5 * IQR
                    col_outliers = (self.df[col] < lower) | (self.df[col] > upper)

                elif method == "zscore":
                    z_scores = np.abs(stats.zscore(self.df[col].dropna()))
                    col_outliers = pd.Series([False] * len(self.df))
                    col_outliers.loc[self.df[col].notna()] = z_scores > 3

                elif method == "modified_zscore":
                    median = self.df[col].median()
                    mad = np.median(np.abs(self.df[col] - median))
                    modified_z = 0.6745 * (self.df[col] - median) / mad
                    col_outliers = np.abs(modified_z) > 3.5

                if action == "remove":
                    outlier_mask = outlier_mask | col_outliers
                elif action == "cap":
                    if method == "iqr":
                        self.df.loc[self.df[col] < lower, col] = lower
                        self.df.loc[self.df[col] > upper, col] = upper
                elif action == "median":
                    self.df.loc[col_outliers, col] = self.df[col].median()

            if action == "remove":
                rows_before = len(self.df)
                self.df = self.df[~outlier_mask]
                rows_removed = rows_before - len(self.df)
                messagebox.showinfo("Success", f"Removed {rows_removed} rows with outliers!")
            else:
                messagebox.showinfo("Success", "Outliers handled successfully!")

            self.update_summary(self.tab_summary)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to handle outliers:\n{str(e)}")

    def apply_normalization(self):
        """Apply normalization to numeric columns"""
        method = self.norm_method.get()

        try:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns

            for col in numeric_cols:
                if method == "minmax":
                    min_val = self.df[col].min()
                    max_val = self.df[col].max()
                    self.df[col] = (self.df[col] - min_val) / (max_val - min_val)

                elif method == "zscore":
                    mean = self.df[col].mean()
                    std = self.df[col].std()
                    self.df[col] = (self.df[col] - mean) / std

                elif method == "robust":
                    median = self.df[col].median()
                    q75 = self.df[col].quantile(0.75)
                    q25 = self.df[col].quantile(0.25)
                    iqr = q75 - q25
                    self.df[col] = (self.df[col] - median) / iqr

            messagebox.showinfo("Success", f"Applied {method} normalization!")

        except Exception as e:
            messagebox.showerror("Error", f"Normalization failed:\n{str(e)}")

    def apply_math_transform(self):
        """Apply mathematical transformation"""
        method = self.math_transform.get()

        try:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns

            for col in numeric_cols:
                if method == "log":
                    # Add small constant if there are zeros
                    min_val = self.df[col].min()
                    if min_val <= 0:
                        self.df[col] = np.log(self.df[col] - min_val + 1)
                    else:
                        self.df[col] = np.log(self.df[col])

                elif method == "sqrt":
                    min_val = self.df[col].min()
                    if min_val < 0:
                        self.df[col] = np.sqrt(self.df[col] - min_val)
                    else:
                        self.df[col] = np.sqrt(self.df[col])

                elif method == "boxcox":
                    # Box-Cox requires positive values
                    if self.df[col].min() > 0:
                        self.df[col], _ = stats.boxcox(self.df[col])
                    else:
                        messagebox.showwarning("Warning", f"Column {col} has non-positive values, skipped")

            messagebox.showinfo("Success", f"Applied {method} transformation!")

        except Exception as e:
            messagebox.showerror("Error", f"Transformation failed:\n{str(e)}")

    def remove_duplicates(self):
        """Remove duplicate rows"""
        rows_before = len(self.df)
        self.df = self.df.drop_duplicates()
        rows_removed = rows_before - len(self.df)

        messagebox.showinfo("Success", f"Removed {rows_removed} duplicate rows!")
        self.update_summary(self.tab_summary)

    def remove_columns(self):
        """Remove selected columns"""
        cols_to_remove = [col for col, var in self.col_checkboxes.items() if var.get()]

        if not cols_to_remove:
            messagebox.showwarning("Warning", "No columns selected!")
            return

        self.df = self.df.drop(columns=cols_to_remove)
        messagebox.showinfo("Success", f"Removed {len(cols_to_remove)} columns!")
        self.update_summary(self.tab_summary)

    def reset_changes(self):
        """Reset all changes"""
        self.df = self.original_df.copy()
        messagebox.showinfo("Reset", "All changes have been reset!")
        self.update_summary(self.tab_summary)

    def apply_changes(self):
        """Apply changes and close window"""
        self.callback(self.df)
        self.destroy()


class CompositeIndicatorApp(ctk.CTk):
    """Main application window with enhanced features"""

    def __init__(self):
        super().__init__()

        self.title("Composite Indicator Builder - by Dr. Merwan Roudane")
        self.geometry("1400x900")
        self.center_window()

        self.df = None
        self.cleaned_df = None
        self.results = {}
        self.ranking_ic = []

        self.build_ui()

    def center_window(self):
        """Center window on screen"""
        self.update_idletasks()
        width = 1400
        height = 900
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def build_ui(self):
        """Build main UI"""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_content()

    def create_sidebar(self):
        """Create scrollable sidebar"""
        sidebar_container = ctk.CTkFrame(self, width=300, corner_radius=0)
        sidebar_container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        sidebar_container.grid_propagate(False)

        sidebar = ctk.CTkScrollableFrame(sidebar_container, width=280, corner_radius=0)
        sidebar.pack(fill="both", expand=True, padx=0, pady=0)

        # Header
        header_frame = ctk.CTkFrame(sidebar, fg_color=COLORS['primary'])
        header_frame.pack(fill="x", padx=10, pady=20)

        ctk.CTkLabel(
            header_frame,
            text="🔬 Indicator Builder",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(pady=10)

        ctk.CTkLabel(
            header_frame,
            text="Dr. Merwan Roudane",
            font=ctk.CTkFont(size=12),
            text_color="white"
        ).pack(pady=(0, 10))

        # File operations
        file_frame = ctk.CTkFrame(sidebar)
        file_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            file_frame,
            text="📁 Data Management",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))

        self.load_btn = ctk.CTkButton(
            file_frame,
            text="📂 Load Excel File",
            command=self.load_file,
            fg_color=COLORS['success'],
            hover_color=COLORS['primary']
        )
        self.load_btn.pack(pady=5, padx=10, fill="x")

        # ============ NEW: DATA CLEANING BUTTON ============
        self.clean_btn = ctk.CTkButton(
            file_frame,
            text="🧹 Clean & Preprocess Data",
            command=self.open_cleaning_window,
            fg_color=COLORS['info'],
            hover_color=COLORS['primary'],
            state="disabled"
        )
        self.clean_btn.pack(pady=5, padx=10, fill="x")

        # Data preview button
        self.preview_btn = ctk.CTkButton(
            file_frame,
            text="👁️ Preview Data",
            command=self.preview_data,
            state="disabled"
        )
        self.preview_btn.pack(pady=5, padx=10, fill="x")

        # Indicator selection
        self.columns_frame = ctk.CTkFrame(sidebar)
        self.columns_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            self.columns_frame,
            text="📊 Indicator Selection",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))

        self.scroll_frame = ctk.CTkScrollableFrame(self.columns_frame, height=150)
        self.scroll_frame.pack(pady=5, padx=10, fill="both", expand=True)

        # Label and Control selections
        label_frame = ctk.CTkFrame(sidebar)
        label_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            label_frame,
            text="🏷️ Label Column",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))

        self.label_var = ctk.StringVar(value="None")
        self.label_menu = ctk.CTkOptionMenu(label_frame, variable=self.label_var, values=["None"])
        self.label_menu.pack(pady=5, padx=10, fill="x")

        control_frame = ctk.CTkFrame(sidebar)
        control_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            control_frame,
            text="🎯 Control Variable",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))

        self.control_var = ctk.StringVar(value="None")
        self.control_menu = ctk.CTkOptionMenu(control_frame, variable=self.control_var, values=["None"])
        self.control_menu.pack(pady=5, padx=10, fill="x")

        # Methods
        methods_frame = ctk.CTkFrame(sidebar)
        methods_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            methods_frame,
            text="⚙️ Methods",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))

        self.method_vars = {}
        methods = [
            ("PCA", "Principal Component Analysis"),
            ("Equal Weights", "Simple Average"),
            ("Entropy", "Shannon's Entropy"),
            ("BoD", "Benefit of the Doubt"),
            ("Geometric", "Geometric Mean"),
            ("Harmonic", "Harmonic Mean"),
            ("Factor Analysis", "Factor Analysis"),
            ("Correlation", "Correlation-based"),
            ("Minimal Uncertainty", "Minimal Uncertainty")
        ]

        for method, tooltip in methods:
            var = ctk.BooleanVar(value=True if method in ["PCA", "Equal Weights", "Entropy"] else False)
            self.method_vars[method] = var
            cb = ctk.CTkCheckBox(methods_frame, text=method, variable=var, font=ctk.CTkFont(size=11))
            cb.pack(pady=2, padx=10, anchor="w")

        # Calculate and Export buttons
        self.calc_btn = ctk.CTkButton(
            sidebar,
            text="🚀 Calculate Indicators",
            command=self.calculate_indicators,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['primary'],
            hover_color=COLORS['accent']
        )
        self.calc_btn.pack(fill="x", padx=10, pady=20)

        self.export_btn = ctk.CTkButton(
            sidebar,
            text="💾 Export Results",
            command=self.export_results,
            height=35,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS['success'],
            hover_color=COLORS['primary']
        )
        self.export_btn.pack(fill="x", padx=10, pady=10)

        self.doc_btn = ctk.CTkButton(
            sidebar,
            text="📚 Documentation",
            command=self.show_documentation,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.doc_btn.pack(fill="x", padx=10, pady=10)

        # About
        about_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        about_frame.pack(fill="x", padx=10, pady=20)

        ctk.CTkLabel(about_frame, text="Version 2.0.0 - Enhanced", font=ctk.CTkFont(size=10), text_color="gray").pack()
        ctk.CTkLabel(about_frame, text="github.com/merwanroudane/indic", font=ctk.CTkFont(size=9), text_color="gray").pack()

    def create_main_content(self):
        """Create main content area"""
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Welcome screen
        self.welcome_frame = ctk.CTkFrame(self.main_frame)
        self.welcome_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self.welcome_frame,
            text="🎯 Welcome to Composite Indicator Builder",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(100, 20))

        ctk.CTkLabel(
            self.welcome_frame,
            text="Enhanced Edition with Data Cleaning",
            font=ctk.CTkFont(size=18),
            text_color=COLORS['info']
        ).pack(pady=(0, 20))

        ctk.CTkLabel(
            self.welcome_frame,
            text="Load your data to get started",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        ).pack(pady=(0, 20))

        features_text = """
        ✓ 9 different calculation methods
        ✓ Comprehensive data cleaning & preprocessing
        ✓ Missing value handling
        ✓ Outlier detection & removal
        ✓ Data transformations & normalization
        ✓ Interactive visualizations
        ✓ Excel export with multiple sheets
        """

        ctk.CTkLabel(
            self.welcome_frame,
            text=features_text,
            font=ctk.CTkFont(size=14),
            justify="left"
        ).pack(pady=20)

        ctk.CTkLabel(
            self.welcome_frame,
            text="Developed by Dr. Merwan Roudane\nmerwanroudane920@gmail.com",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['secondary']
        ).pack(side="bottom", pady=20)

    def load_file(self):
        """Load Excel file"""
        filename = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            self.df = pd.read_excel(filename)
            self.cleaned_df = self.df.copy()

            # Update UI
            for widget in self.scroll_frame.winfo_children():
                widget.destroy()

            self.column_vars = {}
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
            all_cols = self.df.columns.tolist()

            for col in numeric_cols:
                var = ctk.BooleanVar(value=True)
                self.column_vars[col] = var
                cb = ctk.CTkCheckBox(self.scroll_frame, text=col, variable=var, font=ctk.CTkFont(size=11))
                cb.pack(pady=2, padx=5, anchor="w")

            self.label_menu.configure(values=["None"] + all_cols)
            self.label_var.set("None")

            self.control_menu.configure(values=["None"] + numeric_cols)
            self.control_var.set("None")

            # Enable buttons
            self.clean_btn.configure(state="normal")
            self.preview_btn.configure(state="normal")

            messagebox.showinfo(
                "Success",
                f"File loaded successfully!\n\nRows: {len(self.df)}\nColumns: {len(self.df.columns)}\nNumeric columns: {len(numeric_cols)}"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")

    def open_cleaning_window(self):
        """Open data cleaning window"""
        if self.df is None:
            messagebox.showwarning("Warning", "Please load a data file first!")
            return

        cleaning_window = DataCleaningWindow(self, self.cleaned_df, self.update_cleaned_data)

    def update_cleaned_data(self, cleaned_df):
        """Callback to update cleaned data"""
        self.cleaned_df = cleaned_df
        messagebox.showinfo("Success", "Data cleaning completed!\nUsing cleaned data for calculations.")

    def preview_data(self):
        """Preview current data"""
        if self.cleaned_df is None:
            messagebox.showwarning("Warning", "No data to preview!")
            return

        preview_window = ctk.CTkToplevel(self)
        preview_window.title("Data Preview")
        preview_window.geometry("900x600")

        # Show basic info
        info_text = f"""
        Shape: {self.cleaned_df.shape[0]} rows × {self.cleaned_df.shape[1]} columns
        Missing Values: {self.cleaned_df.isnull().sum().sum()}
        Duplicates: {self.cleaned_df.duplicated().sum()}
        """

        ctk.CTkLabel(preview_window, text=info_text, font=ctk.CTkFont(size=12)).pack(pady=10)

        # Show first rows
        text_widget = ctk.CTkTextbox(preview_window)
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)

        text_widget.insert("1.0", self.cleaned_df.head(20).to_string())
        text_widget.configure(state="disabled")

    def calculate_indicators(self):
        """Calculate composite indicators using cleaned data"""
        if self.cleaned_df is None:
            messagebox.showwarning("Warning", "Please load a data file first!")
            return

        selected_cols = [col for col, var in self.column_vars.items() if var.get()]

        if len(selected_cols) < 2:
            messagebox.showwarning("Warning", "Please select at least 2 indicators!")
            return

        selected_methods = [method for method, var in self.method_vars.items() if var.get()]

        if not selected_methods:
            messagebox.showwarning("Warning", "Please select at least one method!")
            return

        try:
            # Use cleaned data for calculations
            control_col = self.control_var.get() if self.control_var.get() != "None" else None

            normalized_data = {}
            for col in selected_cols:
                if control_col and control_col in self.cleaned_df.columns:
                    corr = self.cleaned_df[col].corr(self.cleaned_df[control_col])
                    orientation = "Min" if corr > 0 else "Max"
                else:
                    orientation = "Min"

                normalized_data[col] = normalizar_dados(self.cleaned_df[col].tolist(), orientation)

            df_norm = pd.DataFrame(normalized_data)

            # Calculate for each method
            self.results = {}

            for method in selected_methods:
                if method == "PCA":
                    model = PCA_Calculation(df_norm)
                    self.results[method] = model.run()

                elif method == "Equal Weights":
                    model = EqualWeights(df_norm)
                    self.results[method] = model.run()

                elif method == "Entropy":
                    model = Entropy_Calculation(df_norm)
                    self.results[method] = model.run()

                elif method == "BoD":
                    model = BOD_Calculation(df_norm)
                    self.results[method] = model.run()

                elif method == "Geometric":
                    model = GeometricMean(df_norm)
                    self.results[method] = model.run()

                elif method == "Harmonic":
                    model = HarmonicMean(df_norm)
                    self.results[method] = model.run()

                elif method == "Factor Analysis":
                    model = FactorAnalysis_Calculation(df_norm)
                    self.results[method] = model.run()

                elif method == "Correlation":
                    model = CorrelationWeights(df_norm)
                    self.results[method] = model.run()

                elif method == "Minimal Uncertainty":
                    all_results = {}
                    for m in ["PCA", "Equal Weights", "Entropy"]:
                        if m == "PCA":
                            model = PCA_Calculation(df_norm)
                        elif m == "Equal Weights":
                            model = EqualWeights(df_norm)
                        else:
                            model = Entropy_Calculation(df_norm)
                        all_results[m] = model.run()

                    model = Minimal_Uncertainty(df_norm, all_results)
                    self.results[method] = model.run()

            self.display_results()

            messagebox.showinfo(
                "Success",
                f"Calculation completed!\n\nMethods: {len(selected_methods)}\nIndicators: {len(selected_cols)}\nUnits: {len(self.cleaned_df)}"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Calculation failed:\n{str(e)}")

    def display_results(self):
        """Display results in tabview"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        tabview = ctk.CTkTabview(self.main_frame)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)

        for method, results in self.results.items():
            tab = tabview.add(method)
            self.create_results_tab(tab, method, results)

        if len(self.results) > 1:
            comp_tab = tabview.add("Comparison")
            self.create_comparison_tab(comp_tab)

    def create_results_tab(self, parent, method, results):
        """Create results display"""
        container = ctk.CTkScrollableFrame(parent)
        container.pack(fill="both", expand=True, padx=5, pady=5)

        df_results = pd.DataFrame([
            {'CI': r.ci, **{f'W{i+1}': w for i, w in enumerate(r.weights)}}
            for r in results
        ])

        label_col = self.label_var.get()
        if label_col != "None" and label_col in self.cleaned_df.columns:
            df_results.insert(0, 'Label', self.cleaned_df[label_col].values[:len(results)])
        else:
            df_results.insert(0, 'Label', [f"DMU {i+1}" for i in range(len(results))])

        df_results = df_results.sort_values('CI', ascending=False)
        df_results.insert(1, 'Rank', range(1, len(df_results) + 1))

        # Summary stats
        stats_frame = ctk.CTkFrame(container)
        stats_frame.pack(fill="x", padx=5, pady=10)

        ci_values = df_results['CI'].values
        stats = [
            ("Mean", f"{np.mean(ci_values):.4f}"),
            ("Std Dev", f"{np.std(ci_values):.4f}"),
            ("Min", f"{np.min(ci_values):.4f}"),
            ("Max", f"{np.max(ci_values):.4f}")
        ]

        for i, (label, value) in enumerate(stats):
            stat_frame = ctk.CTkFrame(stats_frame)
            stat_frame.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            stats_frame.grid_columnconfigure(i, weight=1)

            ctk.CTkLabel(stat_frame, text=label, font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(5, 0))
            ctk.CTkLabel(stat_frame, text=value, font=ctk.CTkFont(size=16)).pack(pady=(0, 5))

        # Visualization
        viz_frame = ctk.CTkFrame(container)
        viz_frame.pack(fill="both", expand=True)

        self.create_visualization(viz_frame, df_results, method)

    def create_visualization(self, parent, df_results, method):
        """Create visualizations"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        fig.patch.set_facecolor('#2b2b2b' if ctk.get_appearance_mode() == "Dark" else 'white')

        top10 = df_results.head(10)
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(top10)))
        ax1.barh(range(len(top10)), top10['CI'].values, color=colors)
        ax1.set_yticks(range(len(top10)))
        ax1.set_yticklabels(top10['Label'].values)
        ax1.set_xlabel('Composite Indicator Value')
        ax1.set_title(f'Top 10 Units - {method}')
        ax1.invert_yaxis()

        ax2.hist(df_results['CI'].values, bins=20, color=COLORS['primary'], alpha=0.7, edgecolor='black')
        ax2.set_xlabel('Composite Indicator Value')
        ax2.set_ylabel('Frequency')
        ax2.set_title(f'CI Distribution - {method}')
        ax2.axvline(df_results['CI'].mean(), color='red', linestyle='--', label='Mean')
        ax2.legend()

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    def create_comparison_tab(self, parent):
        """Create comparison visualization"""
        container = ctk.CTkScrollableFrame(parent)
        container.pack(fill="both", expand=True, padx=5, pady=5)

        comparison_data = {}
        for method, results in self.results.items():
            comparison_data[method] = [r.ci for r in results]

        df_comp = pd.DataFrame(comparison_data)

        label_col = self.label_var.get()
        if label_col != "None" and label_col in self.cleaned_df.columns:
            df_comp.insert(0, 'Label', self.cleaned_df[label_col].values[:len(results)])
        else:
            df_comp.insert(0, 'Label', [f"DMU {i+1}" for i in range(len(results))])

        corr_frame = ctk.CTkFrame(container)
        corr_frame.pack(fill="both", expand=True, padx=5, pady=10)

        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_facecolor('#2b2b2b' if ctk.get_appearance_mode() == "Dark" else 'white')

        corr_matrix = df_comp.drop('Label', axis=1).corr()
        sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm',
                    center=0, square=True, ax=ax, cbar_kws={'label': 'Correlation'})
        ax.set_title('Method Correlation Matrix', fontsize=14, pad=20)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, corr_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    def export_results(self):
        """Export results to Excel"""
        if not self.results:
            messagebox.showwarning("Warning", "No results to export!")
            return

        filename = filedialog.asksaveasfilename(
            title="Save Results",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=f"composite_indicators_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )

        if filename:
            try:
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    for method, results in self.results.items():
                        df_results = pd.DataFrame([
                            {'CI': r.ci, **{f'Weight_{i+1}': w for i, w in enumerate(r.weights)}}
                            for r in results
                        ])

                        label_col = self.label_var.get()
                        if label_col != "None":
                            df_results.insert(0, 'Label', self.cleaned_df[label_col].values[:len(results)])
                        else:
                            df_results.insert(0, 'Label', [f"DMU {i+1}" for i in range(len(results))])

                        df_results = df_results.sort_values('CI', ascending=False)
                        df_results.insert(1, 'Rank', range(1, len(df_results) + 1))

                        sheet_name = method[:31]
                        df_results.to_excel(writer, sheet_name=sheet_name, index=False)

                    summary_data = []
                    for method, results in self.results.items():
                        ci_values = [r.ci for r in results]
                        summary_data.append({
                            'Method': method,
                            'Min': np.min(ci_values),
                            'Max': np.max(ci_values),
                            'Mean': np.mean(ci_values),
                            'Std Dev': np.std(ci_values)
                        })

                    df_summary = pd.DataFrame(summary_data)
                    df_summary.to_excel(writer, sheet_name='Summary', index=False)

                messagebox.showinfo("Success", f"Results exported to:\n{filename}")

            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")

    def show_documentation(self):
        """Show documentation"""
        doc_window = ctk.CTkToplevel(self)
        doc_window.title("Documentation")
        doc_window.geometry("800x600")

        doc_text = ctk.CTkTextbox(doc_window)
        doc_text.pack(fill="both", expand=True, padx=10, pady=10)

        documentation = """
COMPOSITE INDICATOR BUILDER - ENHANCED EDITION
==============================================

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: merwanroudane/indic

NEW FEATURES IN VERSION 2.0
---------------------------
✓ Comprehensive data cleaning interface
✓ Missing value handling (8 methods)
✓ Outlier detection & removal (3 methods)
✓ Data transformations (normalization, standardization)
✓ Mathematical transformations (log, sqrt, Box-Cox)
✓ Data filtering and column management
✓ Real-time data summary and statistics

DATA CLEANING OPTIONS
---------------------

1. Missing Values Handling:
   - Drop rows/columns
   - Fill with mean, median, mode
   - Forward/backward fill
   - Linear interpolation

2. Outlier Detection:
   - IQR method
   - Z-score method
   - Modified Z-score (MAD-based)
   
   Actions:
   - Remove outlier rows
   - Cap outliers (winsorize)
   - Replace with median

3. Data Transformations:
   - Min-Max normalization [0, 1]
   - Z-score standardization
   - Robust scaling
   - Log transformation
   - Square root transformation
   - Box-Cox transformation

4. Data Filtering:
   - Remove duplicates
   - Remove columns
   - Filter rows (coming soon)

WORKFLOW
--------
1. Load Excel file
2. Clean & preprocess data (optional but recommended)
3. Select indicators
4. Choose methods
5. Calculate indicators
6. Export results

CALCULATION METHODS
-------------------
1. PCA - Principal Component Analysis
2. Equal Weights - Simple average
3. Shannon's Entropy - Information-based
4. Benefit of the Doubt - DEA-based
5. Geometric Mean - Multiplicative
6. Harmonic Mean - Least compensatory
7. Factor Analysis - Latent factors
8. Correlation-based - Reference correlation
9. Minimal Uncertainty - Consensus ranking

For detailed information on each method, refer to OECD Handbook
on Constructing Composite Indicators.

SUPPORT
-------
Dr. Merwan Roudane
merwanroudane920@gmail.com
"""

        doc_text.insert("1.0", documentation)
        doc_text.configure(state="disabled")


def main():
    """Main entry point"""
    app = CompositeIndicatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()