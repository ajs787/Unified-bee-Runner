##Edited 6/9/2022 Rich Howard
##Commented out lines with double #
sleep 15

sudo umount /dev/sda1
#sudo umount /dev/sda
sudo mkdir /mnt/usb
sudo mount -t auto /dev/sda1 /mnt/usb
#sudo mount -t auto /dev/sda /mnt/usb
cd /home/pi
#sudo date '+%Y%m%d' -s '20220714'
sudo python3 cam.helmholtz.py &
#remove comment above for continuous image display
sudo python3 Helmholtz_Drive.py
wait
