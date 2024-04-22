# clone .env
sed 's/=.*/=/' .env > .env.example
# remove comments
sed -i 's:#.*$::g' .env.example