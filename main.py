import tkinter as tk
from tkinter import ttk, messagebox
import threading
from PIL import Image, ImageTk
import sys
import os 
import speedtest 

# --- Speedtest-cli Check ---
try:
    import speedtest
except ImportError:
    print("ERROR: speedtest-cli module not found!")
    print("Please install it using: pip install speedtest-cli")
    sys.exit(1)

# --- Define the SpeedTestApp Class ---

class SpeedTestApp:
    def __init__(self, root):
        self.root = root
        self.is_testing = False
        
        # Initialize image attributes
        self.pil_image = None
        self.tk_image = None
        
        # Initialize other attribute references
        self.download_label = None
        self.upload_label = None
        self.ping_label = None
        self.download_progress = None
        self.upload_progress = None
        self.ping_progress = None
        self.status_label = None
        self.test_button = None
        self.loader_canvas = None
        self.loader_arc = None
        self.background_label = None 
        
        # Animation variables
        self.loader_angle = 0
        self.animation_id = None
        
        # Define NEW dimensions
        self.APP_WIDTH = 1200
        self.APP_HEIGHT = 650
        self.IMAGE_WIDTH = 400 # 2x the original image width
        self.APP_INTERFACE_WIDTH = self.APP_WIDTH - self.IMAGE_WIDTH # 800 pixels for widgets
        
        # Setup must run first to create the window context
        self.setup_window()
        
        # Load image AFTER the root window has been created
        # We will resize the image to 400x650 for the right panel
        self.load_background_image("src/images/test2.png", width=self.IMAGE_WIDTH, height=self.APP_HEIGHT)
        
        self.create_widgets()
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title("Internet Speed Checker")
        self.root.config(bg="#1a1a1a") 
        self.root.geometry(f"{self.APP_WIDTH}x{self.APP_HEIGHT}")
        self.root.resizable(False, False)
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.APP_WIDTH // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.APP_HEIGHT // 2)
        self.root.geometry(f'{self.APP_WIDTH}x{self.APP_HEIGHT}+{x}+{y}')

    def load_background_image(self, path, width, height):
        """Loads and sets the image on the right side of the app."""
        try:
            if not os.path.exists(path):
                print(f"Error: Background image not found at '{path}'. Skipping background image.")
                return

            # Open image and resize it to the new specified dimensions (400x650)
            self.pil_image = Image.open(path).resize((width, height), Image.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(self.pil_image)
            
            self.background_label = tk.Label(self.root, image=self.tk_image)
            
            # KEY CHANGE: Place image on the right edge
            # x=800 (1200 - 400) places the top-left corner at x=800
            self.background_label.place(x=self.APP_INTERFACE_WIDTH, y=0, width=self.IMAGE_WIDTH, height=self.APP_HEIGHT)
            
        except Exception as e:
            print(f"Error loading background image: {e}")
            self.background_label = None 

    def create_widgets(self):
        """Create and layout all UI components in the LEFT 800px area."""
        
        # Calculate the center X position of the 800px interface area
        CENTER_X = self.APP_INTERFACE_WIDTH // 2
        
        # --- Title ---
        title = tk.Label(
            self.root,
            text="Internet Speed Checker",
            font=("Segoe UI", 32, "bold"), # Increased font size for wider window
            bg="#1a1a1a", 
            fg="#ffffff"
        )
        # PLACEMENT: Centered at X=400 (800 / 2)
        title.place(x=CENTER_X, rely=0.04, anchor="center") 
        
        # --- Status label ---
        self.status_label = tk.Label(
            self.root,
            text="Click 'Test Speed' to begin",
            font=("Segoe UI", 12),
            bg="#1a1a1a",
            fg="#a0a0a0"
        )
        # PLACEMENT: Centered at X=400
        self.status_label.place(x=CENTER_X, rely=0.11, anchor="center")
        
        # --- Loader canvas (hidden by default) ---
        self.loader_canvas = tk.Canvas(
            self.root,
            width=80, # Increased size
            height=80,
            bg="#1a1a1a", 
            highlightthickness=0
        )
        self.loader_arc = self.loader_canvas.create_arc(
            10, 10, 70, 70, # Adjusted arc dimensions
            start=0,
            extent=120,
            outline="#03a9f4",
            width=6, # Increased width
            style=tk.ARC
        )
        
        # --- Main container (Frame placed in the left 800px area) ---
        main_frame = tk.Frame(self.root, bg="#1a1a1a", relief=tk.FLAT, bd=0)
        # Width set to 700 to fill most of the 800px area
        main_frame.place(x=CENTER_X, rely=0.5, anchor="center", width=700) 

        
        # --- Speed Sections (Download, Upload, Ping) ---
        self.create_speed_section(
            main_frame, 
            "Download Speed",
            "download_label",
            "download_progress",
            "#4CAF50"
        )
        
        self.create_speed_section(
            main_frame,
            "Upload Speed",
            "upload_label",
            "upload_progress",
            "#2196F3"
        )
        
        self.create_speed_section(
            main_frame,
            "Ping",
            "ping_label",
            "ping_progress",
            "#FF9800"
        )
        
        # --- Test button ---
        self.test_button = tk.Button(
            self.root,
            text="🚀 Test Speed",
            font=("Segoe UI", 18, "bold"), # Increased font size
            bg="#03a9f4",
            fg="#ffffff",
            activebackground="#0288d1",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            width=30, # Increased width
            height=2,
            command=self.start_speed_test,
            borderwidth=0,
            highlightthickness=0
        )
        # PLACEMENT: Centered at the bottom of the left 800px area (X=400)
        self.test_button.place(x=CENTER_X, rely=0.9, anchor="center") 

    def create_speed_section(self, parent, title, label_attr, progress_attr, color):
        """Create a section for displaying speed metrics"""
        frame = tk.Frame(parent, bg="#2a2a2a", relief=tk.FLAT, bd=0)
        frame.pack(fill=tk.X, pady=10) # Increased padding
        
        # Section title
        title_label = tk.Label(
            frame,
            text=title,
            font=("Segoe UI", 14, "bold"), # Increased font size
            bg="#2a2a2a",
            fg="#ffffff",
            anchor="w"
        )
        title_label.pack(fill=tk.X, padx=20, pady=(15, 5)) # Increased padding
        
        # Value label
        value_label = tk.Label(
            frame,
            text="-- --",
            font=("Segoe UI", 18), # Increased font size
            bg="#2a2a2a",
            fg="#ffffff",
            anchor="w"
        )
        value_label.pack(fill=tk.X, padx=20, pady=(0, 10)) # Increased padding
        setattr(self, label_attr, value_label)
        
        # Progress bar with custom style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            f"{progress_attr}.Horizontal.TProgressbar",
            troughcolor='#3a3a3a',
            background=color,
            borderwidth=0,
            thickness=10 # Increased thickness
        )
        
        progress = ttk.Progressbar(
            frame,
            style=f"{progress_attr}.Horizontal.TProgressbar",
            orient=tk.HORIZONTAL,
            length=650, # Adjusted length to fit new frame width
            mode='determinate',
            maximum=100
        )
        progress.pack(padx=20, pady=(0, 15)) # Increased padding
        setattr(self, progress_attr, progress)
        
    # --- Animation and Test Logic (Adjusted placements only) ---
    def animate_loader(self):
        """Animate the spinning loader"""
        if not self.is_testing:
            return
            
        self.loader_angle = (self.loader_angle + 10) % 360
        self.loader_canvas.itemconfig(
            self.loader_arc,
            start=self.loader_angle
        )
        self.animation_id = self.root.after(30, self.animate_loader)
    
    def show_loader(self):
        """Show and start the loader animation"""
        # Place loader in the middle of the left panel (x=400)
        CENTER_X = self.APP_INTERFACE_WIDTH // 2
        self.loader_canvas.place(x=CENTER_X, rely=0.20, anchor="center") 
        self.animate_loader()
    
    def hide_loader(self):
        """Hide and stop the loader animation"""
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        self.loader_canvas.place_forget()
        self.loader_angle = 0
    
    def animate_progress(self, progress_bar, target_value):
        """Smoothly animate progress bar to target value"""
        current = progress_bar['value']
        step = (target_value - current) / 20
        
        def update():
            nonlocal current
            if abs(current - target_value) < abs(step):
                progress_bar['value'] = target_value
                return
            current += step
            progress_bar['value'] = current
            self.root.after(30, update)
            
        update()
        
    def start_speed_test(self):
        """Start speed test in a separate thread"""
        if self.is_testing:
            return
            
        self.is_testing = True
        self.test_button.config(state=tk.DISABLED, text="Testing...")
        self.status_label.config(text="Initializing speed test...", fg="#03a9f4")
        
        # Show loader animation
        self.show_loader()
        
        # Reset displays
        self.download_label.config(text="-- --")
        self.upload_label.config(text="-- --")
        self.ping_label.config(text="-- --")
        self.download_progress['value'] = 0
        self.upload_progress['value'] = 0
        self.ping_progress['value'] = 0
        
        # Run test in background thread
        thread = threading.Thread(target=self.run_speed_test, daemon=True)
        thread.start()
        
    def run_speed_test(self):
        """Perform the actual speed test"""
        try:
            st = speedtest.Speedtest()
            
            # Get best server
            self.root.after(0, lambda: self.status_label.config(
                text="Finding best server..."
            ))
            st.get_best_server()
            
            # Test download
            self.root.after(0, lambda: self.status_label.config(
                text="Testing download speed..."
            ))
            download_speed = st.download() / 1_000_000
            
            # Test upload
            self.root.after(0, lambda: self.status_label.config(
                text="Testing upload speed..."
            ))
            upload_speed = st.upload() / 1_000_000
            
            # Get ping
            ping = st.results.ping
            
            # Update UI on main thread
            self.root.after(0, lambda: self.update_results(
                download_speed, upload_speed, ping
            ))
            
        except Exception as e:
            
            self.root.after(0, lambda err=e: self.handle_error(str(err)))
            
    def update_results(self, download, upload, ping):
        """Update UI with test results"""
        # Update labels
        self.download_label.config(text=f"{download:.2f} Mbps")
        self.upload_label.config(text=f"{upload:.2f} Mbps")
        self.ping_label.config(text=f"{ping:.2f} ms")
        
        # Animate progress bars (scale for visual effect)
        self.animate_progress(self.download_progress, min(download * 0.8, 100))
        self.animate_progress(self.upload_progress, min(upload * 1.2, 100))
        self.animate_progress(self.ping_progress, min(100 - (ping * 0.5), 100))
        
        # Update status
        self.status_label.config(text="Test completed successfully", fg="#4CAF50")
        self.test_button.config(state=tk.NORMAL, text="🚀 Test Speed")
        self.is_testing = False
        self.hide_loader() 
        
    def handle_error(self, error_msg):
        """Handle errors during speed test"""
        self.hide_loader() 
        self.status_label.config(
            text="Test failed - Check your connection",
            fg="#f44336"
        )
        self.test_button.config(state=tk.NORMAL, text="🚀 Test Speed")
        self.is_testing = False
        messagebox.showerror(
            "Speed Test Error",
            f"An error occurred:\n{error_msg}\n\nPlease check your internet connection."
        )

# --- Main Execution Block  ---

def main():
    root = tk.Tk() 
    app = SpeedTestApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()