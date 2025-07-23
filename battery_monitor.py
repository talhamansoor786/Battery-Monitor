import psutil
import time
import winsound
import threading
import sys
import os
import winreg
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import tkinter as tk
from tkinter import messagebox, filedialog
import json

class BatteryMonitor:
    def __init__(self):
        # Configuration file path
        self.config_file = os.path.join(os.path.dirname(__file__), 'battery_config.json')
        
        # Load configuration
        self.load_config()
        
        # Control flags
        self.running = True
        self.monitoring = True
        
        # Create system tray icon
        self.create_tray_icon()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_battery, daemon=True)
        self.monitor_thread.start()
    
    def load_config(self):
        """Load configuration from JSON file"""
        default_config = {
            'alarm_sound': 'D:\\Battery Alarm\\siren-alert.wav',
            'low_threshold': 20,
            'high_threshold': 90,
            'check_interval': 60,
            'auto_startup': False
        }
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
        except FileNotFoundError:
            config = default_config
            self.save_config(config)
        
        self.alarm_sound = config['alarm_sound']
        self.low_threshold = config['low_threshold']
        self.high_threshold = config['high_threshold']
        self.check_interval = config['check_interval']
        self.auto_startup = config['auto_startup']
    
    def save_config(self, config=None):
        """Save configuration to JSON file"""
        if config is None:
            config = {
                'alarm_sound': self.alarm_sound,
                'low_threshold': self.low_threshold,
                'high_threshold': self.high_threshold,
                'check_interval': self.check_interval,
                'auto_startup': self.auto_startup
            }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
    
    def create_battery_icon(self, percent, plugged=False):
        """Create a battery icon for the system tray"""
        # Create a 64x64 image
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Battery outline
        draw.rectangle([10, 20, 50, 45], outline='black', width=2)
        # Battery tip
        draw.rectangle([50, 28, 54, 37], fill='black')
        
        # Battery fill based on percentage
        fill_width = int((percent / 100) * 36)
        if percent > 50:
            color = 'green'
        elif percent > 20:
            color = 'orange'
        else:
            color = 'red'
        
        if fill_width > 0:
            draw.rectangle([12, 22, 12 + fill_width, 43], fill=color)
        
        # Charging indicator
        if plugged:
            draw.text((15, 48), "⚡", fill='blue')
        
        # Battery percentage
        draw.text((5, 5), f"{percent}%", fill='black')
        
        return image
    
    def create_tray_icon(self):
        """Create system tray icon with menu"""
        # Get initial battery status
        battery = psutil.sensors_battery()
        icon_image = self.create_battery_icon(battery.percent, battery.power_plugged)
        
        # Create menu
        menu = Menu(
            MenuItem("Battery Monitor", self.show_status, default=True),
            MenuItem("Settings", self.show_settings),
            MenuItem("Pause/Resume", self.toggle_monitoring),
            MenuItem("Auto Startup", self.toggle_auto_startup, checked=lambda item: self.auto_startup),
            MenuItem("Exit", self.quit_application)
        )
        
        self.icon = Icon("BatteryMonitor", icon_image, "Battery Monitor", menu)
    
    def update_tray_icon(self, percent, plugged):
        """Update the tray icon with current battery status"""
        if hasattr(self, 'icon') and self.icon:
            new_icon = self.create_battery_icon(percent, plugged)
            self.icon.icon = new_icon
            tooltip = f"Battery: {percent}%"
            if plugged:
                tooltip += " (Charging)"
            self.icon.title = tooltip
    
    def play_alert(self):
        """Play alert sound"""
        try:
            if self.alarm_sound and os.path.exists(self.alarm_sound):
                winsound.PlaySound(self.alarm_sound, winsound.SND_FILENAME | winsound.SND_ASYNC)
            else:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception as e:
            print(f"Error playing sound: {e}")
    
    def monitor_battery(self):
        """Main monitoring loop"""
        last_low_alert = 0
        last_high_alert = 0
        
        while self.running:
            if self.monitoring:
                try:
                    battery = psutil.sensors_battery()
                    if battery is None:
                        time.sleep(self.check_interval)
                        continue
                    
                    percent = battery.percent
                    plugged = battery.power_plugged
                    current_time = time.time()
                    
                    # Update tray icon
                    self.update_tray_icon(percent, plugged)
                    
                    # Check for low battery
                    if (percent <= self.low_threshold and not plugged and 
                        current_time - last_low_alert > 300):  # 5 minutes cooldown
                        print(f"Battery Low: {percent}%")
                        self.play_alert()
                        last_low_alert = current_time
                    
                    # Check for high battery
                    elif (percent >= self.high_threshold and plugged and 
                          current_time - last_high_alert > 300):  # 5 minutes cooldown
                        print(f"Battery High: {percent}%")
                        self.play_alert()
                        last_high_alert = current_time
                
                except Exception as e:
                    print(f"Error monitoring battery: {e}")
            
            time.sleep(self.check_interval)
    
    def show_status(self, icon=None, item=None):
        """Show current battery status"""
        try:
            battery = psutil.sensors_battery()
            percent = battery.percent
            plugged = "Yes" if battery.power_plugged else "No"
            
            status = f"Battery Level: {percent}%\nCharging: {plugged}\nMonitoring: {'On' if self.monitoring else 'Off'}"
            
            # Create a simple status window
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showinfo("Battery Status", status)
            root.destroy()
        except Exception as e:
            print(f"Error showing status: {e}")
    
    def show_settings(self, icon=None, item=None):
        """Show settings dialog"""
        root = tk.Tk()
        root.title("Battery Monitor Settings")
        root.geometry("450x400")
        root.resizable(False, False)
        
        # Variables
        low_var = tk.IntVar(value=self.low_threshold)
        high_var = tk.IntVar(value=self.high_threshold)
        interval_var = tk.IntVar(value=self.check_interval)
        sound_var = tk.StringVar(value=self.alarm_sound)
        
        # GUI elements with better spacing
        tk.Label(root, text="Low Battery Threshold (%):", font=('Arial', 10)).pack(pady=(10, 5))
        tk.Scale(root, from_=5, to=50, orient=tk.HORIZONTAL, variable=low_var, length=350).pack(pady=(0, 10))
        
        tk.Label(root, text="High Battery Threshold (%):", font=('Arial', 10)).pack(pady=(10, 5))
        tk.Scale(root, from_=50, to=100, orient=tk.HORIZONTAL, variable=high_var, length=350).pack(pady=(0, 10))
        
        tk.Label(root, text="Check Interval (seconds):", font=('Arial', 10)).pack(pady=(10, 5))
        tk.Scale(root, from_=10, to=300, orient=tk.HORIZONTAL, variable=interval_var, length=350).pack(pady=(0, 15))
        
        tk.Label(root, text="Alarm Sound File:", font=('Arial', 10)).pack(pady=(10, 5))
        sound_frame = tk.Frame(root)
        sound_frame.pack(pady=(0, 20), padx=20, fill=tk.X)
        
        sound_entry = tk.Entry(sound_frame, textvariable=sound_var, width=35, font=('Arial', 9))
        sound_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(sound_frame, text="Browse", 
                              command=lambda: self.browse_sound_file(sound_var),
                              width=10, height=1)
        browse_btn.pack(side=tk.RIGHT)
        
        # Buttons with better spacing
        button_frame = tk.Frame(root)
        button_frame.pack(pady=30)
        
        def save_settings():
            self.low_threshold = low_var.get()
            self.high_threshold = high_var.get()
            self.check_interval = interval_var.get()
            self.alarm_sound = sound_var.get()
            self.save_config()
            root.destroy()
        
        save_btn = tk.Button(button_frame, text="Save", command=save_settings, 
                            width=12, height=2, font=('Arial', 10))
        save_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=root.destroy, 
                              width=12, height=2, font=('Arial', 10))
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        root.mainloop()
    
    def browse_sound_file(self, sound_var):
        """Browse for sound file"""
        filename = filedialog.askopenfilename(
            title="Select Sound File",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        if filename:
            sound_var.set(filename)
    
    def toggle_monitoring(self, icon=None, item=None):
        """Toggle monitoring on/off"""
        self.monitoring = not self.monitoring
        status = "resumed" if self.monitoring else "paused"
        print(f"Monitoring {status}")
    
    def toggle_auto_startup(self, icon=None, item=None):
        """Toggle auto startup"""
        self.auto_startup = not self.auto_startup
        self.save_config()
        
        if self.auto_startup:
            self.add_to_startup()
        else:
            self.remove_from_startup()
    
    def add_to_startup(self):
        """Add application to Windows startup"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "BatteryMonitor"
            app_path = sys.executable if getattr(sys, 'frozen', False) else __file__
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
            
            print("Added to startup")
        except Exception as e:
            print(f"Error adding to startup: {e}")
    
    def remove_from_startup(self):
        """Remove application from Windows startup"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "BatteryMonitor"
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.DeleteValue(key, app_name)
            
            print("Removed from startup")
        except FileNotFoundError:
            pass  # Already not in startup
        except Exception as e:
            print(f"Error removing from startup: {e}")
    
    def quit_application(self, icon=None, item=None):
        """Quit the application"""
        self.running = False
        if hasattr(self, 'icon'):
            self.icon.stop()
        sys.exit(0)
    
    def run(self):
        """Run the application"""
        try:
            self.icon.run()
        except KeyboardInterrupt:
            self.quit_application()

if __name__ == "__main__":
    app = BatteryMonitor()
    app.run()