"""
Conway's Game of Life Simulator

A Tkinter-based GUI application that simulates Conway's Game of Life.
Users can select predefined patterns and watch them evolve in real-time
using embedded Matplotlib animations within Tkinter.

Author: [Your Name or Username]
License: MIT (or your preferred license)
Dependencies: tkinter, numpy, matplotlib
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")  # Use Tkinter-compatible backend for Matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys

# Constants
GRID_ROWS = 60  # Larger grid for better pattern movement and less edge interference
GRID_COLS = 60
ANIMATION_FRAMES = 1000  # More frames for longer simulation
ANIMATION_INTERVAL = 150  # Faster for smoother movement

# Predefined patterns (coordinates as (row, col) tuples, centered for proper evolution)
PATTERNS = {
    "Gliders": {
        "Glider": [(25, 26), (26, 27), (27, 25), (27, 26), (27, 27)],  # Centered, standard 5 cells
        "Lightweight Spaceship (LWSS)": [  # Corrected to standard 9 cells
            (25, 26), (26, 25), (26, 29), (27, 25), (28, 25), (28, 28), (28, 29), (29, 25), (29, 29)
        ],
    },
    "Oscillators": {
        "Blinker": [(30, 29), (30, 30), (30, 31)],  # Centered
        "Toad": [(25, 26), (25, 27), (25, 28), (26, 25), (26, 26), (26, 27)],  # Centered, standard 6 cells
    },
}

class GameOfLifeApp:
    """
    Main application class for the Conway's Game of Life GUI.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Conway's Game of Life")
        self.root.geometry("800x600")  # Larger window for embedded plots
        
        # Notebook for multiple tabs (one per simulation)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        
        # UI Elements
        self.setup_ui()
        
        # Track active animations to prevent conflicts
        self.active_animations = []
    
    def setup_ui(self):
        """Set up the Tkinter UI components."""
        # Create a tab for pattern selection
        select_tab = ttk.Frame(self.notebook)
        self.notebook.add(select_tab, text="Select Pattern")
        
        # Title label
        tk.Label(select_tab, text="Select a Pattern", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Scrollable frame for buttons
        canvas = tk.Canvas(select_tab)
        scrollbar = ttk.Scrollbar(select_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create buttons for each pattern
        for category, items in PATTERNS.items():
            tk.Label(scrollable_frame, text=category, font=("Arial", 14, "bold")).pack(pady=5)
            for name, cells in items.items():
                tk.Button(
                    scrollable_frame, text=name,
                    width=30, height=2,
                    command=lambda c=cells, n=name: self.run_simulation(c, n)
                ).pack(pady=3)
    
    def run_simulation(self, cells, title):
        """Run the Game of Life simulation in a new tab with embedded Matplotlib."""
        try:
            # Stop any existing animations to avoid conflicts
            for ani in self.active_animations:
                ani.event_source.stop()
            self.active_animations.clear()
            
            # Create a new tab for the simulation
            sim_tab = ttk.Frame(self.notebook)
            self.notebook.add(sim_tab, text=title)
            self.notebook.select(sim_tab)  # Switch to the new tab
            
            # Initialize grid
            grid = np.zeros((GRID_ROWS, GRID_COLS))
            for i, j in cells:
                if 0 <= i < GRID_ROWS and 0 <= j < GRID_COLS:
                    grid[i, j] = 1
            
            # Update function for animation
            def update(frame):
                nonlocal grid
                new_grid = grid.copy()
                for i in range(GRID_ROWS):
                    for j in range(GRID_COLS):
                        # Count neighbors (toroidal grid)
                        neighbors = sum(
                            grid[(i + di) % GRID_ROWS, (j + dj) % GRID_COLS]
                            for di in [-1, 0, 1] for dj in [-1, 0, 1] if (di, dj) != (0, 0)
                        )
                        # Apply Conway's rules
                        if grid[i, j] == 1 and (neighbors < 2 or neighbors > 3):
                            new_grid[i, j] = 0
                        elif grid[i, j] == 0 and neighbors == 3:
                            new_grid[i, j] = 1
                grid = new_grid
                img.set_data(grid)
                return img,
            
            # Set up Matplotlib figure
            fig, ax = plt.subplots(figsize=(6, 6))
            img = ax.imshow(grid, cmap="binary")
            ax.set_title(title)
            ax.set_xticks(np.arange(0, GRID_COLS, 5))  # Show ticks every 5 cells
            ax.set_yticks(np.arange(0, GRID_ROWS, 5))
            ax.grid(True, color='gray', linestyle='-', linewidth=0.5)  # Add grid lines
            ax.set_xticklabels([])  # Hide tick labels for cleaner look
            ax.set_yticklabels([])
            
            # Embed in Tkinter
            canvas = FigureCanvasTkAgg(fig, master=sim_tab)
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # Create and start animation
            ani = animation.FuncAnimation(fig, update, frames=ANIMATION_FRAMES, interval=ANIMATION_INTERVAL, repeat=True)
            self.active_animations.append(ani)
            
            # Draw the initial plot
            canvas.draw()
            
        except Exception as e:
            print(f"Error in simulation: {e}")

def main():
    """Main entry point for the application."""
    try:
        root = tk.Tk()
        app = GameOfLifeApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()