if [ -d "Manuscripts" ]; then
	cd Manuscripts
	git pull
	cd ..
else
	git clone https://github.com/Handrit/Manuscripts.git
fi
