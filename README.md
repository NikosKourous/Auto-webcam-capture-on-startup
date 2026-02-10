# Auto-webcam-capture-on-startup
A light-weight program that captures a series of images from my laptop webcam upon startup. Used to gather a dataset of my face using my laptop.
+++ Setup webcam_startup_snapshots.py to run at login

+ install prerequisites

sudo apt update
sudo apt install -y fswebcam

+ place the script

mkdir -p ~/.local/bin
nano ~/.local/bin/webcam_startup_snapshots.py
chmod +x ~/.local/bin/webcam_startup_snapshots.py

+ test manually

~/.local/bin/webcam_startup_snapshots.py

+++ Create a systemd user service

+ write the service file

mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/webcam-startup.service <<'EOF'
[Unit]
Description=Webcam snapshots at login (user service)
After=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/bin/env python3 %h/.local/bin/webcam_startup_snapshots.py
Nice=10
IOSchedulingClass=idle
Restart=no

[Install]
WantedBy=default.target
EOF

+++ Enable and start

+ reload and enable

systemctl --user daemon-reload
systemctl --user enable webcam-startup.service
systemctl --user start webcam-startup.service

+++ Verify

+ check status

systemctl --user status webcam-startup.service

+ view logs

journalctl --user -u webcam-startup.service -e --no-pager

+ confirm files

ls -lt ~/Pictures/Webcam-Pics-Startup///* | head
