run:
	sudo scapy < parsehttp.py

run2:
	sudo scapy < multihttp.py

host:
	sudo php -S 0.0.0.0:5000 -t result/ylb.jp

clean:
	sudo rm -rf result
	mkdir result