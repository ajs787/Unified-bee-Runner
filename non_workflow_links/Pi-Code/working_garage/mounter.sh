sudo umount /dev/sda
#sudo umount /dev/sda
sudo mkdir -f /mnt/usb
sudo mount -t auto /dev/sda1 /mnt/usb
#sudo mount -t auto /dev/sda /mnt/usb
cd /home/pi
#parallel ::: "sudo python3 cam.py" "sudo python pin10sec.py"
sudo python3 cam.py &
sudo python helmholtz.py &
wait
