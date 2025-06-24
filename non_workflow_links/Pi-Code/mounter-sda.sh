sudo umount /dev/sda1
#sudo umount /dev/sda
sudo mkdir /mnt/usb
sudo mount -t auto /dev/sda1 /mnt/usb
#sudo mount -t auto /dev/sda /mnt/usb
cd /home/pi
#parallel ::: "sudo python3 cam.py" "sudo python pin10sec.py"
sudo python3 cam.py &
sudo python pin.py &
wait
